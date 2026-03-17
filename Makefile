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

.PHONY: help setup test test-matlab test-python analysis analysis-benchmark-figures paper clean

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

# ---- Paper ----

paper: ## Compile the LaTeX paper
	$(MAKE) -C paper all

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
