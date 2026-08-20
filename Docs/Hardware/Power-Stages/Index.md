---
doctype: Index
doc_id: OV-PS-INDEX
title: Power Stages
product_line: openvvvf
applies_to:
  - chassis-size-2
version: "0.3"
date: "2026-08-20"
description: Physical chassis and inverter assemblies. Each chassis family has an integration guide and an assembly guide.
nav_order: 200
---

# Power Stages

OpenVVVF power stages are physical chassis/inverter assemblies that pair with the control module. Each chassis is a family of variants built around a common form factor and IGBT module choice; the same control module can drive any of them.

## Which chassis do I have?

| Chassis | Form factor | Typical DC link | Current rating (RMS) | Status |
|---------|-------------|-----------------|--------------------|--------|
| **[C2 - Chassis Size 2](C2/Index.md)** | Mid-size | 150 / 200 / 400 V class, per DC-link capacitor selection | **220 A continuous / 600 A peak (60 s)** | Implemented, under test |

C2 ratings are stated as continuous vs peak per the IEC 61800-2 style 60 s overload convention: the 600 A peak is time-limited (60 s per event, windowed RMS over any 10 min ≤ the continuous rating), and the 220 A continuous figure is a conservative analytical bound set by the DC-link plate temperature (FSR-08 90 °C derate onset) at 6 kHz PWM, below the ~320 A electrolytic ripple limit. See `OV-C2-DD-THERMAL` (§6.4), `OV-C2-DD-DCLINK-RIPPLE`, and `OV-C2-DD-DCLINK-THERMAL`.

- If you are building or installing a C2 unit, start with the [C2 Integration Guide](C2/Integration-Guide/Index.md) or [C2 Assembly Guide](C2/Assembly-Guide/Index.md).

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.2 | 2026-08-15 | (Prior revision; see git history.) |
| 0.3 | 2026-08-20 | C2 current rating restated as 220 A continuous / 600 A peak (60 s, IEC 61800-2 style overload convention), replacing the previous "~600 A continuous" advertisement; continuous rating is a conservative analytical bound set by the DC-link plate temperature at 6 kHz PWM, below the ~320 A electrolytic ripple limit. References to the C2 design docs added. |
