---
doctype: Index
doc_id: OV-C2-DD-INDEX
title: Design Documents
product_line: openvvvf
applies_to:
  - chassis-size-2
version: "0.1"
date: "2026-08-07"
description: Engineering analyses, calculations, and design rationale for the Chassis Size 2 power stage.
nav_order: 240
normative_refs:
  - OV-C2-INDEX
---

# Design Documents

Engineering reference documents for the C2 power stage: thermal models, loss calculations, component sizing, and other analyses that support the hardware design.

- **[System Thermal Analysis](Thermal-Analysis/Index.md)** - IGBT and diode losses, inverter efficiency, and heatsink/baseplate sizing for the traction inverter.
- **[DC Link Thermal Analysis](DC-Link-Thermal/Index.md)** - DC-link capacitor bank standoff heat-path and thermal resistance analysis.
- **[DC Link Capacitor Ripple Current and Thermal Load](DC-Link-Ripple/Index.md)** - RMS ripple-current derivation and per-can ESR heating for the DC-link capacitor bank across the operating envelope, checked against the Nichicon UCS datasheet ripple ratings.
