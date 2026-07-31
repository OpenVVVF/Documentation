.PHONY: help install test test-bom test-docgen validate docs clean

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
	@echo "  docs         build all product manuals"
	@echo "  clean        remove build artifacts and venv"

install:
	python3 -m venv $(VENV)
	$(PIP) install -e tools/bom-manager -q
	$(PIP) install -e tools/docgen -q

test: test-bom test-docgen

test-bom:
	$(PYTHON) -m pytest tools/bom-manager/tests -q

test-docgen:
	$(PYTHON) -m pytest tools/docgen/tests -q

validate:
	$(PYTHON) -m docgen validate

docs:
	$(PYTHON) -m docgen build --product OV-MOTO-C2 --output docs/manuals/product-manuals/openvvvf-motorcycle-kit-c2.md

clean:
	rm -rf $(VENV) build dist .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
