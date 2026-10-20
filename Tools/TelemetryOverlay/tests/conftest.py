"""Shared fixtures: a tiny synthetic telemetry session + run config."""
import json

import numpy as np
import pytest


@pytest.fixture()
def session_file(tmp_path):
    """A few telemetry lines + signal_definition lines (which must be
    ignored), including None and non-finite values to exercise cleaning."""
    rows = [
        {"type": "session_start", "started_at_utc": "2026-10-16T18:17:05Z"},
        {"type": "signal_definition", "name": "thr_a_norm", "unit": "1"},
        {"type": "signal_definition", "name": "display_speed_mph", "unit": "mph"},
        {"type": "telemetry", "t": 0.0,
         "values": {"thr_a_norm": 0.0, "display_speed_mph": 0.0, "cg_iq_a": None}},
        {"type": "telemetry", "t": 1.0,
         "values": {"thr_a_norm": 0.5, "display_speed_mph": 12.0, "cg_iq_a": 40.0}},
        {"type": "telemetry", "t": 2.0,
         "values": {"thr_a_norm": float("nan"), "display_speed_mph": 23.0,
                    "cg_iq_a": -90.0}},
        {"type": "telemetry", "t": 3.0,
         "values": {"thr_a_norm": 1.0, "display_speed_mph": float("inf"),
                    "cg_iq_a": 0000.0}},
        {"type": "telemetry", "t": 4.0,
         "values": {"thr_a_norm": 0.8, "display_speed_mph": 31.0, "cg_iq_a": 55.0}},
    ]
    p = tmp_path / "session.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return p


@pytest.fixture()
def run_config(tmp_path, session_file):
    cfg = {
        "test": {"number": "OV-TEST-011", "title": "Gen7 dyno shakedown",
                 "description": "First full-power pull of the Gen 7 stack "
                                "with the new gate drivers and DC link.",
                 "date": "2026-10-16"},
        "brand": {"watermark": True,
                  "sponsors": ["mitsubishi-electric", "mouser", "scs"],
                  "intro_s": 5.0, "outro_s": 4.0},
        "session": str(session_file),
        "video": {"duration": 8.0, "offset": 1.0},
        "fps": 10,
        "layout": {"canvas_w": 1280, "canvas_h": 720,
                   "video_width": 400, "video_height": 720,
                   "panels": [{"file": "left.mp4", "x": 40},
                              {"file": "right.mp4", "x": 920}]},
        "signals": {
            "thr": {"source": "thr_a_norm", "resample": "median",
                    "win": 0.2, "clip": [0, 1]},
            "mph": {"source": "display_speed_mph", "resample": "nearest"},
            "iq": {"source": "cg_iq_a", "resample": "nearest", "abs": True},
            "pwr": {"mul": ["thr_a_norm", "cg_iq_a"], "resample": "nearest",
                    "scale": 0.001},
        },
        "panels": {
            "left": {"panel_width": 400, "panel_height": 720, "widgets": [
                {"type": "header", "y": 22, "show_dot": False},
                {"type": "bigvalue", "y": 80, "signal": "mph",
                 "label": "SPEED", "unit": "mph", "size": 120},
                {"type": "bar", "y": 260, "signal": "thr", "label": "THROTTLE",
                 "max": 1, "value_scale": 100, "value_format": "{:.0f}%",
                 "color": "green"},
                {"type": "bar", "y": 340, "signal": "iq", "label": "PHASE",
                 "max": "auto", "zero_center": True},
            ]},
            "right": {"panel_width": 400, "panel_height": 720, "widgets": [
                {"type": "header", "y": 22, "title": "GEN7", "subtitle": "dyno"},
                {"type": "statsrow", "y": 120, "items": [
                    {"label": "PWR", "signal": "pwr", "format": "{:.1f} kW"},
                    {"label": "IQ", "signal": "iq", "format": "{:.0f} A"},
                ]},
                {"type": "tempbars", "y": 220, "label": "TEMPS", "max": 80,
                 "signals": ["iq", "mph"], "names": ["A", "B"]},
                {"type": "graphs", "y": 420, "h": 200, "window_s": 5,
                 "graphs": [{"signal": "thr", "min": 0, "max": 1,
                             "color": "cyan"},
                            {"signal": "mph", "min": 0, "max": "auto",
                             "color": "red"}]},
            ]},
        },
        "timeline": [
            {"time": 2.0, "label": "spike", "kind": "marker"},
            {"time": 4.0, "label": "overcurrent spike", "kind": "freeze",
             "duration": 2.0, "text": "Phase current hit the limit here."},
        ],
    }
    p = tmp_path / "run.json"
    p.write_text(json.dumps(cfg))
    return p


@pytest.fixture()
def tiny_series():
    n = 80
    return {
        "mph": np.linspace(0, 30, n),
        "thr": np.clip(np.linspace(-0.5, 1.5, n), -1, 1),
        "iq": np.linspace(-90, 55, n),
        "pwr": np.linspace(-5, 40, n),
        "vdc": np.full(n, 400.0),
        "t1": np.linspace(20, 70, n),
    }
