---
doctype: Software Manual
doc_id: OV-CA-SWM-INDEX
title: Software Manual
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - software-target-main-mcu
  - software-target-safety-coprocessor
version: "0.1"
date: "2026-08-08"
status: draft
placeholder: true
description: Base firmware image, RTE Studio setup, flashing procedures, and custom software development for the control module.
nav_order: 120
normative_refs:
  - OV-SW-MAINMCU-INDEX
  - OV-SW-MAINMCU-ARCH
  - OV-SW-MAINMCU-BOOT
  - OV-SW-COPROC-INDEX
  - OV-SW-COPROC-ARCH
  - OV-SW-RTE-INDEX
  - OV-SW-RTE-INTERFACE
---

# Software Manual

This manual describes the software side of the OpenVVVF control module.

> **Placeholder** - This manual is being rewritten. The previous Software Architecture Document mixed user, developer, and safety-coprocessor material; it is being split into the documents below.

## Planned sections

1. Base firmware image overview
2. Flashing and recovery procedures
3. RTE Studio setup and configuration
4. Building and loading custom application code
5. Firmware updates and rollback
6. Safety-coprocessor interaction
7. Troubleshooting

## Related documents

- `OV-SW-MAINMCU-INDEX` - Main MCU Software
- `OV-SW-MAINMCU-ARCH` - Architecture
- `OV-SW-MAINMCU-BOOT` - Bootloader
- `OV-SW-COPROC-INDEX` - Safety Coprocessor Software
- `OV-SW-COPROC-ARCH` - Architecture
- `OV-SW-RTE-INDEX` - RTE Studio Software
- `OV-SW-RTE-INTERFACE` - Interface
