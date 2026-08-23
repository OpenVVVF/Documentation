---
doctype: Index
doc_id: OV-PS-INDEX
title: Power Stages
product_line: openvvvf
applies_to:
  - chassis-size-2
version: "0.4"
date: "2026-08-23"
description: Physical chassis and inverter assemblies. Each chassis family has an integration guide and an assembly guide.
nav_order: 200
---

# Power Stages

OpenVVVF power stages are physical chassis/inverter assemblies that pair with the control module. Each chassis is a family of variants built around a common form factor and IGBT module choice; the same control module can drive any of them.

## Which chassis do I have?

| Chassis | Form factor | Typical DC link | Current rating (peak, RMS in parentheses) | Status |
|---------|-------------|-----------------|--------------------|--------|
| **[C2 - Chassis Size 2](C2/Index.md)** | Mid-size | 150 / 200 / 400 V class, per DC-link capacitor selection | **465 A (330 A RMS) continuous / 600 A (424 A RMS) peak, 60 s** | Implemented, under test |

C2 ratings are stated as continuous vs peak per the IEC 61800-2 style 60 s overload convention, dual-labeled peak with RMS in parentheses: the 600 A peak (424 A RMS) is time-limited (60 s per event, windowed RMS over any 10 min ≤ 330 A RMS), and the 465 A peak (330 A RMS) continuous figure is a conservative analytical bound set by the DC-link electrolytic ripple rating at 6 kHz PWM. The DC-link plate temperature is an informational bound only after the rev-B 6.35 mm spreader plate (≈ 87 °C bound at the continuous point, below the FSR-08 90 °C derate onset). See `OV-C2-DD-THERMAL` (§6.4), `OV-C2-DD-DCLINK-RIPPLE`, and `OV-C2-DD-DCLINK-THERMAL`.

- If you are building or installing a C2 unit, start with the [C2 Integration Guide](C2/Integration-Guide/Index.md) or [C2 Assembly Guide](C2/Assembly-Guide/Index.md).

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.2 | 2026-08-15 | (Prior revision; see git history.) |
| 0.3 | 2026-08-20 | C2 current rating restated as 220 A continuous / 600 A peak (60 s, IEC 61800-2 style overload convention), replacing the previous "~600 A continuous" advertisement; continuous rating is a conservative analytical bound set by the DC-link plate temperature at 6 kHz PWM, below the ~320 A electrolytic ripple limit. References to the C2 design docs added. |
| 0.4 | 2026-08-23 | C2 re-rated per `OV-C2-DD-THERMAL` v1.3: the 600 A figure is peak phase current (424 A RMS), and the continuous rating is raised to 465 A peak (330 A RMS), now set by the electrolytic ripple limit; the rev-B 6.35 mm DC-link spreader plate moved the plate temperature to an informational bound below the FSR-08 derate onset. Ratings dual-labeled peak (RMS). |
