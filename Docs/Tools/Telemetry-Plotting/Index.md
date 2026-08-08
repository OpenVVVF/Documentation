---
doctype: Tool Manual
doc_id: OV-TOOLS-RTEPLOT
title: Telemetry Plotting Tool
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-1
  - chassis-size-2
  - chassis-size-3
version: "0.1"
date: "2026-08-08"
status: draft
description: RTE telemetry plotting tool for turning JSONL logs into figures.
nav_order: 710
normative_refs:
  - OV-TOOLS-INDEX
---

# Telemetry Plotting Tool

The telemetry plotting tool turns RTE `.jsonl` logs into publication-ready figures for analysis, debugging, and test reports.

## Purpose

- Quickly visualize control problems from field or lab captures.
- Generate consistent figures for documentation and presentations.
- Support common diagnostic views: currents, voltages, field weakening, overmodulation, and resistance calibration.

## Quick start

```bash
cd RTE/Tools/rteplot
../../.venv/bin/python rteplot.py info example.jsonl
../../.venv/bin/python rteplot.py recipes
../../.venv/bin/python rteplot.py plot example.jsonl --recipe resistance -o result.png
```

## Recipes

| Recipe | View |
|--------|------|
| `currents` | Phase and d/q currents |
| `voltages` | Phase, d/q, and DC-link voltages |
| `fieldweakening` | Speed, id/iq, and modulation index |
| `overmodulation` | Modulation index and voltage saturation |
| `fwanalysis` | Field-weakening diagnostic with anomaly regions |
| `resistance` | Resistance calibration currents, bus voltage, and measured resistance |

## Output formats

- `.png` and `.jpg` for slides and papers.
- `.html` for interactive pan/zoom plots.
- `.pdf` and `.svg` for vector output.

## More information

See the `README.md` in `RTE/Tools/rteplot` for the full CLI reference and instructions on adding custom recipes.
