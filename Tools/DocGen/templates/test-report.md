---
# Template for a formal test report.
# Place under Docs/Testing/<Hardware|Firmware|Integration>/<Test-Name>/
doctype: Test Report
doc_id: OV-TEST-XX-XXXX
title: Test Title
product_line: openvvvf
applies_to:
  - replace-me
version: "0.1"
date: "YYYY-MM-DD"
status: draft
description: One-sentence summary of what this test validates.
nav_order: 5NN
normative_refs:
  - OV-TEST-INDEX
  - OV-SAF-HARA-CORE
---

# Test Title

## Objective

What requirement, hazard, or design claim does this test address?

## Setup

- Hardware / software revision under test
- Instrumentation and calibration
- Environmental conditions

## Procedure

1. ...
2. ...

## Results

| Step | Expected | Actual | Verdict |
|------|----------|--------|---------|
| ...  | ...      | ...    | ...     |

## Conclusion

Pass / fail summary and traceability to requirements or HARA items.
