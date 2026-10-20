"""Branded intro / outro title cards.

Intro (float intro_s seconds, default 5.0):
  phase 1 (~40%): the white OpenVVVF wordmark fades in at center on a
      near-black background;
  phase 2 (~60%): the wordmark moves up and the TEST number (big Saira
      Italic 900), title, wrapped description, date, and a single-line
      sponsor strip fade in beneath it.

Outro (brand.outro_s, default 4.0): dark background, a larger sponsor
wall (logo grid), then the OpenVVVF wordmark with the test number
small beneath. Ends with a fade to black.

Frames are generated in PIL (alpha fades, no ffmpeg-only fades) at the
config fps, and encoded to canvas-sized mp4 with a silent AAC track so
the composer can concat intro + main + outro in one pass. Card videos
are cached in `_brand_cache/` under the working directory, keyed by a
hash of the test/brand/fps/canvas config.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import brand


def _fonts():
    def f(key, size):
        return ImageFont.truetype(str(brand.FONT_FILES[key]), size)
    return f


def _fade(img, layer, alpha):
    """Alpha-composite `layer` onto `img` (both RGBA) with global alpha."""
    if alpha <= 0.0:
        return
    if alpha < 1.0:
        layer = layer.copy()
        layer.putalpha(layer.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(layer)


def _fit_width(im, maxw):
    if im.width <= maxw:
        return im
    h = max(1, round(im.height * maxw / im.width))
    return im.resize((maxw, h), Image.LANCZOS)


class _CardLayer:
    """A sized RGBA layer with its draw context, positioned on the canvas."""

    def __init__(self, cw, ch):
        self.img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.cw, self.ch = cw, ch


def build_intro_frames(config):
    """Yield canvas-sized RGB frames for the intro card."""
    f = _fonts()
    lay = config.get("layout", {})
    cw = lay.get("canvas_w", 1920)
    ch = lay.get("canvas_h", 1080)
    fps = float(config.get("fps", 15))
    test = config.get("test", {})
    brand_cfg = config.get("brand", {})
    dur = float(brand_cfg.get("intro_s", 5.0))
    sponsors = brand_cfg.get("sponsors", [])
    scale = ch / 1080.0

    n = max(2, round(dur * fps))
    p1 = 0.4  # share of intro spent on the wordmark-only phase

    # logo layer (per-frame height differs, rebuilt cheaply each frame)
    mark = brand.wordmark("white")

    # texts layer (static content, fades in as one group, staggered below)
    texts = _CardLayer(cw, ch)
    number = test.get("number", "")
    title = test.get("title", "")
    desc = test.get("description", "")
    date = test.get("date", "")
    center_x = cw // 2

    y_num = int(ch * 0.52)
    if number:
        texts.d.text((center_x, y_num), f"TEST {number}",
                     font=f("black_italic", int(96 * scale)),
                     fill=(255, 255, 255, 255), anchor="ma")
    if title:
        texts.d.text((center_x, y_num + int(110 * scale)), title.upper(),
                     font=f("black", int(52 * scale)),
                     fill=brand.RED + (255,), anchor="ma")
    if desc:
        maxw = cw - int(2 * 140 * scale)
        font_d = f("semibold", int(30 * scale))
        lines = []
        cur = ""
        for wd in desc.split():
            trial = (cur + " " + wd).strip()
            if cur and texts.d.textlength(trial, font=font_d) > maxw:
                lines.append(cur)
                cur = wd
            else:
                cur = trial
        if cur:
            lines.append(cur)
        n_lines_used = min(len(lines), 4)
        for k, ln in enumerate(lines[:4]):
            texts.d.text((center_x, y_num + int(180 * scale) + k * int(42 * scale)),
                         ln, font=font_d, fill=brand.GREY + (255,), anchor="ma")
    else:
        n_lines_used = 0
    if date:
        y_date = y_num + int(180 * scale) + n_lines_used * int(42 * scale) + int(30 * scale)
        texts.d.text((center_x, y_date), date, font=f("semibold", int(30 * scale)),
                     fill=brand.WHITE + (230,), anchor="ma")

    # sponsor strip layer
    strip = None
    if sponsors:
        strip = brand.sponsor_strip(sponsors, height=int(40 * scale),
                                    gap=int(72 * scale), pad=int(12 * scale),
                                    white=True)
        strip = _fit_width(strip, cw - int(2 * 100 * scale))

    for i in range(n):
        t = i / max(n - 1, 1)  # 0..1 across the card
        img = Image.new("RGBA", (cw, ch), brand.BG + (255,))
        # wordmark: fade in during phase 1, then drift up to its phase-2 spot
        if t < p1:
            p = t / p1
            alpha = min(1.0, p * 1.5)
            cy = ch * 0.5
        else:
            p = (t - p1) / (1.0 - p1)
            alpha = 1.0
            ease = min(1.0, p * 2.5)
            cy = ch * 0.5 - (ch * 0.5 - ch * 0.28) * ease
            # phase 2 content fades in staggered
            a2 = min(1.0, max(0.0, (p - 0.15) * 3.0))
            _fade(img, texts.img, a2)
            if strip is not None:
                a3 = min(1.0, max(0.0, (p - 0.4) * 3.0))
                sl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
                sy = ch - strip.height - int(56 * scale)
                sl.alpha_composite(strip, ((cw - strip.width) // 2, sy))
                _fade(img, sl, a3)
        mh = int(120 * scale * (1.25 - 0.25 * (max(0.0, t - p1) / (1.0 - p1)))
                 ) if t >= p1 else int(120 * scale * 1.25)
        m = brand._fit_height(mark, mh)
        lay_logo = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        lay_logo.alpha_composite(m, (center_x - m.width // 2,
                                     int(cy - m.height / 2)))
        _fade(img, lay_logo, alpha)
        yield img.convert("RGB")


def build_outro_frames(config):
    """Yield canvas-sized RGB frames for the outro card."""
    f = _fonts()
    lay = config.get("layout", {})
    cw = lay.get("canvas_w", 1920)
    ch = lay.get("canvas_h", 1080)
    fps = float(config.get("fps", 15))
    test = config.get("test", {})
    brand_cfg = config.get("brand", {})
    dur = float(brand_cfg.get("outro_s", 4.0))
    sponsors = brand_cfg.get("sponsors", [])
    scale = ch / 1080.0

    n = max(2, round(dur * fps))
    center_x = cw // 2

    wall = None
    if sponsors:
        wall = brand.sponsor_wall(sponsors, height=int(84 * scale),
                                  gx=int(110 * scale), gy=int(64 * scale),
                                  cols=2, pad=int(20 * scale), white=True)
        wall = _fit_width(wall, cw - int(2 * 160 * scale))

    mark = brand._fit_height(brand.wordmark("white"), int(88 * scale))

    static = Image.new("RGBA", (cw, ch), brand.BG + (255,))
    if wall is not None:
        static.alpha_composite(wall, (center_x - wall.width // 2,
                                      int(ch * 0.30 - wall.height / 2)))
    my = int(ch * 0.68)
    static.alpha_composite(mark, (center_x - mark.width // 2, my))
    d = ImageDraw.Draw(static)
    number = test.get("number", "")
    if number:
        d.text((center_x, my + mark.height + int(26 * scale)),
               f"TEST {number}", font=f("semibold", int(30 * scale)),
               fill=brand.GREY + (255,), anchor="ma")

    for i in range(n):
        t = i / max(n - 1, 1)
        img = static.copy()
        # fade in over the first 20%, fade to black over the last 20%
        alpha = min(1.0, t / 0.2) if t < 0.2 else 1.0
        if t > 0.8:
            alpha = max(0.0, (1.0 - t) / 0.2)
        if alpha < 1.0:
            black = Image.new("RGBA", (cw, ch), (0, 0, 0, 255))
            img = Image.blend(black.convert("RGB").convert("RGBA"), img, alpha)
        yield img.convert("RGB")


def brand_key(config):
    """Stable hash of everything that determines card/watermark content."""
    lay = config.get("layout", {})
    payload = {
        "test": config.get("test", {}),
        "brand": config.get("brand", {}),
        "fps": config.get("fps", 15),
        "canvas": [lay.get("canvas_w", 1920), lay.get("canvas_h", 1080)],
    }
    return hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]


def cache_dir(config):
    return Path.cwd() / "_brand_cache"


def _encode_frames(frames, n_frames, fps, size, out_path):
    """Pipe RGB frames to ffmpeg, attach a silent stereo AAC track."""
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{size[0]}x{size[1]}", "-r", str(fps), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-t", f"{n_frames / fps:.4f}",
        "-movflags", "+faststart", str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for fr in frames:
            proc.stdin.write(fr.tobytes())
        proc.stdin.close()
    except BrokenPipeError:
        pass
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed ({rc}) encoding {out_path}")


def ensure_card(config, kind):
    """Build or fetch the cached intro/outro mp4. Returns its Path."""
    assert kind in ("intro", "outro")
    cache = cache_dir(config)
    cache.mkdir(exist_ok=True)
    path = cache / f"{kind}-{brand_key(config)}.mp4"
    if path.exists():
        print(f"{kind}: cached {path}", file=sys.stderr)
        return path
    lay = config.get("layout", {})
    size = (lay.get("canvas_w", 1920), lay.get("canvas_h", 1080))
    fps = float(config.get("fps", 15))
    frames = list((build_intro_frames if kind == "intro"
                   else build_outro_frames)(config))
    print(f"{kind}: encoding {len(frames)} frames -> {path}", file=sys.stderr)
    _encode_frames(iter(frames), len(frames), fps, size, path)
    return path
