"""Configurable F1-style telemetry panel renderer (OpenVVVF branded).

A run config (dict / JSON file) declares the panel layout as a list of
widgets. Each widget is {"type": ..., "y": ..., ...}. Supported types:

  header     brand wordmark or title, LIVE dot, clock, next-event countdown
  bigvalue   one huge value (signal, unit, label, color-by thresholds)
  bar        label + horizontal bar (signal, max, color, segments,
             zero_center bidirectional mode)
  statsrow   row of small label/value pairs
  tempbars   stacked temperature bars (list of signals)
  graphs     one or more scrolling sparkline charts with event markers

Signals are referenced by name and resolved against a pre-resampled
dict name -> ndarray aligned to the frame grid. All geometry is in the
run config; nothing here is specific to a particular vehicle.

Fonts are the OpenVVVF brand Saira family shipped in
telemetry_overlay/assets/fonts (big numbers/titles use Saira Italic 900).
"""
import re

from . import brand
from PIL import Image, ImageDraw, ImageFont

FONTS = {
    "huge": brand.FONT_FILES["black_italic"],
    "big": brand.FONT_FILES["black_italic"],
    "med": brand.FONT_FILES["bold_italic"],
    "num": brand.FONT_FILES["bold"],
    "lbl": brand.FONT_FILES["bold"],
    "lbl2": brand.FONT_FILES["semibold"],
    "small": brand.FONT_FILES["regular"],
}

WHITE = brand.WHITE
GREY = brand.GREY
DIMGREY = brand.DIMGREY
RED = brand.RED
AMBER = brand.AMBER
GREEN = brand.GREEN
CYAN = brand.CYAN
NAMED = brand.NAMED
col = brand.col


class PanelRenderer:
    def __init__(self, config, timeline=None):
        self.cfg = config
        self.w = config.get("panel_width", 576)
        self.h = config.get("panel_height", 1080)
        self.bg = col(config.get("bg"), brand.BG)
        self.track = col(config.get("track"), brand.TRACK)
        self.accent = col(config.get("accent"), brand.RED)
        self.pad = config.get("pad", 30)
        self.timeline = timeline
        self._fonts = {}
        self._logo_cache = {}

    def font(self, key, size):
        k = (key, size)
        if k not in self._fonts:
            self._fonts[k] = ImageFont.truetype(str(FONTS[key]), size)
        return self._fonts[k]

    def render(self, frame_idx, series, video_t, fps):
        """series: signal name -> ndarray (one value per frame).
        Returns a PIL Image for this frame."""
        img = Image.new("RGB", (self.w, self.h), self.bg)
        self._img = img
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 6, self.h], fill=self.accent)
        for wcfg in self.cfg["widgets"]:
            getattr(self, "_w_" + wcfg["type"])(d, wcfg, series,
                                               frame_idx, video_t, fps)
        img = self._draw_timeline_overlays(img, series, frame_idx, video_t, fps)
        return img

    # ---------- helpers ----------
    def _val(self, series, name, i):
        a = series.get(name)
        if a is None or len(a) == 0:
            return 0.0
        return a[min(i, len(a) - 1)]

    @staticmethod
    def _fmt(fmt, v):
        # never show "-0" (with or without a unit suffix) for tiny negatives
        s = fmt.format(v)
        m = re.match(r"^-([0-9.eE]+)(\s.*)?$", s)
        if m and float(m.group(1)) == 0:
            return s[1:]
        return s

    def _header_logo(self, c):
        """Header mark: widget 'logo' path if given, else the white
        OpenVVVF wordmark from the brand assets."""
        key = c.get("logo") or "::brand-white"
        if key not in self._logo_cache:
            if c.get("logo"):
                im = Image.open(c["logo"]).convert("RGBA")
            else:
                im = brand.wordmark("white")
            self._logo_cache[key] = im
        return self._logo_cache[key]

    def _bar(self, d, y, h, frac, color, segments=None):
        x0, x1 = self.pad, self.w - self.pad
        frac = max(0.0, min(1.0, float(frac)))
        d.rectangle([x0, y, x1, y + h], fill=self.track)
        if frac > 0:
            d.rectangle([x0, y, x0 + (x1 - x0) * frac, y + h], fill=color)
        for sf in segments or []:
            x = x0 + (x1 - x0) * sf
            d.line([x, y, x, y + h], fill=self.bg, width=3)

    def _graph(self, d, x0, y0, w, h, series, name, color, vmin, vmax,
               label, markers, fps):
        d.rectangle([x0, y0, x0 + w, y0 + h], outline=DIMGREY, width=1)
        for g in (0.25, 0.5, 0.75):
            yy = y0 + h * g
            d.line([x0, yy, x0 + w, yy], fill=(35, 35, 42), width=1)
        a = series.get(name)
        if a is not None and len(a) > 1:
            n = len(a)
            rng = (vmax - vmin) or 1.0
            pts = [(x0 + w * j / (n - 1),
                    y0 + h - h * (max(vmin, min(vmax, a[j])) - vmin) / rng)
                   for j in range(n)]
            d.line(pts, fill=color, width=2)
            d.text((x0 + w - 4, y0 + 2), f"{a[-1]:.0f}", font=self.font("small", 20),
                   fill=WHITE, anchor="ra")
        # event markers (vertical ticks)
        t0 = markers.get("t0", 0.0)
        span = markers.get("span", 1.0)
        for mk in markers.get("events", []):
            fx = (mk.time - t0) / span
            if 0.0 <= fx <= 1.0:
                x = x0 + w * fx
                d.line([x, y0, x, y0 + h], fill=RED, width=2)
        d.text((x0 + 4, y0 + 2), label, font=self.font("small", 20), fill=GREY)

    # ---------- widgets ----------
    def _w_header(self, d, c, series, i, vt, fps):
        f1 = self.font("lbl", c.get("size", 24))
        f2 = self.font("lbl2", c.get("sub_size", 22))
        y = c.get("y", 22)
        x = self.pad
        logo_h = c.get("logo_height", 36)
        if not c.get("title"):
            logo = self._header_logo(c)
            lw = int(logo.width * logo_h / logo.height)
            logo = logo.resize((lw, logo_h), Image.LANCZOS)
            self._img.paste(logo, (x, y), logo)
            x += lw + 16
        else:
            title = c["title"]
            d.text((x, y), title, font=f1, fill=WHITE)
            x += int(f1.getlength(title)) + 14
        if c.get("show_dot", True):
            d.ellipse([x, y + 8, x + 14, y + 22], fill=RED)
            x += 22
        if c.get("subtitle"):
            d.text((x, y + 4), c["subtitle"], font=f2, fill=GREY)
        # clock + next-marker countdown
        m = int(vt // 60); s = vt - 60 * m
        d.text((self.w - self.pad, c.get("y", 22) + 2), f"{m:02d}:{s:04.1f}",
               font=f2, fill=GREY, anchor="ra")
        if self.timeline:
            nxt = self.timeline.upcoming_marker(vt, c.get("marker_lookahead", 5.0))
            if nxt:
                d.text((self.w - self.pad, c.get("y", 22) + 28),
                       f"▼ {nxt.label} in {nxt.time - vt:.0f}s",
                       font=f2, fill=AMBER, anchor="ra")
        d.line([self.pad, c.get("divider_y", 66), self.w - self.pad,
                c.get("divider_y", 66)], fill=DIMGREY, width=1)

    def _w_bigvalue(self, d, c, series, i, vt, fps):
        y = c.get("y", 84)
        v = self._val(series, c["signal"], i)
        d.text((self.pad, y), c.get("label", c["signal"]), font=self.font("lbl", 24), fill=GREY)
        d.text((self.w - self.pad, y + c.get("unit_drop", 34)), c.get("unit", ""),
               font=self.font("lbl", 24), fill=GREY, anchor="rs")
        color = col(c.get("color"), WHITE)
        for th, cname in sorted((c.get("color_thresholds") or {}).items(),
                                key=lambda kv: float(kv[0])):
            if v > float(th):
                color = col(cname, color)
        d.text((self.pad - 4, y + c.get("value_drop", 12)), self._fmt(c.get("format", "{:.0f}"), v),
               font=self.font("huge", c.get("size", 150)), fill=color)

    def _w_bar(self, d, c, series, i, vt, fps):
        y = c.get("y", 500)
        v = self._val(series, c["signal"], i)
        vmax = c.get("max") or 1.0
        d.text((self.pad, y), c.get("label", c["signal"]), font=self.font("lbl", 24), fill=GREY)
        color = col(c.get("color"), GREEN)
        for th, cname in sorted((c.get("color_thresholds") or {}).items(),
                                key=lambda kv: float(kv[0])):
            if v > float(th):
                color = col(cname, color)
        if c.get("value_show", True):
            d.text((self.w - self.pad, y - 6),
                   c.get("value_format", "{:.0f}").format(v * (c.get("value_scale", 1))),
                   font=self.font("med", 40), fill=color, anchor="ra")
        if c.get("zero_center"):
            # bidirectional bar: +value fills right, -value fills left
            x0, x1 = self.pad, self.w - self.pad
            xc = (x0 + x1) / 2
            d.rectangle([x0, y + c.get("bar_drop", 44), x1, y + c.get("bar_drop", 44) + c.get("bar_h", 24)],
                        fill=self.track)
            frac = max(-1.0, min(1.0, v / vmax))
            if frac >= 0:
                d.rectangle([xc, y + c.get("bar_drop", 44), xc + (x1 - xc) * frac,
                             y + c.get("bar_drop", 44) + c.get("bar_h", 24)], fill=color)
            else:
                d.rectangle([xc + (x0 - xc) * abs(frac), y + c.get("bar_drop", 44),
                             xc, y + c.get("bar_drop", 44) + c.get("bar_h", 24)],
                            fill=col(c.get("neg_color"), CYAN))
            return
        segs = [s / vmax for s in c.get("segments", [])]
        self._bar(d, y + c.get("bar_drop", 44), c.get("bar_h", 24),
                  v / vmax, color, segs)

    def _w_statsrow(self, d, c, series, i, vt, fps):
        y = c.get("y", 776)
        if c.get("divider", True):
            d.line([self.pad, y - 18, self.w - self.pad, y - 18], fill=DIMGREY, width=1)
        items = c["items"]  # list of {label, signal, format, color}
        cw = (self.w - 2 * self.pad) / len(items)
        for k, it in enumerate(items):
            x = self.pad + cw * k
            d.text((x, y), it.get("label", it["signal"]), font=self.font("small", 20), fill=GREY)
            v = self._val(series, it["signal"], i)
            d.text((x, y + 26), self._fmt(it.get("format", "{:.0f}"), v),
                   font=self.font("num", it.get("size", 34)), fill=col(it.get("color"), WHITE))

    def _w_tempbars(self, d, c, series, i, vt, fps):
        y = c.get("y", 900)
        tmax = c.get("max", 80)
        d.text((self.pad, y), c.get("label", "TEMPS"), font=self.font("lbl", 24), fill=GREY)
        d.text((self.w - self.pad, y + 4), "°C", font=self.font("lbl2", 22), fill=GREY, anchor="ra")
        bar_x0 = self.pad + c.get("name_w", 70)
        bar_x1 = self.w - self.pad - c.get("val_w", 46)
        for k, sig in enumerate(c["signals"]):
            yy = y + 40 + k * c.get("row_h", 34)
            d.text((self.pad, yy - 4), c.get("names", [s.upper() for s in c["signals"]])[k],
                   font=self.font("small", 20), fill=GREY)
            v = self._val(series, sig, i)
            f = max(0.0, min(1.0, v / tmax))
            color = col(c.get("color"), (110, 200, 255))
            for th, cname in sorted((c.get("color_thresholds") or {}).items(),
                                    key=lambda kv: float(kv[0])):
                if v > float(th):
                    color = col(cname, color)
            d.rectangle([bar_x0, yy, bar_x1, yy + 16], fill=self.track)
            d.rectangle([bar_x0, yy, bar_x0 + (bar_x1 - bar_x0) * f, yy + 16], fill=color)
            d.text((self.w - self.pad, yy - 6), f"{v:.0f}", font=self.font("small", 20),
                   fill=WHITE, anchor="ra")

    def _w_graphs(self, d, c, series, i, vt, fps):
        win = c.get("window_s", 30)
        i0 = max(0, i - int(win * fps))
        x0 = self.pad
        gap = c.get("gap", 16)
        n = len(c["graphs"])
        w2 = (self.w - 2 * self.pad - gap * (n - 1)) / n
        for g, gc in enumerate(c["graphs"]):
            sliced = {k: v[i0:i + 1] for k, v in series.items()}
            self._graph(d, x0, c.get("y", 896), w2, c.get("h", 140), sliced,
                        gc["signal"], col(gc.get("color"), CYAN),
                        gc.get("min", 0), gc.get("max", 1),
                        gc.get("label", gc["signal"]),
                        {"t0": vt - (i - i0) / fps, "span": (i - i0) / fps or 1,
                         "events": self.timeline.markers() if self.timeline else []},
                        fps)
            x0 += w2 + gap

    # ---------- timeline overlays ----------
    def _draw_timeline_overlays(self, img, series, i, vt, fps):
        if not self.timeline:
            return img
        ev = self.timeline.active_note(vt)
        if ev is None:
            return img
        # dim via RGBA layer, then card
        dim = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 110))
        img_rgba = img.convert("RGBA")
        img_rgba.alpha_composite(dim)
        d = ImageDraw.Draw(img_rgba)
        card = [self.pad, 260, self.w - self.pad, 520]
        d.rectangle(card, fill=(28, 28, 36), outline=self.accent, width=3)
        tag = "FREEZE FRAME" if ev.kind == "freeze" else "NOTE"
        d.text((card[0] + 20, card[1] + 16), f"{tag}  @ {ev.time:,.1f}s",
               font=self.font("lbl", 26), fill=self.accent)
        # auto-fit title into card width
        tsize = 40
        maxw = card[2] - card[0] - 40
        while tsize > 20 and d.textlength(ev.label, font=self.font("med", tsize)) > maxw:
            tsize -= 2
        d.text((card[0] + 20, card[1] + 60), ev.label,
               font=self.font("med", tsize), fill=WHITE)
        # wrap text
        f2 = self.font("lbl2", 22)
        maxw = card[2] - card[0] - 40
        for k, ln in enumerate(_wrap_text(d, f2, ev.text or "", maxw)[:6]):
            d.text((card[0] + 20, card[1] + 120 + k * 30), ln, font=f2, fill=GREY)
        return img_rgba.convert("RGB")


def _wrap_text(d, font, text, maxw):
    """Word-wrap `text` to lines that fit `maxw` under `font`."""
    lines, cur = [], ""
    for wd in text.split():
        trial = (cur + " " + wd).strip()
        if cur and d.textlength(trial, font=font) > maxw:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines
