"""OpenVVVF brand: colours, fonts, wordmarks, sponsor strips, watermark.

All brand assets ship inside the package (telemetry_overlay/assets/) so
the tool works identically anywhere it is installed:

  assets/fonts/        Saira 400/600/700/900 + Italic 600/700/900
  assets/wordmark-red.png    OpenVVVF wordmark (brand red, transparent)
  assets/logo-bw.png / logo-grey.png           monochrome wordmarks
  assets/sponsors/     mitsubishi-electric.png, mouser.png, scs-white.png

The white wordmark does not exist as a repo file; it is derived in
memory from the red wordmark (RGB replaced with white, alpha kept).

Palatte constants come from the OpenVVVF wordmark red and the existing
dark F1 dash look.
"""
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parent / "assets"
FONT_DIR = ASSETS / "fonts"
SPONSOR_DIR = ASSETS / "sponsors"

# ---- palette (dark F1 dash + OpenVVVF accent red) ----
_BG = (14, 14, 18)
BG = _BG
TRACK = (22, 22, 28)
WHITE = (240, 240, 244)
GREY = (140, 140, 150)
DIMGREY = (80, 80, 90)
RED = (225, 30, 45)      # OpenVVVF wordmark red
GREEN = (60, 220, 110)
CYAN = (60, 200, 235)
AMBER = (255, 170, 40)
ORANGE = (255, 110, 30)
NAMED = {
    "white": WHITE, "grey": GREY, "red": RED, "green": GREEN,
    "cyan": CYAN, "amber": AMBER, "orange": ORANGE,
}

# ---- fonts ----
FONT_FILES = {
    "regular": FONT_DIR / "Saira-400.ttf",
    "semibold": FONT_DIR / "Saira-600.ttf",
    "bold": FONT_DIR / "Saira-700.ttf",
    "black": FONT_DIR / "Saira-900.ttf",
    "semibold_italic": FONT_DIR / "Saira-Italic-600.ttf",
    "bold_italic": FONT_DIR / "Saira-Italic-700.ttf",
    "black_italic": FONT_DIR / "Saira-Italic-900.ttf",
}

WORDMARK_RED = ASSETS / "wordmark-red.png"
WORDMARK_BW = ASSETS / "logo-bw.png"
WORDMARK_GREY = ASSETS / "logo-grey.png"

SPONSOR_FILES = {
    "mitsubishi-electric": SPONSOR_DIR / "mitsubishi-electric.png",
    "mouser": SPONSOR_DIR / "mouser.png",
    "scs": SPONSOR_DIR / "scs-white.png",
}

_wordmark_cache = {}


def col(c, default=WHITE):
    if c is None:
        return default
    if isinstance(c, str):
        return NAMED.get(c.lower(), default)
    return tuple(c)


def wordmark(variant="white"):
    """OpenVVVF wordmark as a PIL RGBA image.

    variant: 'red' | 'grey' | 'white' (white is derived from the red
    wordmark by recolouring opaque pixels; alpha is preserved).
    """
    if variant not in _wordmark_cache:
        if variant == "red":
            im = Image.open(WORDMARK_RED).convert("RGBA")
        elif variant == "grey":
            im = Image.open(WORDMARK_GREY).convert("RGBA")
        elif variant == "white":
            im = Image.open(WORDMARK_RED).convert("RGBA")
            px = im.load()
            for y in range(im.height):
                for x in range(im.width):
                    r, g, b, a = px[x, y]
                    if a:
                        px[x, y] = (255, 255, 255, a)
        else:
            raise ValueError(f"unknown wordmark variant {variant!r}")
        _wordmark_cache[variant] = im
    return _wordmark_cache[variant]


def load_sponsor(name, white=False):
    """Sponsor logo RGBA image. `white` recolours opaque pixels to white
    (preserving alpha), which keeps dark logos legible on dark cards."""
    path = SPONSOR_FILES.get(name)
    if path is None or not Path(path).exists():
        raise FileNotFoundError(f"no sponsor logo for {name!r}")
    # crop to opaque alpha bbox so mixed-padding logos normalize evenly
    im = Image.open(path).convert("RGBA")
    bbox = im.split()[3].getbbox()
    if bbox:
        im = im.crop(bbox)
    if white:
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a:
                    px[x, y] = (255, 255, 255, a)
    return im


def _fit_height(im, height):
    w = max(1, round(im.width * height / im.height))
    return im.resize((w, height), Image.LANCZOS)


def sponsor_strip(names, height=64, gap=56, pad=10, white=True):
    """Single-line strip of sponsor logos, equal height, centered.

    Returns an RGBA image sized to content plus `pad` on every side.
    """
    logos = [_fit_height(load_sponsor(n, white=white), height) for n in names]
    w = sum(l.width for l in logos) + gap * (len(logos) - 1) + 2 * pad if logos else 2 * pad
    out = Image.new("RGBA", (max(w, 1), height + 2 * pad), (0, 0, 0, 0))
    x = pad
    for l in logos:
        out.alpha_composite(l, (x, pad))
        x += l.width + gap
    return out


def sponsor_wall(names, height=90, gx=80, gy=56, cols=2, pad=20, white=True):
    """Grid wall of sponsor logos, larger, for the outro card.

    Rows are centered horizontally; every logo is fit to `height`.
    Returns an RGBA image sized to content plus `pad`.
    """
    rows = [names[i:i + cols] for i in range(0, len(names), cols)]
    rows = [[_fit_height(load_sponsor(n, white=white), height) for n in r] for r in rows]
    if not rows:
        return Image.new("RGBA", (2 * pad, 2 * pad), (0, 0, 0, 0))
    widths = [r[0].width + gx * (len(r) - 1) + sum(l.width for l in r[1:]) for r in rows]
    w = max(widths) + 2 * pad
    h = len(rows) * height + gy * (len(rows) - 1) + 2 * pad
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = pad
    for r, rw in zip(rows, widths):
        x = (w - rw) // 2
        for l in r:
            out.alpha_composite(l, (x, y))
            x += l.width + gx
        y += height + gy
    return out


def build_watermark(config):
    """Full-canvas RGBA watermark image: white wordmark + 'TEST <number>'
    at ~35% opacity, top-left of the video box (not over the panels).
    """
    from PIL import ImageDraw, ImageFont

    lay = config.get("layout", {})
    cw = lay.get("canvas_w", 1920)
    ch = lay.get("canvas_h", 1080)
    vw = lay.get("video_width", 1344)
    vx = lay.get("video_x", (cw - vw) // 2)
    test_number = config.get("test", {}).get("number", "")
    opacity = config.get("brand", {}).get("watermark_opacity", 0.35)
    a = round(255 * opacity)

    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    mark_h = 26
    mark = _fit_height(wordmark("white"), mark_h)
    # fade the mark to the desired opacity
    mk = mark.copy()
    alpha = mk.split()[3].point(lambda v: v * a // 255)
    mk.putalpha(alpha)

    d = ImageDraw.Draw(img)
    x0, y0 = vx + 20, 20
    img.alpha_composite(mk, (x0, y0))
    if test_number:
        f = ImageFont.truetype(str(FONT_FILES["semibold"]), 24)
        tx = x0 + mk.width + 16
        ty = y0 + mark_h // 2
        d.text((tx, ty), f"TEST {test_number}", font=f, fill=(255, 255, 255, a),
               anchor="lm")
    return img
