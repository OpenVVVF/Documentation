#!/usr/bin/env python3
"""OpenVVVF icon / favicon generator (deterministic).

Renders the "OV" monogram icon: brand-red rounded square, white italic
monogram in Saira 900 Italic with the wordmark's extra lean, plus the
signature slanted underline bar. Outputs PNG (any size), multi-size ICO,
and a true-vector SVG (glyph outlines baked to paths, no font needed to
view).

Usage:
    python openvvvf_icon_gen.py --png icon.png --size 512
    python openvvvf_icon_gen.py --ico favicon.ico
    python openvvvf_icon_gen.py --svg icon.svg
    python openvvvf_icon_gen.py --set icons/          # full web favicon set
    python openvvvf_icon_gen.py --png icon.png --size 512 --transparent
"""
import argparse
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "openvvvf-brand-fonts", "Saira-Italic-900.ttf")

RED = (252, 15, 39)
MONOGRAM = "OV"
ITALIC_ANGLE = 12.0        # Saira italic, degrees
EXTRA_SHEAR = 0.15         # additional lean, matches the wordmark
TOTAL_SLANT = math.tan(math.radians(ITALIC_ANGLE)) + EXTRA_SHEAR
TRACK = -0.02              # em, letter tracking
TEXT_WIDTH_FRAC = 0.58     # monogram width as fraction of icon
RADIUS_FRAC = 0.20         # corner radius


def _hex(c):
    return "#%02X%02X%02X" % c


# ---------------------------------------------------------------- raster --

def _text_mask(f, ref_px):
    """Render monogram with tracking + extra shear; return boolean mask."""
    tmp = Image.new("L", (ref_px * 3, ref_px * 2), 0)
    d = ImageDraw.Draw(tmp)
    x = 100
    for ch in MONOGRAM:
        d.text((x, 100), ch, font=f, fill=255)
        x += d.textlength(ch, font=f) + TRACK * ref_px
    m = np.array(tmp) > 127
    ys, xs = np.where(m)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = m.shape
    dx = int(EXTRA_SHEAR * h)
    tm = Image.fromarray((m * 255).astype("uint8")).transform(
        (w + dx, h), Image.AFFINE, (1, EXTRA_SHEAR, -dx, 0, 1, 0),
        resample=Image.BICUBIC)
    a = np.array(tm) > 127
    ys, xs = np.where(a)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def render_png(path, size, bg=RED, fg=(255, 255, 255), transparent=False):
    SS = 8  # supersampling factor
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if not transparent:
        d.rounded_rectangle([0, 0, S - 1, S - 1],
                            radius=int(S * RADIUS_FRAC), fill=bg + (255,))
    f = ImageFont.truetype(FONT_PATH, int(S * 0.52))
    a = _text_mask(f, S)
    th, tw = a.shape
    scale = (S * TEXT_WIDTH_FRAC) / tw
    tw2, th2 = int(tw * scale), int(th * scale)
    tm = np.array(Image.fromarray((a * 255).astype("uint8"))
                  .resize((tw2, th2), Image.LANCZOS)) > 127

    bar_h = max(int(th2 * 0.14), SS)
    sl = TOTAL_SLANT * bar_h
    gap = int(S * 0.02)
    total_h = th2 + gap + bar_h
    ox, oy = (S - tw2) // 2, (S - total_h) // 2 + int(S * 0.02)

    # --- analytic bar endpoints (measured on the sheared text mask) ---
    yb_rel = th + gap + bar_h                     # bar bottom, mask coords
    # left edge: fit the O's left contour over its straight run
    yl, xl = [], []
    for yy in range(int(th * 0.20), int(th * 0.80)):
        row = np.where(a[yy, :int(tw * 0.35)])[0]
        if len(row):
            yl.append(yy)
            xl.append(row.min())
    sO, iO = np.polyfit(yl, xl, 1)
    x_start = sO * yb_rel + iO
    # right edge: fit the V's right contour over its full straight run
    yr, xr = [], []
    for yy in range(int(th * 0.10), int(th * 0.80)):
        row = np.where(a[yy, int(tw * 0.5):])[0]
        if len(row):
            yr.append(yy)
            xr.append(row.max() + int(tw * 0.5))
    sV, iV = np.polyfit(yr, xr, 1)
    x_end = sV * yb_rel + iV

    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    la = np.array(layer)
    la[oy:oy + th2, ox:ox + tw2][tm] = fg + (255,)
    layer = Image.fromarray(la)
    dl = ImageDraw.Draw(layer)
    yb, yt = oy + th2 + gap + bar_h, oy + th2 + gap
    x0, x1 = ox + x_start * scale, ox + x_end * scale
    # bar ends collinear with the letter edges (same slope, not just italic)
    slL = -sO * bar_h
    slR = -sV * bar_h
    dl.polygon([(x0 + slL, yt), (x1 + slR, yt),
                (x1, yb), (x0, yb)], fill=fg + (255,))
    img = Image.alpha_composite(img, layer)
    img.resize((size, size), Image.LANCZOS).save(path)
    return path


def render_ico(path, bg=RED, fg=(255, 255, 255)):
    sizes = (16, 24, 32, 48, 64)
    frames = []
    for s in sizes:
        tmp = path + f".tmp{s}.png"
        render_png(tmp, s, bg, fg)
        frames.append(Image.open(tmp).copy())
        os.remove(tmp)
    frames[0].save(path, format="ICO",
                   sizes=[(f.width, f.height) for f in frames])
    return path


# ---------------------------------------------------------------- vector --

def render_svg(path, size=512, bg=RED, fg=(255, 255, 255),
               transparent=False):
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.misc.transform import Transform

    ft = TTFont(FONT_PATH)
    gs = ft.getGlyphSet()
    cmap = ft.getBestCmap()
    upm = ft["head"].unitsPerEm

    from fontTools.pens.recordingPen import RecordingPen

    glyphs = []          # (glyph, recording, x offset) in font units, y-up
    x_off = 0.0
    for ch in MONOGRAM:
        g = gs[cmap[ord(ch)]]
        rp = RecordingPen()
        g.draw(rp)
        glyphs.append((g, rp.value, x_off))
        x_off += g.width + TRACK * upm

    # sheared coordinates (lean right at top, y-up): xs = x + EXTRA_SHEAR*y
    def sheared_pts(rec, go):
        pts = []
        for op, pps in rec:
            for (px, py) in pps:
                pts.append((px + go + EXTRA_SHEAR * py, py))
        return pts

    all_pts = [p for rec_go in glyphs for p in sheared_pts(rec_go[1], rec_go[2])]
    xmin = min(p[0] for p in all_pts)
    xmax = max(p[0] for p in all_pts)
    ymin = min(p[1] for p in all_pts)
    ymax = max(p[1] for p in all_pts)
    tw, th = xmax - xmin, ymax - ymin

    S = 512.0
    scale = (S * TEXT_WIDTH_FRAC) / tw
    tw2, th2 = tw * scale, th * scale
    bar_h = th2 * 0.14
    sl = TOTAL_SLANT * bar_h
    gap = S * 0.02
    total_h = th2 + gap + bar_h
    ox = (S - tw2) / 2
    oy = (S - total_h) / 2 + S * 0.02

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" '
           f'height="{size}" viewBox="0 0 512 512">']
    if not transparent:
        out.append(f'<rect width="512" height="512" rx="{512 * RADIUS_FRAC:.1f}" '
                   f'fill="{_hex(bg)}"/>')
    for g, rec, go in glyphs:
        # affine: font units (y-up) -> canvas (y-down), with shear + flip
        m = Transform(scale, 0, EXTRA_SHEAR * scale, -scale,
                      ox + (go - xmin) * scale, oy + ymax * scale)
        pen = SVGPathPen(gs)
        g.draw(TransformPen(pen, m))
        out.append(f'<path d="{pen.getCommands()}" fill="{_hex(fg)}"/>')

    # --- analytic bar endpoints: measure on a raster reference (same math
    # as render_png) and transfer as fractions of the text width ---
    f_ref = ImageFont.truetype(FONT_PATH, 1024)
    a = _text_mask(f_ref, 2048)
    th_r, tw_r = a.shape
    scale_r = (2048 * TEXT_WIDTH_FRAC) / tw_r
    th2_r = th_r * scale_r
    bar_h_r = th2_r * 0.14
    gap_r = 2048 * 0.02
    yb_rel = th_r + gap_r + bar_h_r
    yl, xl = [], []
    for yy in range(int(th_r * 0.20), int(th_r * 0.80)):
        row = np.where(a[yy, :int(tw_r * 0.35)])[0]
        if len(row):
            yl.append(yy)
            xl.append(row.min())
    sO, iO = np.polyfit(yl, xl, 1)
    x_start_r = sO * yb_rel + iO
    yr, xr = [], []
    for yy in range(int(th_r * 0.10), int(th_r * 0.80)):
        row = np.where(a[yy, int(tw_r * 0.5):])[0]
        if len(row):
            yr.append(yy)
            xr.append(row.max() + int(tw_r * 0.5))
    sV, iV = np.polyfit(yr, xr, 1)
    x_end_r = sV * yb_rel + iV

    x0 = ox + (x_start_r / tw_r) * tw2
    x1 = ox + (x_end_r / tw_r) * tw2
    yt, yb = oy + th2 + gap, oy + th2 + gap + bar_h
    slL, slR = -sO * bar_h, -sV * bar_h   # ends collinear with letter edges
    pts = (f"{x0 + slL:.2f},{yt:.2f} {x1 + slR:.2f},{yt:.2f} "
           f"{x1:.2f},{yb:.2f} {x0:.2f},{yb:.2f}")
    out.append(f'<polygon points="{pts}" fill="{_hex(fg)}"/>')
    out.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(out))
    return path


# ------------------------------------------------------------------- set --

def render_set(outdir, bg=RED, fg=(255, 255, 255)):
    os.makedirs(outdir, exist_ok=True)
    made = []
    made.append(render_ico(os.path.join(outdir, "favicon.ico"), bg, fg))
    for name, s in [("favicon-16x16.png", 16), ("favicon-32x32.png", 32),
                    ("apple-touch-icon.png", 180),
                    ("android-chrome-192x192.png", 192),
                    ("android-chrome-512x512.png", 512)]:
        made.append(render_png(os.path.join(outdir, name), s, bg, fg))
    made.append(render_svg(os.path.join(outdir, "icon.svg"), 512, bg, fg))
    return made


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="OpenVVVF icon generator")
    ap.add_argument("--png", help="output PNG path")
    ap.add_argument("--size", type=int, default=512, help="PNG size (px)")
    ap.add_argument("--ico", help="output ICO path (multi-size)")
    ap.add_argument("--svg", help="output SVG path")
    ap.add_argument("--set", metavar="DIR", help="write full favicon set to DIR")
    ap.add_argument("--transparent", action="store_true",
                    help="no background square (monogram + bar only)")
    ap.add_argument("--bg", default=_hex(RED), help="background hex color")
    ap.add_argument("--fg", default="#FFFFFF", help="foreground hex color")
    args = ap.parse_args()

    def parse(c):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

    bg, fg = parse(args.bg), parse(args.fg)
    if not any([args.png, args.ico, args.svg, args.set]):
        ap.error("specify --png, --ico, --svg and/or --set")
    if args.png:
        print("wrote", render_png(args.png, args.size, bg, fg,
                                  args.transparent))
    if args.ico:
        print("wrote", render_ico(args.ico, bg, fg))
    if args.svg:
        print("wrote", render_svg(args.svg, args.size, bg, fg,
                                  args.transparent))
    if args.set:
        for p in render_set(args.set, bg, fg):
            print("wrote", p)
