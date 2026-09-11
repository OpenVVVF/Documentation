.PHONY: help install test test-bom test-docgen test-hwrelease hw-update hw-list hw-viewer validate site pdfs manuals serve clean check-clean

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
	@echo "  hw-viewer    regenerate the PCB Tool page"
	@echo "  validate     validate documentation cross-references and frontmatter"
	@echo "  site         build the static HTML documentation site"
	@echo "  pdfs         build the site and generate per-document PDFs into site/pdfs"
	@echo "  manuals      generate umbrella manual PDFs (e.g. full C2 assembly guide)"
	@echo "  serve        serve the built site locally on port 8000"
	@echo "  clean        remove build artifacts and venv"
	@echo "  check-clean  fail if *.egg-info files are tracked in git"
	@echo "  ci_cd        full pre-CI gate (validate + tests + viewer regen + clean checks)"

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
	@bad=$$(git ls-files | grep -E '\.egg-info/' || true); \
	if [ -n "$$bad" ]; then \
		echo "ERROR: *.egg-info files are tracked in git:"; \
		echo "$$bad"; \
		exit 1; \
	fi
	@echo "No tracked *.egg-info content."

# Full pre-CI gate: same checks CI would run, plus regeneration drift checks.
ci_cd: validate test check-clean
	@# Regenerating the tool viewer pages must be a no-op (hash before/after),
	@# or the committed Docs/Tools/*.html files are out of date with Tools/HWRelease.
	@before=$$(md5sum Docs/Tools/BOM-Tool/bom-tool.html Docs/Tools/PCB-Tool/pcb-tool.html); \
	$(MAKE) -s hw-viewer >/dev/null; \
	after=$$(md5sum Docs/Tools/BOM-Tool/bom-tool.html Docs/Tools/PCB-Tool/pcb-tool.html); \
	if [ "$$before" != "$$after" ]; then \
		echo "ERROR: Docs/Tools HTML pages differ from hwrelease output - rerun: make hw-viewer"; \
		exit 1; \
	fi
	@# No stray documentation outside Docs/ (Tools/*/Docs is tool documentation,
	@# vendored libs under Docs/Tools/**/o3dv are assets, not docs).
	@stray=$$(find . -path ./.venv -prune -o -path ./.git -prune -o -path ./build -prune -o \
		-path ./site -prune -o -path '*/Docs' -type d -print 2>/dev/null | \
		grep -v '^\./Docs$$' | grep -vE '^\./Tools/[^/]+/Docs$$' | grep -vE '^\./Tools/[^/]+/src/[^/]+/templates$$' || true); \
	if [ -n "$$stray" ]; then \
		echo "WARNING: unexpected Docs-like directories:"; \
		echo "$$stray"; \
	fi
	@echo "Fully clean: ready for CI/CD push."
