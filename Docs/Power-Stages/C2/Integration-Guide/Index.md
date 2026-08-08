---
doctype: Integration Manual
doc_id: OV-C2-IG-INDEX
title: Integration Guide
product_line: openvvvf
applies_to:
  - chassis-size-2
version: "0.2"
date: "2026-08-08"
status: draft
placeholder: true
description: Installation, integration, and operating guide for the Chassis Size 2 power-stage family. Under revision.
nav_order: 321
normative_refs:
  - OV-SAF-HARA-CORE
  - OV-SAF-HARA-PROF-MOTO
---

# Integration Guide

> **NOTE**
> This guide is under revision. The previous version contained a large amount of control-module content that is shared across all chassis sizes and belongs in the `OV-CA-UHW-INDEX` Control Assembly User Hardware Manual. It also presented specific capacitor and current ratings that do not apply to all C2 variants.
>
> The C2 chassis family is designed to support a range of DC-link capacitor voltages (200 V class through 450 V class) and continuous current ratings. Specific BOMs, ratings, and variant-specific instructions will be documented here once the platform-vs-chassis split is finalized.
>
> For now, refer to the assembly guide, design documents, and HARA / TARA for safety-relevant information.

## Planned content

- Mechanical installation and mounting
- HV and LV electrical interface
- Thermal management and heatsink requirements
- CAN integration and reference frame definitions
- Precharge and safe-state behavior
- Troubleshooting
