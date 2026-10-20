import json

import numpy as np
import pytest

from telemetry_overlay import render_run
from telemetry_overlay.telemetry import Session


def test_config_load_ok(run_config):
    cfg = render_run.load_config(run_config)
    assert cfg["test"]["number"] == "OV-TEST-011"
    assert set(cfg["panels"]) == {"left", "right"}


def test_config_errors(tmp_path, session_file):
    base = json.loads((tmp_path / "nope.json").read_text()) if False else None
    cfg = {"session": str(session_file), "video": {"duration": 4.0},
           "layout": {"panels": [{"file": "left.mp4", "x": 40}]},
           "panels": {},   # no config for 'left'
           "timeline": [{"time": 1.0, "label": "x", "kind": "bogus"}]}
    with pytest.raises(ValueError) as e:
        render_run.validate_config(cfg)
    assert "panels.left" in str(e.value)
    assert "bogus" in str(e.value)

    with pytest.raises(ValueError, match="session"):
        render_run.validate_config({"layout": {"panels": []},
                                    "panels": {}})


def test_build_series(session_file):
    cfg = {
        "video": {"duration": 4.0, "offset": 0.0},
        "fps": 10,
        "signals": {
            "thr": {"source": "thr_a_norm", "resample": "median", "win": 0.2,
                    "clip": [0, 1]},
            "mph": {"source": "display_speed_mph", "resample": "nearest"},
            "iq": {"source": "cg_iq_a", "resample": "nearest", "abs": True},
            "pwr": {"mul": ["thr_a_norm", "cg_iq_a"], "resample": "nearest",
                    "scale": 0.001},
            "missing": {"source": "nope", "resample": "nearest"},
        },
        "panels": {"left": {"widgets": [
            {"type": "bar", "signal": "iq", "max": "auto"},
            {"type": "graphs", "graphs": [
                {"signal": "iq", "min": "auto", "max": "auto"}]},
        ]}},
    }
    session = Session(session_file)
    n, video_t, telem_t = render_run.build_grid(cfg)
    assert n == 40
    series = render_run.build_series(cfg, session, telem_t)
    assert "missing" not in series
    assert len(series["mph"]) == n
    assert np.all(series["iq"] >= 0)          # abs applied
    assert np.all((series["thr"] >= 0) & (series["thr"] <= 1))  # clip
    # auto scaling resolved from data, not left as the string
    widgets = cfg["panels"]["left"]["widgets"]
    assert isinstance(widgets[0]["max"], float)
    assert isinstance(widgets[1]["graphs"][0]["max"], float)
    assert widgets[0]["max"] > 0


def test_panel_specs(run_config):
    cfg = render_run.load_config(run_config)
    specs = render_run.panel_specs(cfg)
    assert [s[0] for s in specs] == ["left", "right"]
    assert specs[0][2] == (400, 720)
