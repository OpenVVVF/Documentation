.PHONY: help install test test-bom test-docgen validate site manuals clean check-clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help:
	@echo "OpenVVVF Documentation"
	@echo ""
	@echo "Targets:"
	@echo "  install      create venv and install tools"
	@echo "  test         run all tests"
	@echo "  test-bom     run BOMManager tests"
	@echo "  test-docgen  run docgen tests"
	@echo "  test-hwrelease  run HWRelease tests"
	@echo "  hw-update    export new board revisions from InverterGen5 release tags"
	@echo "  hw-list      list exported board revisions"
	@echo "  hw-viewer    regenerate the PCB assembly viewer page"
	@echo "  validate     validate documentation cross-references and frontmatter"
	@echo "  site         build the static HTML documentation site"
	@echo "  pdfs         build the site and generate per-document PDFs into site/pdfs"
	@echo "  manuals      generate umbrella manual PDFs (e.g. full C2 assembly guide)"
	@echo "  serve        serve the built site locally on port 8000"
	@echo "  clean        remove build artifacts and venv"
	@echo "  check-clean  fail if ignored *.egg-info directories are present"

install:
	python3 -m venv $(VENV)
	$(PIP) install -e Tools/BOMManager -q
	$(PIP) install -e Tools/DocGen -q
	$(PIP) install -e Tools/HWRelease -q

test: test-bom test-docgen test-hwrelease

test-bom:
	$(PYTHON) -m pytest Tools/BOMManager/tests -q

test-docgen:
	$(PYTHON) -m pytest Tools/DocGen/tests -q

test-hwrelease:
	$(PYTHON) -m pytest Tools/HWRelease/tests -q

hw-update:
	$(PYTHON) -m hwrelease.cli update

hw-list:
	$(PYTHON) -m hwrelease.cli list

hw-viewer:
	$(PYTHON) -m hwrelease.cli build-viewer

validate:
	$(PYTHON) -m docgen validate

site:
	$(PYTHON) -m docgen site --output-dir site

pdfs: site
	$(PYTHON) -m docgen pdf --all --output-dir site/pdfs

manuals: site
	$(PYTHON) -m docgen pdf --manual OV-C2-AG-INDEX --output-dir site/pdfs

serve:
	cd site && $(PYTHON) -m http.server 8000

clean:
	rm -rf $(VENV) build dist site .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

check-clean:
	@bad=$$(git status --ignored --short | grep -E '^!! .*\.egg-info/$$' || true); \
	if [ -n "$$bad" ]; then \
		echo "ERROR: ignored *.egg-info directories are present in the working tree:"; \
		echo "$$bad"; \
		exit 1; \
	fi
	@echo "Working tree is clean of ignored *.egg-info directories."
