#!/usr/bin/env python3
"""Deterministic OpenVVVF logo generator.

Reconstructs the logo from embedded vector outlines — no input image needed.
Outputs SVG at any size, and PNG at any resolution (Pillow only, no other deps).

Usage:
    python openvvvf_logo_gen.py --svg logo.svg
    python openvvvf_logo_gen.py --png logo.png --width 4096
    python openvvvf_logo_gen.py --svg logo.svg --png logo.png --width 1920 --height 487
    python openvvvf_logo_gen.py --png logo.png --width 2048 --color "#FC0F27"
"""
import argparse, json
from PIL import Image, ImageDraw

# Vector outlines traced from the original logo (base canvas 925x234).
# Each glyph: an outer polygon plus hole polygons (for O, e, etc.).
BASE_W, BASE_H = 925, 234
DEFAULT_COLOR = "#FC0F27"  # sampled brand red

POLYGONS = json.loads('''[{"outer":[[188,195],[833,195],[838,180],[826,180],[825,179],[822,180],[821,179],[820,180],[819,179],[818,180],[817,179],[816,180],[814,179],[813,180],[812,179],[811,180],[790,180],[789,179],[786,180],[781,179],[780,180],[774,179],[772,180],[771,179],[770,180],[769,179],[768,180],[766,179],[765,180],[761,179],[752,180],[746,179],[745,180],[726,180],[725,179],[724,180],[710,180],[709,179],[708,180],[695,180],[694,179],[693,180],[201,179],[200,180],[194,179]],"holes":[]},{"outer":[[40,195],[138,195],[143,179],[140,180],[139,179],[136,180],[135,179],[134,180],[133,179],[128,180],[127,179],[125,180],[123,179],[109,179],[108,180],[107,179],[102,180],[101,179],[100,180],[96,179],[95,180],[93,179],[92,180],[88,179],[84,180],[83,179],[78,180],[77,179],[76,180],[49,179],[47,180],[45,179],[42,185]],"holes":[]},{"outer":[[446,87],[440,83],[432,81],[411,82],[401,85],[395,89],[394,87],[396,83],[368,83],[344,152],[343,159],[370,159],[371,158],[373,159],[391,106],[395,102],[403,100],[410,101],[412,103],[411,104],[409,103],[411,105],[412,103],[414,109],[397,158],[399,159],[429,159],[431,157],[431,154],[447,109],[449,93]],"holes":[]},{"outer":[[349,88],[341,83],[330,81],[328,82],[327,81],[312,81],[300,83],[293,86],[291,85],[289,88],[281,93],[275,100],[268,112],[261,133],[261,147],[264,152],[273,158],[283,160],[319,159],[333,155],[340,135],[321,141],[298,142],[292,138],[292,130],[294,128],[297,129],[300,128],[304,130],[309,128],[310,129],[311,128],[313,129],[314,128],[321,129],[322,128],[329,129],[330,128],[337,129],[344,128],[346,126],[353,102],[352,93]],"holes":[[[323,100],[324,107],[320,114],[298,114],[297,113],[299,108],[306,99],[312,97],[318,97]]]},{"outer":[[261,91],[256,86],[250,83],[240,81],[205,82],[186,86],[148,195],[180,195],[183,187],[184,188],[183,185],[189,167],[193,160],[213,160],[229,155],[232,156],[231,155],[243,147],[254,134],[262,114],[263,96]],"holes":[[[229,99],[231,101],[230,102],[231,101],[232,102],[233,108],[229,121],[223,132],[212,141],[198,144],[197,141],[201,133],[212,100],[216,98]]]},{"outer":[[886,44],[866,44],[865,45],[864,44],[802,44],[756,159],[762,158],[763,159],[771,158],[772,159],[773,158],[774,159],[792,159],[797,149],[808,118],[810,116],[818,117],[852,116],[853,117],[855,115],[862,94],[821,94],[820,95],[818,94],[817,92],[825,71],[830,69],[835,70],[836,69],[838,70],[839,69],[840,70],[841,69],[877,69]],"holes":[]},{"outer":[[461,159],[512,159],[578,51],[579,56],[578,57],[577,79],[570,138],[570,149],[568,158],[569,159],[616,159],[683,50],[684,58],[682,69],[682,81],[674,159],[725,159],[792,44],[763,44],[761,46],[714,126],[712,124],[717,79],[718,55],[720,45],[719,44],[656,44],[628,92],[626,94],[625,93],[626,95],[608,124],[607,123],[607,112],[614,44],[552,44],[502,125],[500,123],[509,45],[508,44],[473,44],[466,102],[464,131],[462,140]],"holes":[]},{"outer":[[182,51],[177,46],[169,42],[140,39],[139,40],[116,41],[107,43],[87,53],[78,63],[73,72],[55,118],[50,134],[50,144],[53,151],[59,156],[71,160],[85,162],[106,162],[121,160],[131,157],[148,147],[160,132],[171,105],[183,70],[184,56]],"holes":[[[143,64],[146,69],[145,75],[130,116],[123,129],[118,134],[108,138],[93,137],[88,131],[89,124],[104,84],[110,72],[117,65],[127,61],[139,62]]]}]''')


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def render_png(path, width, height=None, color=DEFAULT_COLOR, background=None,
               supersample=4):
    """Render PNG. Keeps aspect ratio if only width given.
    Transparent background unless `background` (hex) is provided."""
    if height is None:
        height = round(width * BASE_H / BASE_W)
    s = supersample
    W, H = width * s, height * s
    sx, sy = W / BASE_W, H / BASE_H
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    for glyph in POLYGONS:
        d.polygon([(x * sx, y * sy) for x, y in glyph["outer"]], fill=255)
        for hole in glyph["holes"]:
            d.polygon([(x * sx, y * sy) for x, y in hole], fill=0)
    mask = mask.resize((width, height), Image.LANCZOS)
    rgb = _hex_to_rgb(color)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    img.putalpha(mask)
    solid = Image.new("RGBA", img.size, rgb + (255,))
    img = Image.composite(solid, img, mask)
    if background:
        bg = Image.new("RGBA", img.size, _hex_to_rgb(background) + (255,))
        img = Image.alpha_composite(bg, img).convert("RGB")
    img.save(path)
    return path


def render_svg(path, width=None, height=None, color=DEFAULT_COLOR,
               background=None):
    """Render a resolution-independent SVG."""
    if width is None and height is None:
        width, height = BASE_W, BASE_H
    elif height is None:
        height = round(width * BASE_H / BASE_W)
    elif width is None:
        width = round(height * BASE_W / BASE_H)

    def path_data(poly):
        return ("M" + "L".join(f"{x},{y}" for x, y in poly) + "Z")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {BASE_W} {BASE_H}">'
    ]
    if background:
        parts.append(
            f'<rect width="{BASE_W}" height="{BASE_H}" fill="{background}"/>')
    for glyph in POLYGONS:
        d = path_data(glyph["outer"]) + "".join(
            path_data(h) for h in glyph["holes"])
        parts.append(f'<path d="{d}" fill="{color}" fill-rule="evenodd"/>')
    parts.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(parts))
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="OpenVVVF logo generator")
    ap.add_argument("--svg", help="output SVG path")
    ap.add_argument("--png", help="output PNG path")
    ap.add_argument("--width", type=int, help="output width in px")
    ap.add_argument("--height", type=int, help="output height in px")
    ap.add_argument("--color", default=DEFAULT_COLOR,
                    help="logo color, hex (default %(default)s)")
    ap.add_argument("--background", default=None,
                    help="background color hex (default transparent)")
    args = ap.parse_args()
    if not args.svg and not args.png:
        ap.error("specify --svg and/or --png")
    if args.svg:
        print("wrote", render_svg(args.svg, args.width, args.height,
                                  args.color, args.background))
    if args.png:
        if not args.width and not args.height:
            args.width = BASE_W * 2
        w = args.width or round(args.height * BASE_W / BASE_H)
        print("wrote", render_png(args.png, w, args.height,
                                  args.color, args.background))
