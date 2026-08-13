---
doctype: Index
doc_id: OV-SW-MAINMCU-INDEX
title: Main MCU Software
product_line: openvvvf
applies_to:
  - software-target-main-mcu
version: "0.1"
date: "2026-08-08"
description: STM32H723ZG main MCU firmware - FOC motor control, sensor acquisition, CAN, and safe-state management.
nav_order: 410
---

# Main MCU Software

The main MCU (STM32H723ZG) runs FOC motor control, sensor acquisition, CAN communication, and safe-state management.

- **[Architecture](Architecture/Index.md)** - Software architecture, layers, state machine, and module overview
- **[Bootloader](Bootloader/Index.md)** - Firmware update, signing, and recovery
- **[Encoder Offset Calibration](Encoder-Offset-Calibration/Index.md)** - Root-cause analysis of the encoder-offset calibration bug and its fix
- **[MPC Multi Rate Sampling](MPC-Multi-Rate-Sampling/Index.md)** - Multi-rate phase-current sampling plan
- **[Codebase Improvement Plan](Codebase-Improvement-Plan/Index.md)** - Firmware readability, reliability, and safety hardening plan
