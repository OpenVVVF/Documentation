---
doctype: Tool Manual
doc_id: OV-TOOLS-TELEMETRY-VIEWER
title: Telemetry Viewer
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-1
  - chassis-size-2
  - chassis-size-3
version: "0.1"
date: "2026-08-08"
status: draft
description: Web-based RTE telemetry log viewer for interactive signal inspection.
nav_order: 720
normative_refs:
  - OV-TOOLS-INDEX
---

# Telemetry Viewer

The Telemetry Viewer is a browser-based tool for inspecting RTE JSONL telemetry logs interactively. It runs entirely client-side: no data is uploaded to a server.

## Features

- Load RTE `.jsonl` telemetry files directly in the browser.
- Select and plot any signal in the log.
- Pan, zoom, and inspect data points interactively with Plotly.
- Quickly check signal lists, ranges, and sample counts.

## Using the viewer

1. Open the [Telemetry Viewer](telemetry-viewer.html).
2. Click **Load JSONL** and select an RTE telemetry log.
3. Choose the signals you want to plot from the sidebar.
4. Use the Plotly toolbar to zoom, pan, or export the figure.

## Data privacy

The viewer parses files locally in your browser. Telemetry data never leaves your machine.

## Source

The viewer is a single self-contained HTML file. It can be copied to a workstation for offline use. Plotly.js is loaded from a CDN by default; for fully-offline operation, download Plotly and update the `<script>` tag in the HTML.
