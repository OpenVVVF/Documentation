---
doctype: Index
doc_id: OV-PS-INDEX
title: Power Stages
product_line: openvvvf
applies_to:
  - chassis-size-1
  - chassis-size-2
  - chassis-size-3
version: "0.1"
date: "2026-08-08"
status: draft
description: Physical chassis and inverter assemblies. Each chassis family has an integration guide and an assembly guide.
nav_order: 200
---

# Power Stages

OpenVVVF power stages are physical chassis/inverter assemblies that pair with the control module. Each chassis is a family of variants built around a common form factor and IGBT module choice; the same control module can drive any of them.

## Which chassis do I have?

| Chassis | Form factor | Typical DC link | Continuous current | Status |
|---------|-------------|-----------------|--------------------|--------|
| **[C1 - Chassis Size 1](C1/index.html)** | Compact / small | Low-voltage, low-current class | TBD | In design |
| **[C2 - Chassis Size 2](C2/index.html)** | Mid-size | 140 V nominal / up to 450 V class | ~600 A | Implemented, under test |
| **[C3 - Chassis Size 3](C3/index.html)** | Large | Up to 1200 V | Up to 1400 A | In development |

- If you are building or installing a C2 unit, start with the [C2 Integration Guide](C2/Integration-Guide/index.html) or [C2 Assembly Guide](C2/Assembly-Guide/index.html).
- C1 and C3 are not yet released; their documentation will be added as the designs mature.
