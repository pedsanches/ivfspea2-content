MAIN = main
BUILD_DIR = build
LLNCS_DIR = ../Springer_Lecture_Notes_in_Computer_Science

.PHONY: all clean view

all: $(BUILD_DIR)/$(MAIN).pdf

$(BUILD_DIR)/$(MAIN).pdf: $(MAIN).tex references.bib
	@mkdir -p $(BUILD_DIR)
	@cp $(LLNCS_DIR)/llncs.cls $(BUILD_DIR)/ 2>/dev/null || true
	@cp $(LLNCS_DIR)/splncs04.bst $(BUILD_DIR)/ 2>/dev/null || true
	@cp $(MAIN).tex $(BUILD_DIR)/
	@cp references.bib $(BUILD_DIR)/
	cd $(BUILD_DIR) && pdflatex $(MAIN) && bibtex $(MAIN) && pdflatex $(MAIN) && pdflatex $(MAIN)

clean:
	rm -rf $(BUILD_DIR)

view: $(BUILD_DIR)/$(MAIN).pdf
	open $(BUILD_DIR)/$(MAIN).pdf
