# ============================================
# IVF-SPEA2 Project Makefile
# ============================================

SHELL := /bin/bash

PYTHON     := python3
PIP        := pip3
PYTEST     := python3 -m pytest
MATLAB     := matlab -batch
VENV_DIR   := .venv
ACTIVATE   := source $(VENV_DIR)/bin/activate

.PHONY: help setup test test-matlab test-python analysis analysis-benchmark-figures \
        analysis-convergence analysis-convergence-build analysis-convergence-summaries \
        analysis-convergence-tests analysis-convergence-plots \
        paper paper-ppsn paper-all paper-clean clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ---- Setup ----

setup: ## Install Python dependencies in virtual environment
	$(PYTHON) -m venv $(VENV_DIR)
	$(ACTIVATE) && $(PIP) install -r requirements.txt
	@echo "\n✅ Setup complete. Activate with: source .venv/bin/activate"

# ---- Testing ----

test: test-python ## Run all available tests

test-matlab: ## Run MATLAB unit tests
	$(MATLAB) "run('tests/matlab/run_tests.m')"

test-python: ## Run Python tests with pytest
	$(ACTIVATE) && $(PYTEST) tests/python/ -v

# ---- Analysis ----

analysis: ## Generate analysis plots from processed data
	$(ACTIVATE) && $(PYTHON) src/python/analysis/script.py

analysis-benchmark-figures: ## Generate 5 benchmark figures (IGD/HV)
	$(ACTIVATE) && $(PYTHON) src/python/analysis/generate_ivf_benchmark_five_figures.py

# ---- Convergence-rigor pipeline (PLAN_CONVERGENCE_RIGOR.md) ----
# Dependency chain:
#   build (.mat -> hosts_convergence.csv)
#     -> summaries (per-run metrics, merge diagnostic, alt-instance selection)
#     -> tests (bootstrap CI, paired Wilcoxon+BH, KS ECDF)
#     -> plots (sensitivity, HV ratio, v2 IGD/ECDF)

ANALYSIS_DIR := src/python/analysis
CONV_CSV     := data/processed/hosts_convergence.csv

analysis-convergence-build: ## Extract IGD+HV traces from PlatEMO .mat files
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/build_hosts_convergence_csv.py

analysis-convergence-summaries: analysis-convergence-build ## Per-run AUC/time-to-target + merge diag + alt selection
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/compute_convergence_summaries.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/diagnose_merge.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/select_convergence_sensitivity.py

analysis-convergence-tests: analysis-convergence-summaries ## Bootstrap CIs, paired Wilcoxon+BH, KS ECDF
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/bootstrap_ci.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/test_convergence_significance.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/test_ecdf_difference.py

analysis-convergence-plots: analysis-convergence-tests ## Sensitivity, HV ratio, v2 IGD+ECDF plots
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/sensitivity_smoothing.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/plot_hosts_convergence_hv.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/plot_hosts_convergence_v2.py

analysis-convergence: analysis-convergence-plots ## Full convergence-rigor pipeline end-to-end

# ---- Paper ----

paper: ## Compile the Springer Nature paper
	$(MAKE) -C paper springer-nature

paper-ppsn: ## Compile the PPSN paper
	$(MAKE) -C paper ppsn2026

paper-all: ## Compile both papers
	$(MAKE) -C paper papers

paper-clean: ## Clean LaTeX build artifacts
	$(MAKE) -C paper clean

# ---- Cleanup ----

clean: paper-clean ## Clean all generated artifacts
	rm -rf results/figures/plots_igd
	rm -rf results/metrics/*.csv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned."

distclean: clean ## Deep clean (includes venv)
	rm -rf $(VENV_DIR)
	@echo "✅ Deep cleaned (venv removed)."
