---
doctype: Test Report
doc_id: OV-TEST-INT-ZERO-DSR-ROAD-2
title: Zero DSR 2018 Road Test 2 - Sponsor Telemetry Overlay Video
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - application-profile-motorcycle
version: "0.2"
date: "2026-10-19"
description: Second on-vehicle run on the Zero DSR, captured both as live telemetry and as a helmet-camera video; the two were fused into a branded F1-style telemetry overlay video for sponsor review.
test_id: 12
nav_order: 373
normative_refs:
  - OV-TEST-INT-INDEX
  - OV-TEST-INT-ZERO-DSR-ROAD
---

# Zero DSR 2018 Road Test 2 — Sponsor Telemetry Overlay Video

This report covers the second logged road ride of the OpenVVVF Gen7 control board in the Zero DSR (see [test 11, the first road test](../Zero-DSR-Road-Test/Index.md) for the test-article description). The run's purpose was demonstration rather than bring-up: produce a full-length, sponsor-presentable video that shows the inverter's live telemetry next to the ride footage.

## Test article and setup

- **Vehicle / test article:** identical to the first road test — Zero DSR (MY2018), stock Z-Force motor, stock ZF14.4 pack, Gen7 control board.
- **Logging:** RTE Android over USB, protocol TLM1, live mode. Session export `raw/runtime-session-2026-10-17T01-16-37.122Z-1ed2dc74.jsonl.zst` in `Data/Tests/INT-Zero-DSR-Road-Test-2/raw/` (~0.68 GB raw, zstd-compressed); 917 s, full signal set, no corrupted frames.
- **Video:** helmet camera, 1080p portrait (rotation −90°), 788.1 s, `raw/VID_20261016_181705.mp4` (untracked, ~1.9 GB). Camera clock pinned against the telemetry clock (video starts 30.18 s into the telemetry session; verified at the first-throttle launch).
- **Overlay production:** `Tools/TelemetryOverlay` (`vvvf-overlay build`), run config `overlay.json` (tracked, in this folder). Source video trimmed to 728.05 s to exclude the arrival segment; output is a 737.1 s composite with 5 s branded intro and 4 s sponsor-wall outro.

## Results

- Peak DC pack power: **26.4 kW** (261 A × ~107 V, vehicle pack telemetry); peak phase current ~183 A; speed up to **51 mph**, motor rpm up to ~2990.
- Inverter temperatures stayed in a 42–50 °C band throughout; pack SOC moved 73 → 69 %.
- DC-link power channel and the vehicle's pack-power telemetry channel carry opposite sign conventions (DC link negative while motoring); the overlay normalizes this so traction power is positive and regen would read negative. No regen events occurred in this capture.
- Raw DC-link current includes single-sample glitches (±800 A); the overlay displays median-window-filtered values.

## Findings and follow-ups

- Regen is not visible in this session: the vehicle's pack-current telemetry never goes negative, and the DC-link power channel's signed value is noise-dominated at cruise. If regen verification matters for sponsor review, capture a dedicated braking run.
- The video/telemetry clock offset (30.18 s) relies on the camera clock; consider a frame of spoken "mark" video at session start to make alignment self-documenting for future rides.

## Artifacts

| Artifact | Path |
|----------|------|
| Brand overlay video (sponsor render) | `Data/Tests/INT-Zero-DSR-Road-Test-2/video/` (untracked) |
| Overlay run config | `Data/Tests/INT-Zero-DSR-Road-Test-2/test.overlay.json` (tracked) |
| Raw telemetry session | `Data/Tests/INT-Zero-DSR-Road-Test-2/raw/runtime-session-2026-10-17T01-16-37.122Z-1ed2dc74.jsonl.zst` |
| Source helmet video | `Data/Tests/INT-Zero-DSR-Road-Test-2/raw/VID_20261016_181705.mp4` |
