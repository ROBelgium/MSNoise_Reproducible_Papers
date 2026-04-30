# Sphinx Makefile for MSNoise Reproducible Papers docs.
#
# Targets:
#   make html        — static build, notebooks shown as source (no execution)
#   make html-exec   — full build with notebook execution (needs project_bundle/)
#   make clean       — remove _build/ and auto_papers/

SPHINXOPTS  ?=
SPHINXBUILD ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

.PHONY: help html html-exec clean

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo "Build finished: $(BUILDDIR)/html/index.html"

html-exec:
	MRP_EXECUTE_NOTEBOOKS=always \
	$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo "Build finished (with execution): $(BUILDDIR)/html/index.html"

clean:
	rm -rf "$(BUILDDIR)" auto_papers
