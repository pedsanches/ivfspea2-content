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

.PHONY: help setup setup-dev test test-matlab test-python analysis analysis-benchmark-figures \
        analysis-convergence analysis-convergence-build analysis-convergence-summaries \
        analysis-convergence-tests analysis-convergence-plots analysis-hosts-audits \
        analysis-nsga analysis-hosts-supplementary \
        verify-release write-checksums \
        paper paper-ppsn paper-hosts paper-clei paper-all paper-clean \
        thesis thesis-bootstrap thesis-doctor thesis-render thesis-clean clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ---- Setup ----

setup: ## Install the locked environment and the ivfspea2 package (editable)
	$(PYTHON) -m venv $(VENV_DIR)
	$(ACTIVATE) && $(PIP) install -r requirements.lock.txt
	$(ACTIVATE) && $(PIP) install -e .
	@echo "\n✅ Setup complete. Activate with: source .venv/bin/activate"

setup-dev: ## Same as setup, plus the linting and test tooling
	$(MAKE) setup
	$(ACTIVATE) && $(PIP) install -e ".[dev]"
	@echo "\n✅ Dev setup complete."

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
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/compute_hosts_dynamic_aggregate.py

analysis-convergence: analysis-convergence-plots ## Full convergence-rigor pipeline end-to-end

# ---- Hosts supporting audits ----
# The accepted PPSN hosts paper promises these tables in its archived artifact
# (main.tex §"Data availability"). The generators existed but were wired to no
# target, so the repository could no longer produce what the paper points at.

# consolidate_nsga_experiments.py is the only producer of
# data/processed/nsga_experiments.csv, which paper/ppsn2026-ivf-hosts declares in
# ASSET_INPUTS. Nothing invoked it, so the paper's input survived only by being
# committed. These three are the NSGA lineage, front to back.
analysis-nsga: ## Consolidate NSGA runs, then its tables and figures
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/consolidate_nsga_experiments.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/compute_nsga_tables.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/plot_nsga_results.py

# plot_hosts_figures_v3.py is the only script in the suite covered by tests that
# exercise real project data, but nothing ran it. Wiring it here means the tests
# guard something reachable.
analysis-hosts-supplementary: ## Supplementary hosts figures (bump chart, stratified W/T/L)
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/plot_hosts_figures_v3.py

analysis-hosts-audits: ## FE-accounting audit, pairing robustness, parameter provenance, dynamic aggregate
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/audit_hosts_fe_accounting.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/compute_hosts_pairing_robustness.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/build_hosts_parameter_provenance.py
	$(ACTIVATE) && $(PYTHON) $(ANALYSIS_DIR)/compute_hosts_dynamic_aggregate.py

# ---- Release integrity ----
# Stdlib + git only, so a fresh clone can verify itself before `make setup`.

verify-release: ## Check every release-manifest row resolves and every checksum matches
	$(PYTHON) scripts/release/verify_release.py

write-checksums: ## Regenerate the release checksum file from the manifest
	$(PYTHON) scripts/release/verify_release.py --write

# ---- Paper ----

paper: ## Compile the Springer Nature paper
	$(MAKE) -C paper springer-nature

paper-ppsn: ## Compile the PPSN dynamics paper
	$(MAKE) -C paper ppsn2026

paper-hosts: ## Compile the PPSN IVF-hosts paper (regenerates its assets)
	$(MAKE) -C paper ppsn-hosts

paper-clei: ## Compile the CLEI paper
	$(MAKE) -C paper clei2026

paper-all: ## Compile all four manuscripts
	$(MAKE) -C paper papers

paper-clean: ## Clean LaTeX build artifacts
	$(MAKE) -C paper clean

# ---- Thesis ----
# thesis/masters/README.md and REVISION_PLAN.md have always documented these
# targets at the root; they simply never existed. Delegating is cheaper than
# correcting both documents, and matches how the paper targets already work.

thesis: ## Compile the master's dissertation (offline; needs thesis-bootstrap once)
	$(MAKE) -C thesis/masters all

thesis-bootstrap: ## First build on a machine: fetch the Tectonic bundle (needs network)
	$(MAKE) -C thesis/masters bootstrap

thesis-doctor: ## Check thesis tooling and validate data-sources.toml
	$(MAKE) -C thesis/masters doctor

thesis-render: ## Rasterize every thesis page for visual QA
	$(MAKE) -C thesis/masters render

thesis-clean: ## Remove thesis build artifacts only
	$(MAKE) -C thesis/masters clean

# ---- Cleanup ----

clean: paper-clean ## Clean all generated artifacts
	rm -rf results/figures/plots_igd
	rm -rf results/metrics/*.csv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned."

distclean: clean ## Deep clean (includes venv)
	rm -rf $(VENV_DIR)
	@echo "✅ Deep cleaned (venv removed)."
