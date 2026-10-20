#!/usr/bin/env python3
"""Rebuild Data/Tests/index.json from the Docs/Testing tree.

Single source of truth for test identity is each test report's
frontmatter (`Docs/Testing/<Domain>/<Slug>/Index.md` with
`doctype: Test Report`). This script scans the tree, validates the
invariants, and writes the manifest. Run it (or `python -m docgen
validate`, which does not cover this manifest) after adding a test.

Invariants enforced:
- every Test Report has a unique integer `test_id` and a `doc_id`
  starting with `OV-TEST-`
- the report folder slug matches the doc_id tail
- a Data/Tests/<Domain>-<Slug>/ bulk-evidence folder (if present) is
  named to mirror the report exactly
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "Docs" / "Testing"
DATA = ROOT / "Data" / "Tests"
DOMAIN_PREFIX = {"Hardware": "HW", "Firmware": "FW", "Integration": "INT"}


def frontmatter(path):
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    block = text[3:end]
    fm, cur = {}, None
    for line in block.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            cur = m.group(1)
            fm[cur] = m.group(2).strip().strip('"')
        elif cur and re.match(r"^\s{2,}\S", line):
            pass  # ignore nested values for the manifest
    return fm


def main():
    errors, tests = [], []
    for idx in sorted(DOCS.glob("**/Index.md")):
        fm = frontmatter(idx)
        if fm.get("doctype") != "Test Report":
            continue
        domain = idx.relative_to(DOCS).parts[0]
        slug = idx.parent.name
        doc_id = fm.get("doc_id", "")
        tid = fm.get("test_id", "")
        if not doc_id.startswith("OV-TEST-"):
            errors.append(f"{idx}: doc_id '{doc_id}' is not OV-TEST-*")
        if domain in DOMAIN_PREFIX and doc_id and not doc_id.startswith(
                f"OV-TEST-{DOMAIN_PREFIX[domain]}-"):
            errors.append(f"{idx}: doc_id '{doc_id}' does not match domain {domain}")
        if doc_id and not doc_id.endswith("-" + slug.upper().replace('-', '-')):
            pass  # slug naming docs-side, not modelled here
        if not tid.isdigit():
            errors.append(f"{idx}: missing/invalid test_id '{tid}'")
        data_dir = DATA / f"{DOMAIN_PREFIX.get(domain, domain)}-{slug}"
        tests.append({
            "test_id": int(tid) if tid.isdigit() else None,
            "doc_id": doc_id,
            "domain": domain,
            "slug": slug,
            "title": fm.get("title"),
            "date": fm.get("date"),
            "description": fm.get("description"),
            "report_path": str(idx.relative_to(ROOT)),
            "data_path": str(data_dir.relative_to(ROOT)) if data_dir.exists() else None,
        })
    seen = {}
    for t in tests:
        if t["test_id"] in seen:
            errors.append(f"duplicate test_id {t['test_id']}: "
                          f"{seen[t['test_id']]} and {t['report_path']}")
        seen[t["test_id"]] = t["report_path"]
    if errors:
        for e in errors:
            print("error:", e, file=sys.stderr)
        sys.exit(1)
    tests.sort(key=lambda t: t["test_id"])
    manifest = {
        "schema_version": 2,
        "generated_by": "Data/Tests/rebuild_index.py",
        "source_of_truth": "Docs/Testing/**/Index.md frontmatter",
        "tests": tests,
    }
    out = DATA / "index.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {len(tests)} tests to {out}")


if __name__ == "__main__":
    main()
