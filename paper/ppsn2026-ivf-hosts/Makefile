MAIN_FILE = main.tex
MAIN_STEM = $(basename $(MAIN_FILE))
OUTPUT_DIR = build
MAIN_PDF = $(OUTPUT_DIR)/$(MAIN_STEM).pdf
PROJECT_ROOT = ../..
ANALYSIS_DIR = $(PROJECT_ROOT)/src/python/analysis
PYTHON ?= $(PROJECT_ROOT)/.venv/bin/python

# Only genuine upstream inputs belong here. data/processed/hosts_paper.csv, the
# figures and everything under results/tables/ are written *by* the assets
# recipe, so listing any of them would leave the stamp permanently out of date.
ASSET_SCRIPTS = $(ANALYSIS_DIR)/figure_io.py \
                $(ANALYSIS_DIR)/build_hosts_paper_csv.py \
                $(ANALYSIS_DIR)/compute_hosts_tables.py \
                $(ANALYSIS_DIR)/build_hosts_rep_endpoint_table.py \
                $(ANALYSIS_DIR)/compute_hosts_geometry_stratified.py \
                $(ANALYSIS_DIR)/plot_hosts_results.py \
                $(ANALYSIS_DIR)/select_convergence_instances.py \
                $(ANALYSIS_DIR)/plot_hosts_figures_v2.py
ASSET_INPUTS = $(PROJECT_ROOT)/data/processed/todas_metricas_consolidado.csv \
               $(PROJECT_ROOT)/data/processed/nsga_experiments.csv \
               $(PROJECT_ROOT)/config/hosts_front_geometry.csv
ASSET_STAMP = $(OUTPUT_DIR)/.assets.stamp

include ../latex.mk

.PHONY: all assets clean clean-assets view install-deps

all: $(MAIN_PDF)

$(MAIN_PDF): $(MAIN_FILE) references.bib llncs.cls splncs04.bst | assets
	@mkdir -p $(OUTPUT_DIR)
	$(call LATEX_BUILD,$(MAIN_FILE))

assets: $(ASSET_STAMP)

$(ASSET_STAMP): $(ASSET_SCRIPTS) $(ASSET_INPUTS)
	@mkdir -p $(OUTPUT_DIR)
	$(PYTHON) $(ANALYSIS_DIR)/build_hosts_paper_csv.py
	$(PYTHON) $(ANALYSIS_DIR)/compute_hosts_tables.py
	$(PYTHON) $(ANALYSIS_DIR)/build_hosts_rep_endpoint_table.py
	$(PYTHON) $(ANALYSIS_DIR)/compute_hosts_geometry_stratified.py
	$(PYTHON) $(ANALYSIS_DIR)/plot_hosts_results.py
	$(PYTHON) $(ANALYSIS_DIR)/select_convergence_instances.py
	$(PYTHON) $(ANALYSIS_DIR)/plot_hosts_figures_v2.py
	@if [ -f $(PROJECT_ROOT)/src/matlab/lib/PlatEMO/Data/IVFSPEA2V2/IVFSPEA2V2_DTLZ5_M2_D11_7001.mat ]; then \
		$(MAKE) -C $(PROJECT_ROOT) analysis-convergence; \
	else \
		printf '%s\n' 'Skipping convergence assets: run experiments/run_hosts_convergence.m first.'; \
	fi
	@touch $@

# Removes only build output. The figures and tables under figures/,
# results/tables/ and data/processed/ are versioned deliverables, so wiping them
# here would delete committed content; use clean-assets for that on purpose.
clean:
	rm -rf $(OUTPUT_DIR)
	rm -f $(MAIN_STEM).aux $(MAIN_STEM).bbl $(MAIN_STEM).blg \
	       $(MAIN_STEM).fdb_latexmk $(MAIN_STEM).fls \
	       $(MAIN_STEM).log $(MAIN_STEM).out $(MAIN_STEM).pdf
	rm -f indent.log $(MAIN_STEM).bak*

# Deletes the generated assets so `make assets` rebuilds them from scratch.
# These paths are tracked in git: expect a dirty working tree afterwards.
# hosts_a12_summary.tex is deliberately spared -- it is hand-maintained and no
# generator would bring it back.
clean-assets:
	rm -f $(ASSET_STAMP)
	rm -f figures/hosts_fig1_wintieloss.pdf figures/hosts_fig2_scatter.pdf \
	       figures/hosts_fig3_family.pdf figures/hosts_fig4_cross_host_ivf.pdf \
	       figures/hosts_v2_fig1_a12_strip.pdf figures/hosts_v2_fig2_heatmap.pdf \
	       figures/hosts_v2_fig3_m2_vs_m3.pdf figures/hosts_v2_fig4_convergence.pdf \
	       figures/hosts_v2_fig5_ecdf.pdf
	rm -f $(PROJECT_ROOT)/results/figures/hosts_fig1_wintieloss.pdf \
	       $(PROJECT_ROOT)/results/figures/hosts_fig2_scatter.pdf \
	       $(PROJECT_ROOT)/results/figures/hosts_fig3_family.pdf \
	       $(PROJECT_ROOT)/results/figures/hosts_fig4_cross_host_ivf.pdf \
	       $(PROJECT_ROOT)/results/figures/hosts_v2_fig1_a12_strip.pdf \
	       $(PROJECT_ROOT)/results/figures/hosts_v2_fig2_heatmap.pdf \
	       $(PROJECT_ROOT)/results/figures/hosts_v2_fig3_m2_vs_m3.pdf \
	       $(PROJECT_ROOT)/results/figures/hosts_v2_fig4_convergence.pdf \
	       $(PROJECT_ROOT)/results/figures/hosts_v2_fig5_ecdf.pdf
	find $(PROJECT_ROOT)/results/tables \
	       \( -name 'hosts_*.tex' -o -name 'hosts_*.csv' -o -name 'hosts_*.txt' \) \
	       ! -name 'hosts_a12_summary.tex' -delete
	rm -f $(PROJECT_ROOT)/data/processed/hosts_paper.csv \
	       $(PROJECT_ROOT)/data/processed/hosts_convergence.csv

view: all
	$(OPEN) $(MAIN_PDF)

install-deps:
	@printf '%s\n' \
		"Install either engine:" \
		"  brew install tectonic          (no system TeX needed)" \
		"  apt-get install texlive-full latexmk"
