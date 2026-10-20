"""Render telemetry side panels as rawvideo RGB streams / encoded mp4s.

Config v2: one JSON file describes every panel. `layout.panels` lists the
panel outputs ({"file": "left.mp4", "x": 40}); each entry maps to a
widget config under `panels["<file stem>"]` (e.g. "left", "right").

Signal options (unchanged from the prototype): `source` or `mul`
(product of two channels), `resample` (nearest/median), `win`, `valid`
(lambda string), `max_abs`, `clip`, `abs`, `scale`, `offset`. Bar/graph
`"max": "auto"` scales from the data (99.5th percentile).

Timeline times are VIDEO seconds. Kinds: marker (graph tick + header
countdown), note (panel card), freeze (card + panel values hold at the
event moment; the compositor also holds the video frame still).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from .telemetry import Session
from .panel import PanelRenderer
from .timeline import Timeline


def load_config(path):
    cfg = json.loads(Path(path).read_text())
    validate_config(cfg)
    return cfg


def validate_config(cfg):
    """Fail early with a clear message on config-schema mistakes."""
    errs = []
    if "session" not in cfg:
        errs.append("missing 'session' (path to a runtime-session JSONL)")
    lay = cfg.get("layout")
    if not isinstance(lay, dict):
        errs.append("missing 'layout' object")
        lay = {}
    panels = lay.get("panels") or []
    if not panels:
        errs.append("layout.panels is empty; at least one panel is required")
    for p in panels:
        stem = Path(p["file"]).stem if "file" in p else None
        if stem is None:
            errs.append("layout.panels entry without a 'file'")
        elif stem not in (cfg.get("panels") or {}):
            errs.append(f"no panel config for {stem!r} (panels.{stem})")
    for name, pc in (cfg.get("panels") or {}).items():
        if not isinstance(pc.get("widgets"), list):
            errs.append(f"panels.{name}.widgets must be a list")
            continue
        for w in pc["widgets"]:
            if "type" not in w:
                errs.append(f"panels.{name}: widget without a 'type'")
            if w.get("type") in ("bigvalue", "bar") and "signal" not in w:
                errs.append(f"panels.{name}: {w['type']} widget without a 'signal'")
    for e in cfg.get("timeline", []):
        if e.get("kind", "marker") not in ("marker", "note", "freeze"):
            errs.append(f"timeline event with unknown kind {e.get('kind')!r}")
        if "time" not in e or "label" not in e:
            errs.append("timeline event without 'time'/'label'")
    if errs:
        raise ValueError("invalid run config:\n  - " + "\n  - ".join(errs))
    return cfg


def build_grid(cfg):
    v = cfg["video"]
    dur = v["duration"]
    fps = cfg.get("fps", 15)
    n = int(dur * fps)
    video_t = (np.arange(n) + 0.5) / fps
    telem_t = video_t + v.get("offset", 0.0)
    return n, video_t, telem_t


def build_series(cfg, session, telem_t, log=None):
    log = log or (lambda *a: None)
    series = {}
    src_cache = {}

    def cleaned(src, sc):
        if src not in src_cache:
            tv = session.cleaned(src, max_abs=sc.get("max_abs"),
                                 valid=eval(sc["valid"]) if sc.get("valid") else None)
            src_cache[src] = tv
        return src_cache[src]

    for name, sc in cfg.get("signals", {}).items():
        if sc.get("mul"):  # product of two source channels
            parts = []
            for src in sc["mul"]:
                if not session.has(src):
                    log(f"warn: signal '{src}' missing")
                    parts = None
                    break
                tv = cleaned(src, sc)
                if sc.get("resample", "nearest") == "median":
                    parts.append(session.resample_median(tv, telem_t, sc.get("win", 0.15)))
                else:
                    parts.append(session.resample_nearest(tv, telem_t))
            if parts is None:
                continue
            with np.errstate(all="ignore"):
                a = parts[0] * parts[1]
            a[~np.isfinite(a)] = 0.0
        else:
            if not session.has(sc["source"]):
                log(f"warn: signal '{sc['source']}' missing")
                continue
            tv = cleaned(sc["source"], sc)
            if sc.get("resample", "nearest") == "median":
                a = session.resample_median(tv, telem_t, sc.get("win", 0.15))
            else:
                a = session.resample_nearest(tv, telem_t)
        if sc.get("scale"):
            a = a * sc["scale"]
        if sc.get("offset"):
            a = a + sc["offset"]
        if sc.get("clip"):
            a = np.clip(a, *sc["clip"])
        if sc.get("abs"):
            a = np.abs(a)
        series[name] = a
    for pc in (cfg.get("panels") or {}).values():
        resolve_auto_scales(pc, series)
    return series


def resolve_auto_scales(panel_cfg, series):
    """Replace 'max'/'min' values of 'auto' with data-driven percentiles."""

    def fix(key, sig, pct, default):
        a = series.get(sig)
        if not isinstance(key, str) or key != "auto":
            return key
        if a is None or len(a) == 0:
            return default
        return float(np.percentile(np.abs(a), pct)) * 1.1 or default

    for w in panel_cfg["widgets"]:
        if w["type"] == "bar":
            w["max"] = fix(w.get("max"), w["signal"], 99.5, 1.0)
        elif w["type"] == "graphs":
            for g in w["graphs"]:
                g["max"] = fix(g.get("max"), g["signal"], 99.5, 1.0)
                if g.get("min") == "auto":
                    a = series.get(g["signal"])
                    g["min"] = float(np.percentile(a, 0.5)) * 1.1 if a is not None else 0.0


def prepare_run(cfg):
    """Shared per-run setup: session, frame grid, series, timeline."""
    fps = cfg.get("fps", 15)
    session = Session(cfg["session"])
    n, video_t, telem_t = build_grid(cfg)
    series = build_series(cfg, session, telem_t,
                          log=lambda *a: print(*a, file=sys.stderr))
    timeline = Timeline.from_dicts(cfg.get("timeline", []))
    print(f"session {session.duration:.0f}s, {len(series)} signals, "
          f"{n} frames @ {fps}fps", file=sys.stderr)
    return session, n, video_t, series, timeline, fps


def panel_names(cfg):
    return [Path(p["file"]).stem for p in cfg["layout"]["panels"]]


def panel_specs(cfg, outdir=None):
    """(name, panel_cfg, size, out_path) per panel in layout order."""
    specs = []
    for p in cfg["layout"]["panels"]:
        stem = Path(p["file"]).stem
        pc = cfg["panels"][stem]
        size = (pc.get("panel_width", 576), pc.get("panel_height", 1080))
        out = Path(outdir) / p["file"] if outdir else Path(p["file"])
        specs.append((stem, pc, size, out))
    return specs


def render_panel_frames(rnd, series, timeline, video_t, fps):
    """Yield rendered PIL frames for one panel (honours freeze holds)."""
    n = len(video_t)
    for i in range(n):
        vt = video_t[i]
        j = i
        ev = timeline.active_note(vt) if timeline else None
        if ev is not None and ev.kind == "freeze":
            j = min(int(ev.time * fps), n - 1)
        yield rnd.render(j, series, vt, fps)


def encode_panel(cfg, name, panel_cfg, size, out_path, series, timeline,
                 video_t, fps):
    """Render one panel to an H.264 mp4 via an ffmpeg rawvideo pipe."""
    rnd = PanelRenderer(panel_cfg, timeline)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{size[0]}x{size[1]}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n_frames = 0
    try:
        for fr in render_panel_frames(rnd, series, timeline, video_t, fps):
            proc.stdin.write(fr.tobytes())
            n_frames += 1
        proc.stdin.close()
    except BrokenPipeError:
        pass
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed ({rc}) encoding panel {name}")
    print(f"panel {name}: {n_frames} frames -> {out_path}", file=sys.stderr)
    return out_path


def render_panels(cfg, outdir=None):
    """Render every panel stream declared in the layout."""
    session, n, video_t, series, timeline, fps = prepare_run(cfg)
    if outdir:
        Path(outdir).mkdir(parents=True, exist_ok=True)
    outs = []
    for name, pc, size, out in panel_specs(cfg, outdir):
        outs.append(encode_panel(cfg, name, pc, size, out, series, timeline,
                                 video_t, fps))
    return outs


def sample_snapshots(cfg, times, out_prefix="sample"):
    """Render one PNG snapshot per panel per requested video time."""
    session, n, video_t, series, timeline, fps = prepare_run(cfg)
    outs = []
    for name, pc, size, _ in panel_specs(cfg):
        rnd = PanelRenderer(pc, timeline)
        for t in times:
            i = min(int(t * fps), n - 1)
            j = i
            ev = timeline.active_note(video_t[i]) if timeline else None
            if ev is not None and ev.kind == "freeze":
                j = min(int(ev.time * fps), n - 1)
            img = rnd.render(j, series, video_t[i], fps)
            out = f"{out_prefix}_{name}_{t:g}s.png"
            img.save(out)
            print(out, file=sys.stderr)
            outs.append(out)
    return outs
