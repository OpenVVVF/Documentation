.PHONY: help install test test-bom test-docgen validate site clean check-clean

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
	@echo "  validate     validate documentation cross-references"
	@echo "  site         build the static HTML documentation site"
	@echo "  clean        remove build artifacts and venv"
	@echo "  check-clean  fail if ignored *.egg-info directories are present"

install:
	python3 -m venv $(VENV)
	$(PIP) install -e Tools/BOMManager -q
	$(PIP) install -e Tools/DocGen -q

test: test-bom test-docgen

test-bom:
	$(PYTHON) -m pytest Tools/BOMManager/tests -q

test-docgen:
	$(PYTHON) -m pytest Tools/DocGen/tests -q

validate:
	$(PYTHON) -m docgen validate

site:
	$(PYTHON) -m docgen site --output-dir site

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
