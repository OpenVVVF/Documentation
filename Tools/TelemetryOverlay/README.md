# TelemetryOverlay

OpenVVVF branded telemetry video overlays: RTE runtime-session JSONL +
camera video in, F1-style telemetry dash video out — with branded
intro/outro title cards, a sponsor wall, and an always-on watermark.

## Install

```sh
pip install -e Tools/TelemetryOverlay    # needs Pillow + numpy + ffmpeg
```

`ffmpeg` and `ffprobe` must be on the PATH (video encoding only; the
test suite does not need them).

## CLI

```sh
# eyeball everything without encoding any video
vvvf-overlay sample run.json -t 100,400,700     # panel PNGs per panel per time
vvvf-overlay sample run.json --cards-only       # intro/outro frames + watermark PNG

# render the panel streams declared in layout.panels (one mp4 each)
vvvf-overlay panels run.json

# composite: video fit + panels + watermark + freeze splices + intro/outro
vvvf-overlay composite run.json VIDEO.mp4 OUT.mp4

# both of the above in one step
vvvf-overlay build run.json VIDEO.mp4 OUT.mp4

# (re)build just the cached brand assets
vvvf-overlay cards run.json
vvvf-overlay assets run.json -o watermark.png
```

Paths in the config (`session`, panel files) are resolved relative to
the config file's directory. Intro/outro card videos and the watermark
PNG are cached next to the config in `_brand_cache/`, keyed by a hash of
the test/brand/fps/canvas config — changing only telemetry or the
timeline does not re-encode the cards.

## Config schema (v2)

One JSON file describes the whole run. Example skeleton:

```json
{
  "test": {"number": "OV-TEST-011", "title": "Gen 7 Dyno Shakedown",
           "description": "...", "date": "2026-10-16"},
  "brand": {"watermark": true,
            "sponsors": ["mitsubishi-electric", "mouser", "scs"],
            "intro_s": 5.0, "outro_s": 4.0},
  "session": "runtime-session-...jsonl",
  "video": {"duration": 728.05, "offset": 30.18},
  "fps": 15,
  "layout": {"canvas_w": 1920, "canvas_h": 1080,
             "video_width": 608, "video_height": 1080,
             "panels": [{"file": "left.mp4", "x": 40},
                        {"file": "right.mp4", "x": 1304}]},
  "signals": {"thr": {"source": "thr_a_norm", "resample": "median",
                      "win": 0.1, "clip": [0, 1]}},
  "panels": {"left":  {"panel_width": 576, "panel_height": 1080,
                       "widgets": []},
             "right": {"panel_width": 576, "panel_height": 1080,
                       "widgets": []}},
  "timeline": []
}
```

### Top level

| key | type | default | meaning |
|---|---|---|---|
| `test` | object | — | test metadata for the intro/outro/watermark |
| `brand` | object | — | branding switches and sponsor list |
| `session` | string | required | path to a runtime-session JSONL (config-relative); see "Compressed session paths" below |

#### Compressed session paths

`session` may point at the plain export or at a compressed copy:
`*.jsonl` (plain), `*.jsonl.gz` (gzip), and `*.jsonl.zst` (zstd, the
format `Data/Tests/<DOM>-<Slug>/raw/` archives use). `.zst` files are
streamed through the `zstd` CLI (`zstd -dc --long=31`), which must be
on the PATH — no extra Python packages are needed. All formats are
decompressed line by line, so loading a large archive costs no more
memory than the plain file.
| `video` | object | required | `duration` (s) of the output main segment; `offset` = telemetry time at video t=0 |
| `fps` | number | 15 | panel + card frame rate |
| `layout` | object | required | canvas and placement, see below |
| `signals` | object | `{}` | panel signal name -> source recipe, see below |
| `panels` | object | required | one widget config per entry in `layout.panels`, keyed by file stem (`left.mp4` -> `panels.left`) |
| `timeline` | array | `[]` | marker/note/freeze events, times in VIDEO seconds |

### `test` / `brand`

| key | meaning |
|---|---|
| `test.number` | test id, e.g. `OV-TEST-011`; shown in intro, outro, watermark |
| `test.title` / `test.description` / `test.date` | intro card content (description is word-wrapped, max 4 lines) |
| `brand.watermark` | draw the 35%-opacity wordmark + "TEST <number>" over the video box (default true) |
| `brand.watermark_opacity` | watermark alpha, 0..1 (default 0.35) |
| `brand.sponsors` | sponsor slugs: `mitsubishi-electric`, `mouser`, `scs` (intro strip + outro wall; dark logos are normalized to white) |
| `brand.intro_s` / `brand.outro_s` | card durations in seconds (set to 0 to skip a card); `brand.intro` / `brand.outro` (bool) can disable outright |

### `layout`

| key | default | meaning |
|---|---|---|
| `canvas_w` / `canvas_h` | 1920 / 1080 | output frame size |
| `video_width` / `video_height` | 1344 / 1080 | box the video is FIT into (aspect preserved, centered, never stretched or cropped; rotated phone video is autorotated by ffmpeg) |
| `video_x` | centered | left edge of the video box |
| `panels` | required | list of `{"file": "left.mp4", "x": 40}`; each file maps to `panels.<stem>` |

### `signals` (panel name -> recipe)

| key | default | meaning |
|---|---|---|
| `source` | — | session channel name |
| `mul` | — | instead of `source`: list of two channel names; the series is their sample-by-sample product |
| `resample` | `nearest` | `nearest` or `median` (glitch-proof window median) |
| `win` | 0.15 | median window half-width (s) |
| `valid` | — | lambda string evaluated on the value array, e.g. `"lambda v: v < 1000"` |
| `max_abs` | — | drop samples with `abs(v) > max_abs` |
| `scale` / `offset` / `clip` / `abs` | — | linear transform, clamp `[lo, hi]`, absolute value |

Bar and graph `"max": "auto"` (and graph `"min": "auto"`) are resolved
from the data (99.5th percentile * 1.1). Negative values are supported
throughout (signed channels, `zero_center` bars, negative graph ranges).

### `panels.<name>` -> widgets

Each panel is `{"panel_width", "panel_height", "bg"/"track"/"accent",
"pad", "widgets": [...]}`; widgets paint top-down by `y`.

| widget | key fields |
|---|---|
| `header` | `logo` path (default: white OpenVVVF wordmark), `logo_height`, `title`, `subtitle`, `show_dot`, live clock, next-marker countdown; `divider_y` |
| `bigvalue` | `signal`, `label`, `unit`, `size`, `value_drop`, `unit_drop`, `format`, `color`, `color_thresholds` |
| `bar` | `signal`, `max` (or `"auto"`), `color`, `segments`, `value_show`, `value_scale`, `value_format`, `color_thresholds`, `zero_center` + `neg_color` (bidirectional) |
| `statsrow` | `items`: `[{label, signal, format, color, size}]` |
| `tempbars` | `label`, `signals`, `names`, `max`, `color`, `color_thresholds` |
| `graphs` | `window_s`, `h`, `graphs`: `[{signal, min, max, color, label}]`, event markers from the timeline |

### `timeline` (times in VIDEO seconds)

| kind | effect |
|---|---|
| `marker` | red tick on graph widgets + upcoming countdown in the header |
| `note` | annotation card (auto-fit label + wrapped `text`) for `duration` s |
| `freeze` | like `note`, plus panel values hold at the event time and the compositor splices a still frame of the video for exactly `duration` s |

## Finding `video.offset`

The offset is the telemetry time at video t=0. Derive it from the
session `started_at_utc` vs the camera clock; cross-check against a
known event (e.g. "first throttle ~8 s in"). If the video leads the
telemetry by N s, INCREASE the offset by N.

## Development

```sh
cd Tools/TelemetryOverlay
python -m pytest          # synthetic fixtures only; no ffmpeg required
```
