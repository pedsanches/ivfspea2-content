MAIN_FILE = main.tex
MAIN_STEM = $(basename $(MAIN_FILE))
OUTPUT_DIR = build
MAIN_PDF = $(OUTPUT_DIR)/$(MAIN_STEM).pdf
PROJECT_ROOT = ../..
ANALYSIS_DIR = $(PROJECT_ROOT)/src/python/analysis
PYTHON ?= $(PROJECT_ROOT)/.venv/bin/python

LATEXMK = latexmk
LATEXMK_FLAGS = -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=$(OUTPUT_DIR)

.PHONY: all assets clean view install-deps

all: $(MAIN_PDF)

$(MAIN_PDF): $(MAIN_FILE) references.bib llncs.cls splncs04.bst | assets
	@mkdir -p $(OUTPUT_DIR)
	$(LATEXMK) $(LATEXMK_FLAGS) $(MAIN_FILE)

assets:
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

clean:
	rm -rf $(OUTPUT_DIR)
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
	rm -f $(PROJECT_ROOT)/results/tables/hosts_*.tex \
	       $(PROJECT_ROOT)/results/tables/hosts_*.csv \
	       $(PROJECT_ROOT)/results/tables/hosts_*.txt
	rm -f $(PROJECT_ROOT)/data/processed/hosts_paper.csv \
	       $(PROJECT_ROOT)/data/processed/hosts_convergence.csv
	rm -f $(MAIN_STEM).aux $(MAIN_STEM).bbl $(MAIN_STEM).blg \
	       $(MAIN_STEM).fdb_latexmk $(MAIN_STEM).fls \
	       $(MAIN_STEM).log $(MAIN_STEM).out $(MAIN_STEM).pdf
	rm -f indent.log $(MAIN_STEM).bak*

view: all
	xdg-open $(MAIN_PDF)

install-deps:
	@echo "Please run: sudo apt-get update && sudo apt-get install texlive-full latexmk"
