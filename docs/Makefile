# Minimal Sphinx Makefile.
# Usage:
#   make html          — full build (runs gen_* scripts via conf.py setup hook)
#   make html PLOT=1   — same but with plot_gallery=True (needs project_bundle/ dirs)
#   make clean         — remove _build/ and auto_papers/

SPHINXOPTS  ?=
SPHINXBUILD ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

.PHONY: help html clean

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo "Build finished: $(BUILDDIR)/html/index.html"
