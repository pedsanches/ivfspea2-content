# Makefile for the Springer Nature / Memetic Computing manuscript

MAIN_FILE = sn-article.tex
MAIN_STEM = $(basename $(MAIN_FILE))
SRC_DIR = src
OUTPUT_DIR = build
MAIN_PDF = $(OUTPUT_DIR)/$(MAIN_STEM).pdf

# latexmk runs with -cd (from SRC_DIR), so its outdir is one level up.
LATEXMK_FLAGS = -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=../$(OUTPUT_DIR) -cd

# The class, styles and figures live outside SRC_DIR. latexmk finds them through
# the TEXINPUTS family below; Tectonic through TEX_SEARCH_PATHS.
TEX_SEARCH_PATHS = cls figures bib bib/bst

# Environment variables for LaTeX to findcls/bst/images
CURDIR=$(shell pwd)
export TEXINPUTS=$(CURDIR)/cls:$(CURDIR)/figures:
export BIBINPUTS=$(CURDIR)/bib:$(CURDIR)/bib/bst:
export BSTINPUTS=$(CURDIR)/bib:$(CURDIR)/bib/bst:

include ../latex.mk

.PHONY: all clean view install-deps

all: $(MAIN_PDF)

$(MAIN_PDF): $(SRC_DIR)/$(MAIN_FILE)
	@mkdir -p $(OUTPUT_DIR)
	$(call LATEX_BUILD,$(SRC_DIR)/$(MAIN_FILE))

clean:
	rm -rf $(OUTPUT_DIR)
	rm -rf build_submission
	rm -rf $(SRC_DIR)/build
	rm -f $(SRC_DIR)/$(MAIN_STEM).aux $(SRC_DIR)/$(MAIN_STEM).bbl $(SRC_DIR)/$(MAIN_STEM).blg $(SRC_DIR)/$(MAIN_STEM).brf $(SRC_DIR)/$(MAIN_STEM).fdb_latexmk $(SRC_DIR)/$(MAIN_STEM).fls $(SRC_DIR)/$(MAIN_STEM).log $(SRC_DIR)/$(MAIN_STEM).out $(SRC_DIR)/$(MAIN_STEM).synctex.gz $(SRC_DIR)/$(MAIN_STEM).toc
	rm -f $(SRC_DIR)/indent.log

view: all
	$(OPEN) $(MAIN_PDF)

install-deps:
	@printf '%s\n' \
		"Install either engine:" \
		"  brew install tectonic          (no system TeX needed)" \
		"  apt-get install texlive-full latexmk"
