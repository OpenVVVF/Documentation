---
doctype: Tool Manual
doc_id: OV-TOOLS-TELEMETRY-OVERLAY
title: Telemetry Overlay
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-10-19"
description: Branded telemetry-video overlay tool that renders RTE session data onto run-footage videos for test evidence.
nav_order: 605
placeholder: true
normative_refs:
  - OV-TOOLS-INDEX
  - OV-TOOLS-TELEMETRY-VIEWER
---

# Telemetry Overlay

The Telemetry Overlay tool renders OpenVVVF-branded telemetry overlays on top of recorded run videos, producing self-contained evidence videos for test reports. Given an RTE runtime-session log (see [Data/Tests registry](../../../Data/Tests/README.md)) and a source video of the run, it composites live signal panels and a synchronized timeline onto the footage, frame-accurate to the session timestamps.

> **Placeholder:** this tool is under active development. The v2 configuration schema and CLI below describe the intended interface; field-by-field details marked *TBD* may change before the first release. Source code lives in `Tools/TelemetryOverlay/`.

## Features

- Overlay branded telemetry panels onto raw run footage (camera or screen capture).
- Synchronize the RTE runtime-session timeline with the video time base.
- Compose multiple signal panels (gauges, traces, numeric readouts) in configurable layouts.
- Produce per-test overlay videos ready to be filed under `Data/Tests/<test>/video/` and referenced from test reports.

Unlike the [Telemetry Viewer](../OpenVVVF-Telemetry-Viewer/Index.md), which is interactive and browser-based, the overlay tool produces a fixed rendered video deliverable.

## Configuration (v2 schema)

The tool is driven by a JSON configuration file. A test folder in the [test registry](../../../Data/Tests/README.md) carries its copy as `test.overlay.json`, so one `Data/Tests/OV-TEST-<NNN>-<slug>/` folder fully describes how to regenerate its overlay video.

Top-level fields:

| Field | Description |
|-------|-------------|
| `test` | Identity of the test this overlay belongs to (test number and slug, e.g. `OV-TEST-007-induction-noload-1h`); used for title overlays and defaults. |
| `brand` | Branding block: logo assets, fonts, accent colors, and optionally sponsor marks to composite into the frame. |
| `session` | Path to the RTE runtime-session source (`runtime-session-*.jsonl`, typically under the test folder's `raw/`), plus any signal resampling/decimation settings. |
| `video` | Source video path (typically under the test folder's `video/`), start timestamp, and frame-rate/timebase information used to align session time to video time. |
| `fps` | Output frame rate; independently configurable from the source video frame rate when re-timing is needed. |
| `layout` | Screen layout definition: frame geometry, panel grid/docking positions, and safe margins. |
| `signals` | Signal selection and scaling: which session signals are shown, their units, ranges, and smoothing. |
| `panels` | Panel definitions: types (trace graph, gauge, numeric readout, status flags), which signals each panel shows, and per-panel styling; binds to `layout` slots. |
| `timeline` | Timeline/seek-bar configuration: duration display, command/fault event markers, and phase annotations along the bottom of the frame. |

## CLI

```text
telemetry-overlay sample    <config>   # render a small sample of frames to verify alignment before a full render
telemetry-overlay panels    <config>   # render the panel layer only (transparent background) for inspection or external compositing
telemetry-overlay composite <config>   # composite the panel layer onto the source video into the final overlay video
telemetry-overlay build     <config>   # run the full pipeline: sample checks, panels, composite (the one-shot production path)
```

Typical workflow from a registered test folder:

```bash
telemetry-overlay sample    Data/Tests/OV-TEST-000-stray-recovery/test.overlay.json
telemetry-overlay build     Data/Tests/OV-TEST-000-stray-recovery/test.overlay.json
```

## Filing overlay videos

Rendered videos are evidence artifacts, not data sources. File them under the test folder's `video/` (or `artifacts/`) directory in `Data/Tests/<NNN>-<slug>/` and link them from the corresponding test report under `Docs/Testing/` by `doc_id`.

## Source

The implementation lives in `Tools/TelemetryOverlay/` in this repository; the eventual user-facing entry point will be the `telemetry-overlay` CLI shown above. *(Tool package under development — see the placeholder notice.)*
