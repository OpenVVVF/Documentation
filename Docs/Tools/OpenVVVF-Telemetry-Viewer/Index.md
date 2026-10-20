---
doctype: Tool Manual
doc_id: OV-TOOLS-TELEMETRY-VIEWER
title: Telemetry Viewer
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1.1"
date: "2026-10-19"
description: Browser-based interactive viewer for RTE JSONL telemetry logs.
nav_order: 601
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

1. Open the [OpenVVVF Telemetry Viewer](telemetry-viewer.html).
2. Click **Load JSONL** and select an RTE telemetry log.
3. Choose the signals you want to plot from the sidebar.
4. Use the Plotly toolbar to zoom, pan, or export the figure.

### Right-click menu

Right-click anywhere on the plot to open a context menu for adding markers, annotations, zooming to a time, or fitting the X axis.

### Command markers

Click a row in the **Commands** panel to toggle a vertical marker at that command time. Click the same row again to remove the marker.

### Linked files

You can link directly to a telemetry file so the viewer opens and loads it automatically. Add the `?file=` parameter with a path relative to the viewer, and use the existing `#s=` hash to pre-select signals.

Example:

```text
telemetry-viewer.html?file=../../Testing/Hardware/Induction-Motor-Calibration/Resistance/induction-cal.jsonl#s=cg_iu_a:left
```

[Open induction calibration log with cg_iu_a plotted](telemetry-viewer.html?file=../../Testing/Hardware/Induction-Motor-Calibration/Resistance/induction-cal.jsonl#s=cg_iu_a:left)

### Compressed files

In addition to plain `.jsonl`, the viewer opens gzip- and zstd-compressed logs (`.jsonl.gz`, `.jsonl.zst`). This works both for files dropped into the page and for `?file=` links — the viewer detects the compression from the file extension and stream-decompresses in the browser:

```text
telemetry-viewer.html?file=../../../Data/Tests/INT-Zero-DSR-Road-Test/raw/runtime-session-2026-10-16T10-35-13.517Z-11b27791.jsonl.zst#s=display_speed_mph:left
```

Decompression uses the browser's built-in `DecompressionStream` API, so no data leaves the machine and no extra JavaScript is needed. Files are parsed incrementally as the (decompressed) stream arrives — the decoded text is never buffered as one string, so captures beyond the browser's string-size limit (hundreds of MB, millions of samples) load fine. Caveats:

- `gzip` is supported in Chrome/Edge 80+, Firefox 113+, and Safari 16.4+.
- `zstd` support is newer: Chrome/Edge 123+ and Safari 18.4+; Firefox does not yet support `DecompressionStream('zstd')`.

If your browser cannot decompress a format natively, the viewer shows an error with the alternative: decompress the file locally first, e.g. with `unzstd file.jsonl.zst` (or `zstd -d file.jsonl.zst`), then open the resulting `.jsonl`.

## Data privacy

The viewer parses files locally in your browser. Telemetry data never leaves your machine.

## Source

The viewer is a single self-contained HTML file. It can be copied to a workstation for offline use. Plotly.js is loaded from a CDN by default; for fully-offline operation, download Plotly and update the `<script>` tag in the HTML.
