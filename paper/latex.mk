# Shared LaTeX engine selection for the manuscripts under paper/.
#
# Include from a manuscript Makefile after defining OUTPUT_DIR, and build with
#     $(call LATEX_BUILD,$(MAIN_FILE))
#
# Engine is auto-detected: latexmk when a system TeX is installed (CI, Overleaf,
# texlive), otherwise Tectonic, which needs no system TeX and pulls packages from
# its own bundle. Force one with ENGINE=latexmk or ENGINE=tectonic.
#
# A manuscript whose .cls/.bst/figures live outside the source directory lists
# those directories in TEX_SEARCH_PATHS before including this file.

LATEXMK  ?= latexmk
TECTONIC ?= tectonic

ifeq ($(ENGINE),)
  ifneq ($(shell command -v $(LATEXMK) 2>/dev/null),)
    ENGINE := latexmk
  else
    ifneq ($(shell command -v $(TECTONIC) 2>/dev/null),)
      ENGINE := tectonic
    else
      ENGINE := none
    endif
  endif
endif

LATEXMK_FLAGS  ?= -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=$(OUTPUT_DIR)
TECTONIC_FLAGS ?= --keep-logs --outdir $(OUTPUT_DIR)

# Tectonic resolves files through its bundle, not TEXINPUTS, so extra source
# directories have to be passed explicitly.
TECTONIC_SEARCH = $(foreach p,$(TEX_SEARCH_PATHS),-Z search-path=$(p))

ifeq ($(ENGINE),latexmk)
  LATEX_BUILD = $(LATEXMK) $(LATEXMK_FLAGS) $(1)
endif
ifeq ($(ENGINE),tectonic)
  LATEX_BUILD = $(TECTONIC) $(TECTONIC_FLAGS) $(TECTONIC_SEARCH) $(1)
endif
ifeq ($(ENGINE),none)
  LATEX_BUILD = @printf '%s\n' \
	'No LaTeX engine found. Install one of:' \
	'  brew install tectonic          (no system TeX needed)' \
	'  brew install --cask mactex     (or: apt-get install texlive-full latexmk)' >&2; \
	exit 1
endif

# Viewer for `make view`.
ifeq ($(shell uname -s),Darwin)
  OPEN ?= open
else
  OPEN ?= xdg-open
endif
