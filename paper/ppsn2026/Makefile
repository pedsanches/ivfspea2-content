MAIN_FILE = main.tex
MAIN_STEM = $(basename $(MAIN_FILE))
OUTPUT_DIR = build
MAIN_PDF = $(OUTPUT_DIR)/$(MAIN_STEM).pdf

include ../latex.mk

.PHONY: all clean view install-deps

all: $(MAIN_PDF)

$(MAIN_PDF): $(MAIN_FILE) references.bib llncs.cls splncs04.bst
	@mkdir -p $(OUTPUT_DIR)
	$(call LATEX_BUILD,$(MAIN_FILE))

clean:
	rm -rf $(OUTPUT_DIR)
	rm -f $(MAIN_STEM).aux $(MAIN_STEM).bbl $(MAIN_STEM).blg $(MAIN_STEM).fdb_latexmk $(MAIN_STEM).fls $(MAIN_STEM).log $(MAIN_STEM).out $(MAIN_STEM).pdf
	rm -f indent.log $(MAIN_STEM).bak*

view: all
	$(OPEN) $(MAIN_PDF)

install-deps:
	@printf '%s\n' \
		"Install either engine:" \
		"  brew install tectonic          (no system TeX needed)" \
		"  apt-get install texlive-full latexmk"
