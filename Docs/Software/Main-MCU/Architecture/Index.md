---
doctype: Software Manual
doc_id: OV-SW-MAINMCU-ARCH
title: Architecture
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - software-target-main-mcu
version: "0.1"
date: "2026-08-08"
placeholder: true
description: STM32H723ZG main MCU software architecture - layers, state machine, FOC, modulation, sensing, and safety mechanisms.
nav_order: 411
normative_refs:
  - OV-SAF-HARA-CORE
  - OV-CA-SWM-INDEX
---

# Architecture

> **Placeholder** - This document will define the main MCU software architecture from scratch. The old SWAD is being abandoned.

## Planned sections

1. Design principles and layer model
2. System state machine
3. FOC and modulation library
4. Multi-rate ADC and current sensing
5. CAN communication and protocol model
6. Safe-state and fault management
7. Input validation and parameter storage
8. Power-loss estimator and thermal model
9. Memory layout and startup
10. Traceability to HARA FSRs
