from PIL import Image

from telemetry_overlay.panel import PanelRenderer
from telemetry_overlay.timeline import Timeline


def test_render_smoke(run_config, tiny_series):
    import json
    from telemetry_overlay import render_run
    cfg = json.loads(run_config.read_text())
    n = 80
    video_t = [(i + 0.5) / 10 for i in range(n)]
    for name, pc in cfg["panels"].items():
        render_run.resolve_auto_scales(pc, tiny_series)
        rnd = PanelRenderer(pc, Timeline.from_dicts(cfg["timeline"]))
        # a normal frame
        img = rnd.render(10, tiny_series, video_t[10], 10)
        assert img.mode == "RGB"
        assert img.size == (pc["panel_width"], pc["panel_height"])
        # a frame during the freeze window -> note card overlay path
        img = rnd.render(45, tiny_series, video_t[45], 10)
        assert isinstance(img, Image.Image)


def test_render_no_widgets():
    rnd = PanelRenderer({"panel_width": 200, "panel_height": 300,
                         "widgets": []})
    img = rnd.render(0, {}, 0.0, 15)
    assert img.size == (200, 300)
