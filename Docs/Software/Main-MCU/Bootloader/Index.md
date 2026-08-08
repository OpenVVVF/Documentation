---
doctype: Software Manual
doc_id: OV-SW-MAINMCU-BOOT
title: Bootloader
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - software-target-main-mcu
version: "0.1"
date: "2026-08-08"
status: draft
placeholder: true
description: STM32H723ZG bootloader - firmware update via CAN/USB/UART, HMAC signing, anti-rollback, and safe-state preconditions.
nav_order: 412
normative_refs:
  - OV-SAF-TARA-INDEX
  - OV-CA-SWM-INDEX
---

# Bootloader

> **Placeholder** - This document will describe the main MCU bootloader and firmware-update mechanism. The old SWAD content will not be migrated directly.

## Planned sections

1. Boot flow and recovery
2. CAN update protocol
3. USB/UART update protocol
4. HMAC-SHA256 firmware signing
5. Anti-rollback counter
6. Update preconditions and safe state
7. Key rotation and user-managed keys
8. Test cases and validation evidence
