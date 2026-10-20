"""Composite video + telemetry panels + brand framing into one mp4.

Pipeline (single ffmpeg pass, except the cached intro/outro cards):
  intro.mp4 + [fitted video + panel overlays + watermark + freeze
  splices] + outro.mp4  --concat-->  OUT.mp4

Layout from config["layout"]:
  canvas_w/canvas_h : output size (default 1920x1080)
  video_width/video_height : the video is uniformly scaled to FIT inside
      this box (aspect ratio preserved, nothing cropped or stretched)
      and centered inside the box at video_x
  panels: list of panel mp4s, each with its own x position
      [{"file": "left.mp4", "x": 40}, ...]

Brand framing (config["brand"]):
  intro_s/outro_s durations; cards are built by titlecards and cached in
  _brand_cache/ keyed by a hash of the test/brand/fps/canvas config, so
  rebuilds skip when the branding did not change.
  watermark (default true): the white wordmark + "TEST <number>" at ~35%
  opacity over the top-left of the video box (never over the panels).

Audio: the main video's audio is kept (resampled to 48 kHz stereo AAC
128k); cards carry silent stereo tracks, so the whole file re-encodes
audio once to AAC — `-c:a copy` is intentionally not used on this pass.

Freeze events (kind=freeze) hold the video frame still: the composited
main is split into trim segments around each freeze and a cloned still
is spliced in.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from . import brand, titlecards


def sh(cmd):
    print("+", " ".join(str(c) for c in cmd[:8]), "...", file=sys.stderr)
    subprocess.run(cmd, check=True)


def has_audio(path):
    rc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True)
    return bool(rc.stdout.strip())


def _watermark_key(config):
    lay = config.get("layout", {})
    payload = {
        "brand_key": titlecards.brand_key(config),
        "box": [lay.get("canvas_w", 1920), lay.get("canvas_h", 1080),
                lay.get("video_width", 1344), lay.get("video_x")],
    }
    return hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]


def ensure_watermark_png(config):
    """Build or fetch the cached full-canvas watermark RGBA PNG."""
    cache = titlecards.cache_dir(config)
    cache.mkdir(exist_ok=True)
    path = cache / f"watermark-{_watermark_key(config)}.png"
    if not path.exists():
        brand.build_watermark(config).save(path)
        print(f"watermark: {path}", file=sys.stderr)
    return path


def build_filter_complex(config, panel_files, have_audio,
                         intro=None, outro=None, watermark=None, fps=15):
    """Returns (filter_complex, v_label, a_label)."""
    lay = config.get("layout", {})
    cw = lay.get("canvas_w", 1920)
    ch = lay.get("canvas_h", 1080)
    vw = lay.get("video_width", 1344)
    vh = lay.get("video_height", 1080)
    vx = lay.get("video_x", (cw - vw) // 2)
    vdur = config["video"]["duration"]
    freezes = sorted([e for e in config.get("timeline", []) if e.get("kind") == "freeze"],
                     key=lambda e: e["time"])

    # input indices: 0=video, 1..N=panels, then intro, outro, watermark
    video_i = 0
    intro_i = 1 + len(panel_files) if intro else None
    outro_i = 1 + len(panel_files) + (1 if intro else 0) if outro else None
    wm_i = (1 + len(panel_files) + (1 if intro else 0) + (1 if outro else 0)
            if watermark else None)

    fc = []
    # fit the video into its box, centered; pillarbox-pad out to the canvas
    fc.append(
        f"[{video_i}:v]fps={fps},scale=w={vw}:h={vh}"
        f":force_original_aspect_ratio=decrease:flags=lanczos,setsar=1,"
        f"pad={cw}:{ch}:x={vx}+({vw}-iw)/2:y=({ch}-ih)/2:color=black[lp0];")
    cur = "[lp0]"
    for k in range(len(panel_files)):
        fc.append(f"{cur}[{k + 1}:v]overlay={config['layout']['panels'][k]['x']}:0"
                  f":format=auto:shortest=1[lp{k + 1}];")
        cur = f"[lp{k + 1}]"
    if watermark is not None:
        fc.append(f"{cur}[{wm_i}:v]overlay=0:0:format=auto:shortest=1[wm];")
        cur = "[wm]"
    fc.append(f"{cur}format=yuv420p[vmix];")

    # freeze-frame splicing
    if not freezes:
        fc.append(f"[vmix]null[main];")
    else:
        bounds, t = [], 0.0
        for e in freezes:
            d = e.get("duration", 3.0)
            bounds.append((t, e["time"], None))
            bounds.append((e["time"], e["time"] + d, e))
            t = e["time"] + d
        bounds.append((t, vdur, None))
        outs = "".join(f"[s{k}]" for k in range(len(bounds)))
        fc.append(f"[vmix]split={len(bounds)}{outs};")
        labels = []
        for k, (a, b, ev) in enumerate(bounds):
            if ev is None:
                fc.append(f"[s{k}]trim=start={a}:end={b},setpts=PTS-STARTPTS[p{k}];")
            else:
                # hold on the exact still frame for `duration`: pick the
                # first frame of the window and loop it frame-count-exact
                # (tpad would add/lose a frame at some fps)
                hold = max(0, round((b - a) * fps) - 1)
                fc.append(f"[s{k}]trim=start={a}:end={b},setpts=PTS-STARTPTS,"
                          f"select='eq(n\\,0)',loop=loop={hold}:size=1,"
                          f"setpts=PTS-STARTPTS[p{k}];")
            labels.append(f"[p{k}]")
        fc.append("".join(labels) + f"concat=n={len(bounds)}:v=1:a=0[main];")

    # audio for the main segment: source audio, else generated silence
    if have_audio:
        fc.append(f"[{video_i}:a]aresample=48000,"
                  f"aformat=channel_layouts=stereo,atrim=0:{vdur},"
                  f"asetpts=PTS-STARTPTS[maina];")
    else:
        fc.append(f"anullsrc=r=48000:cl=stereo:d={vdur}[maina];")

    # concat parts (cards normalize to fps/sar first); inputs are
    # segment-video/segment-audio pairs in playback order
    segs = []
    if intro is not None:
        fc.append(f"[{intro_i}:v]fps={fps},setsar=1[iv];"
                  f"[{intro_i}:a]aresample=48000,aformat=channel_layouts=stereo[ia];")
        segs.append(("[iv]", "[ia]"))
    segs.append(("[main]", "[maina]"))
    if outro is not None:
        fc.append(f"[{outro_i}:v]fps={fps},setsar=1[ov];"
                  f"[{outro_i}:a]aresample=48000,aformat=channel_layouts=stereo[oa];")
        segs.append(("[ov]", "[oa]"))
    sin = "".join(v + a for v, a in segs)
    fc.append(f"{sin}concat=n={len(segs)}:v=1:a=1[vout][aout]")
    return "".join(fc), "[vout]", "[aout]"


def composite(config, video, out, panel_dir=None):
    """Render OUT from VIDEO + the config's panel streams + brand framing."""
    lay = config.get("layout", {})
    fps = config.get("fps", 15)
    panel_files = []
    for p in lay.get("panels", []):
        f = p["file"]
        panel_files.append(str(Path(panel_dir) / f) if panel_dir else f)
        if not Path(panel_files[-1]).exists():
            raise FileNotFoundError(
                f"panel stream {panel_files[-1]} missing; run the 'panels' step first")

    brand_cfg = config.get("brand", {})
    use_intro = brand_cfg.get("intro", True) and brand_cfg.get("intro_s", 5.0) > 0
    use_outro = brand_cfg.get("outro", True) and brand_cfg.get("outro_s", 4.0) > 0
    intro = titlecards.ensure_card(config, "intro") if use_intro else None
    outro = titlecards.ensure_card(config, "outro") if use_outro else None
    wm = ensure_watermark_png(config) if brand_cfg.get("watermark", True) else None

    base = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(video)]
    for f in panel_files:
        base += ["-i", f]
    if intro:
        base += ["-i", str(intro)]
    if outro:
        base += ["-i", str(outro)]
    if wm:
        base += ["-loop", "1", "-i", str(wm)]

    fc, v_label, a_label = build_filter_complex(
        config, panel_files, has_audio(video),
        intro=intro, outro=outro, watermark=wm, fps=fps)
    cmd = (base + ["-filter_complex", fc, "-map", v_label, "-map", a_label,
                   "-c:v", "libx264", "-crf", "19", "-preset", "veryfast",
                   "-c:a", "aac", "-b:a", "128k",
                   "-movflags", "+faststart", str(out)])
    sh(cmd)
    return out
