"""vvvf-overlay: branded telemetry video overlays for OpenVVVF.

Subcommands:
  sample     snapshot PNGs: panels, watermark, intro/outro frames
  panels     render every panel stream declared in layout.panels
  composite  composite video + panels + watermark + intro/outro
  build      panels + composite in one step
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from . import brand, render_run, titlecards, composite


def _load_and_chdir(args):
    cfgp = Path(args.config).resolve()
    cfg = render_run.load_config(cfgp)
    # paths in the config (session, panel files, cache) are config-relative
    os.chdir(cfgp.parent)
    return cfg


def _parse_times(s):
    return [float(x) for x in s.split(",") if x.strip()]


def cmd_sample(args):
    cfg = _load_and_chdir(args)
    times = _parse_times(args.times)
    if not args.cards_only:
        render_run.sample_snapshots(cfg, times, out_prefix=args.prefix)
    if not args.panels_only:
        wm = composite.ensure_watermark_png(cfg)
        print(f"watermark: {wm}", file=sys.stderr)
        intro = list(titlecards.build_intro_frames(cfg))
        outro = list(titlecards.build_outro_frames(cfg))
        picks = {}
        for name, frames in (("intro", intro), ("outro", outro)):
            idx = {0, len(frames) // 2, len(frames) - 1}
            for i in sorted(idx):
                p = f"{args.prefix}_{name}_f{i:04d}.png"
                frames[i].save(p)
                print(p, file=sys.stderr)
                picks[p] = True
    return 0


def cmd_panels(args):
    cfg = _load_and_chdir(args)
    render_run.render_panels(cfg, outdir=args.outdir)
    return 0


def cmd_composite(args):
    cfg = _load_and_chdir(args)
    composite.composite(cfg, args.video, args.out, panel_dir=args.panel_dir)
    return 0


def cmd_build(args):
    cfg = _load_and_chdir(args)
    render_run.render_panels(cfg, outdir=args.panel_dir)
    composite.composite(cfg, args.video, args.out, panel_dir=args.panel_dir)
    return 0


def cmd_cards(args):
    cfg = _load_and_chdir(args)
    print(titlecards.ensure_card(cfg, "intro"), file=sys.stderr)
    print(titlecards.ensure_card(cfg, "outro"), file=sys.stderr)
    return 0


def cmd_assets(args):
    cfg = _load_and_chdir(args)
    wm = composite.ensure_watermark_png(cfg)
    out = args.out or f"{Path(args.config).stem}_watermark.png"
    import shutil
    shutil.copy(wm, out)
    print(out, file=sys.stderr)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="vvvf-overlay", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("sample", help="snapshot PNGs of panels, watermark, cards")
    p.add_argument("config")
    p.add_argument("-t", "--times", default="0",
                   help="comma-separated video times for panel snapshots")
    p.add_argument("--prefix", default="sample")
    p.add_argument("--panels-only", action="store_true")
    p.add_argument("--cards-only", action="store_true")
    p.set_defaults(fn=cmd_sample)

    p = sub.add_parser("panels", help="render all panel streams (H.264 mp4)")
    p.add_argument("config")
    p.add_argument("-o", "--outdir", default=None,
                   help="output directory (default: config directory)")
    p.set_defaults(fn=cmd_panels)

    p = sub.add_parser("composite", help="composite video + panels + branding")
    p.add_argument("config")
    p.add_argument("video")
    p.add_argument("out")
    p.add_argument("--panel-dir", default=None,
                   help="directory holding the rendered panel mp4s")
    p.set_defaults(fn=cmd_composite)

    p = sub.add_parser("build", help="panels + composite in one step")
    p.add_argument("config")
    p.add_argument("video")
    p.add_argument("out")
    p.add_argument("--panel-dir", default=None)
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("cards", help="(re)build cached intro/outro card mp4s")
    p.add_argument("config")
    p.set_defaults(fn=cmd_cards)

    p = sub.add_parser("assets", help="write the cached watermark PNG here")
    p.add_argument("config")
    p.add_argument("-o", "--out", default=None)
    p.set_defaults(fn=cmd_assets)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
