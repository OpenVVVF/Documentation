from telemetry_overlay import brand


def test_wordmark_variants():
    for v in ("white", "red", "grey"):
        im = brand.wordmark(v)
        assert im.mode == "RGBA" and im.width > 0
    # the white variant is white where opaque
    im = brand.wordmark("white").resize((80, 16))
    px = [p for p in im.getdata() if p[3] > 200]
    assert px and all(p[0] == 255 and p[1] == 255 and p[2] == 255 for p in px)


def test_sponsor_strip_and_wall():
    names = ["mitsubishi-electric", "mouser", "scs"]
    strip = brand.sponsor_strip(names, height=32, gap=40, pad=8)
    assert strip.mode == "RGBA"
    assert strip.height == 32 + 16
    assert strip.width > 300
    wall = brand.sponsor_wall(names, height=40, cols=2)
    assert wall.height > 40
    # white recolour: dark mitsubishi logo is now visible (white px present)
    one = brand.load_sponsor("mitsubishi-electric", white=True)
    white_px = [p for p in one.resize((100, 30)).getdata()
                if p[3] > 200 and p[0] == 255]
    assert white_px


def test_build_watermark(run_config):
    import json
    cfg = json.loads(run_config.read_text())
    wm = brand.build_watermark(cfg)
    assert wm.mode == "RGBA"
    assert wm.size == (1280, 720)
    # some non-zero alpha (the mark is drawn somewhere on the canvas)
    alpha = wm.split()[3]
    assert max(alpha.getdata()) > 0
