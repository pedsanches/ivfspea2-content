MAIN_FILE = main.tex
MAIN_STEM = $(basename $(MAIN_FILE))
OUTPUT_DIR = build
MAIN_PDF = $(OUTPUT_DIR)/$(MAIN_STEM).pdf

LATEXMK = latexmk
LATEXMK_FLAGS = -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=$(OUTPUT_DIR)

.PHONY: all clean view install-deps

all: $(MAIN_PDF)

$(MAIN_PDF): $(MAIN_FILE) references.bib llncs.cls splncs04.bst
	@mkdir -p $(OUTPUT_DIR)
	$(LATEXMK) $(LATEXMK_FLAGS) $(MAIN_FILE)

clean:
	rm -rf $(OUTPUT_DIR)
	rm -f $(MAIN_STEM).aux $(MAIN_STEM).bbl $(MAIN_STEM).blg $(MAIN_STEM).fdb_latexmk $(MAIN_STEM).fls $(MAIN_STEM).log $(MAIN_STEM).out $(MAIN_STEM).pdf
	rm -f indent.log $(MAIN_STEM).bak*

view: all
	xdg-open $(MAIN_PDF)

install-deps:
	@echo "Please run: sudo apt-get update && sudo apt-get install texlive-full latexmk"
