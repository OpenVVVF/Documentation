#!/usr/bin/env python3
"""OpenVVVF wordmark generator (deterministic, font-based).

Typesets "OpenVVVF" in Saira 900 Italic with tightened tracking and extra
lean, then adds the signature underline bars with analytically-derived
geometry:

  - left bar start:  O's left edge extended down its slope to bar level
  - gap:             symmetric around the p's descender stem
  - right bar end:   F's top-right corner projected down the italic angle
  - bar end slopes:  collinear with the letter edges

Usage:
    python openvvvf_wordmark_gen.py --png logo.png --width 2048
    python openvvvf_wordmark_gen.py --png logo.png --width 1024 --transparent
    python openvvvf_wordmark_gen.py --png logo.png --color "#FC0F27"
"""
import argparse
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "openvvvf-brand-fonts", "Saira-Italic-900.ttf")

TEXT = "OpenVVVF"
RED = "#FC0F27"
ITALIC_ANGLE = 12.0        # Saira italic, degrees
EXTRA_SHEAR = 0.15         # additional lean
TOTAL_SLANT = math.tan(math.radians(ITALIC_ANGLE)) + EXTRA_SHEAR
TRACK = -0.035             # em, general tracking
TRACK_AFTER_O = -0.03      # em, extra O->p tightening
BAR_HEIGHT_FRAC = 0.38     # of p descender drop
GAP_PAD_FRAC = 0.012       # symmetric gap padding, fraction of text width


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def build_mask(px=800):
    """Typeset + shear the wordmark; return (mask, geometry)."""
    f = ImageFont.truetype(FONT_PATH, px)
    tmp = Image.new("L", (px * 9, int(px * 2.2)), 0)
    d = ImageDraw.Draw(tmp)
    x = 100
    for i, ch in enumerate(TEXT):
        d.text((x, 100), ch, font=f, fill=255)
        adv = d.textlength(ch, font=f)
        x += adv + TRACK * px + (TRACK_AFTER_O * px if i == 0 else 0)
    a = np.array(tmp) > 127
    ys, xs = np.where(a)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

    # extra lean (top shifts right, nothing clipped)
    h, w = a.shape
    dx = int(EXTRA_SHEAR * h)
    im = Image.fromarray((a * 255).astype("uint8")).transform(
        (w + dx, h), Image.AFFINE, (1, EXTRA_SHEAR, -dx, 0, 1, 0),
        resample=Image.BICUBIC)
    a = np.array(im) > 127
    ys, xs = np.where(a)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    H, W = a.shape

    # ---- geometry ----
    rowsum = a.sum(axis=1)
    baseline = np.where(rowsum > rowsum.max() * 0.15)[0].max()
    desc = a[baseline + 2:, :]
    dys, dxs = np.where(desc)
    p_bottom = baseline + 2 + dys.max()

    # p stem edges at descender bottom
    stem_cols = np.where(desc[max(0, desc.shape[0] - 8):, :].any(axis=0))[0]
    st_l, st_r = stem_cols.min(), stem_cols.max()

    # O left edge: fit contour over its straight run
    yl, xl = [], []
    for yy in range(int(H * 0.25), int(H * 0.70)):
        row = np.where(a[yy, :int(W * 0.2)])[0]
        if len(row):
            yl.append(yy)
            xl.append(row.min())
    sO, iO = np.polyfit(yl, xl, 1)

    # F top-right corner, projected down the italic angle
    ys_all, xs_all = np.where(a)
    x_max = xs_all.max()
    y_at = ys_all[xs_all.argmax()]

    geo = dict(baseline=baseline, p_bottom=p_bottom,
               st_l=st_l, st_r=st_r, sO=sO, iO=iO,
               x_max=x_max, y_at=y_at)
    return a, geo


def render_png(path, width=None, height=None, color=RED,
               background=None, transparent=False):
    a, g = build_mask()
    H, W = a.shape
    full_W = W / 0.995          # mask occupies ~full width; keep proportions
    # bar geometry in mask coords
    drop = g["p_bottom"] - g["baseline"]
    bar_h = int(drop * BAR_HEIGHT_FRAC)
    pad = int(GAP_PAD_FRAC * W)
    X_L0 = g["sO"] * g["p_bottom"] + g["iO"]
    X_L1 = g["st_l"] - pad
    X_R0 = g["st_r"] + pad
    X_R1 = g["x_max"] - TOTAL_SLANT * (g["p_bottom"] - g["y_at"])
    sl = TOTAL_SLANT * bar_h

    ML, MT = int(0.035 * W), int(0.06 * H)
    canvas_w = int(ML + W + sl + 0.035 * W)
    canvas_h = int(MT + H + 0.09 * H)

    def draw(scale=1.0):
        cw, chh = int(canvas_w * scale), int(canvas_h * scale)
        m = Image.fromarray((a * 255).astype("uint8")).resize(
            (int(W * scale), int(H * scale)), Image.LANCZOS)
        mm = np.array(m) > 127
        img = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
        ia = np.array(img)
        ia[int(MT * scale):int(MT * scale) + int(H * scale),
           int(ML * scale):int(ML * scale) + int(W * scale)][mm] = \
            _hex(color) + (255,)
        img = Image.fromarray(ia)
        dd = ImageDraw.Draw(img)
        yb = (MT + g["p_bottom"]) * scale
        yt = yb - bar_h * scale
        sl_s = sl * scale

        def bar(xa, xb):
            dd.polygon([(xa + sl_s, yt), (xb + sl_s, yt), (xb, yb), (xa, yb)],
                       fill=_hex(color) + (255,))
        bar((ML + X_L0) * scale, (ML + X_L1) * scale)
        bar((ML + X_R0) * scale, (ML + X_R1) * scale)
        return img

    SS = 4
    base_w = width or 2048
    scale = (base_w * SS) / canvas_w
    img = draw(scale)
    if height and not width:
        base_w = int(canvas_w * (height * SS) / canvas_h)
    img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)
    if width and height:
        img = img.resize((width, height), Image.LANCZOS)
    if background and not transparent:
        bg = Image.new("RGBA", img.size, _hex(background) + (255,))
        img = Image.alpha_composite(bg, img).convert("RGB")
    img.save(path)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="OpenVVVF wordmark generator")
    ap.add_argument("--png", required=True, help="output PNG path")
    ap.add_argument("--width", type=int, help="output width (px)")
    ap.add_argument("--height", type=int, help="output height (px)")
    ap.add_argument("--color", default=RED, help="logo color hex")
    ap.add_argument("--background", default=None, help="background hex")
    ap.add_argument("--transparent", action="store_true")
    args = ap.parse_args()
    print("wrote", render_png(args.png, args.width, args.height,
                              args.color, args.background, args.transparent))
