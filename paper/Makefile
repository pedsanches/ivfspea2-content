# Makefile for the single-source IVF/SPEA2 manuscript

MAIN_FILE = sn-article.tex
MAIN_STEM = $(basename $(MAIN_FILE))
SRC_DIR = src
OUTPUT_DIR = build
MAIN_PDF = $(OUTPUT_DIR)/$(MAIN_STEM).pdf

# Tools
LATEXMK = latexmk
LATEXMK_FLAGS = -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=../$(OUTPUT_DIR) -cd

# Environment variables for LaTeX to findcls/bst/images
CURDIR=$(shell pwd)
export TEXINPUTS=$(CURDIR)/cls:$(CURDIR)/figures:
export BIBINPUTS=$(CURDIR)/bib:$(CURDIR)/bib/bst:
export BSTINPUTS=$(CURDIR)/bib:$(CURDIR)/bib/bst:

.PHONY: all clean view install-deps

all: $(MAIN_PDF)

$(MAIN_PDF): $(SRC_DIR)/$(MAIN_FILE)
	@mkdir -p $(OUTPUT_DIR)
	$(LATEXMK) $(LATEXMK_FLAGS) $(SRC_DIR)/$(MAIN_FILE)

clean:
	rm -rf $(OUTPUT_DIR)
	rm -rf build_submission
	rm -f $(SRC_DIR)/$(MAIN_STEM).aux $(SRC_DIR)/$(MAIN_STEM).bbl $(SRC_DIR)/$(MAIN_STEM).blg $(SRC_DIR)/$(MAIN_STEM).brf $(SRC_DIR)/$(MAIN_STEM).fdb_latexmk $(SRC_DIR)/$(MAIN_STEM).fls $(SRC_DIR)/$(MAIN_STEM).log $(SRC_DIR)/$(MAIN_STEM).out $(SRC_DIR)/$(MAIN_STEM).synctex.gz $(SRC_DIR)/$(MAIN_STEM).toc

view: all
	xdg-open $(MAIN_PDF)

install-deps:
	@echo "Please run: sudo apt-get update && sudo apt-get install texlive-full latexmk"
