SHELL := /bin/bash

TECTONIC        ?= tectonic
TECTONIC_BUNDLE ?= https://relay.fullyjustified.net/default_bundle_v33.tar
PYTHON          ?= python3
PDFTOPPM        ?= pdftoppm

MAIN       := main.tex
BUILD_DIR  := build
PDF        := $(BUILD_DIR)/main.pdf
RENDER_DIR := $(BUILD_DIR)/render

SOURCES := $(MAIN) inf-ufg-tectonic.cls inf-ufg.cls abnt-alf.bst inf-ufg.bst \
           tocloft.sty data-sources.toml \
           $(wildcard bib/*.bib) \
           $(wildcard pre/*.tex) \
           $(wildcard tex/*.tex) \
           $(wildcard pos/*.tex) \
           $(wildcard fig/*.pdf)

.PHONY: all bootstrap doctor render clean

all: $(PDF)

$(PDF): $(SOURCES)
	mkdir -p $(BUILD_DIR)
	$(TECTONIC) --only-cached --keep-logs --keep-intermediates \
		--outdir $(BUILD_DIR) $(MAIN)

bootstrap:
	mkdir -p $(BUILD_DIR)
	$(TECTONIC) -b $(TECTONIC_BUNDLE) --keep-logs --keep-intermediates \
		--outdir $(BUILD_DIR) $(MAIN)

doctor:
	@command -v $(TECTONIC) >/dev/null
	@command -v $(PYTHON) >/dev/null
	@command -v $(PDFTOPPM) >/dev/null
	$(PYTHON) scripts/validate_data_sources.py

render: $(PDF)
	mkdir -p $(RENDER_DIR)
	find $(RENDER_DIR) -type f -name 'page-*.png' -delete
	$(PDFTOPPM) -png -r 120 $(PDF) $(RENDER_DIR)/page

clean:
	rm -rf $(BUILD_DIR)
