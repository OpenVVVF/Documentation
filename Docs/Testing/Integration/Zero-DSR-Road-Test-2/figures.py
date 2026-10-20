"""Regenerate the six report figures for the Zero DSR road test from the raw
TLM1 runtime-session log.

Usage (repo venv):
    .venv/bin/python figures.py [--stats-only]

Streams `Data/Tests/INT-Zero-DSR-Road-Test/raw/runtime-session-...jsonl.zst`
via `zstd -dc --long=31` (no zstandard wheel in the venv), keeps per-signal
(t, v) numpy arrays for the channels the report uses, prints every number the
report quotes, then renders fig-01..fig-06 PNGs (1500x1200) next to this file.

Parsed series are cached in /tmp/zero-dsr-figs-cache.npz keyed by the raw
file's mtime so re-styling does not re-parse 1.5 GB of JSONL.

Data quirks handled here:
  - bms_pack_a is a wrapping unsigned 16-bit value (0..65535); decode with a
    wrapping signed 16-bit mask (values >= 32768 are negative).
  - Inverter DC-link power/current and the vehicle pack channels use OPPOSITE
    sign conventions: pack positive = discharge, while inverter DC-link
    motoring reads negative. All panels here use "positive = out of pack".
"""

import json
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, MaxNLocator

HERE = Path(__file__).resolve().parent
RAW = (
    HERE.parent.parent.parent.parent
    / "Data/Tests/INT-Zero-DSR-Road-Test-2/raw"
    / "runtime-session-2026-10-17T01-16-37.122Z-1ed2dc74.jsonl.zst"
)
CACHE = Path("/tmp/zero-dsr-figs-cache-t2.npz")

SIGNALS = [
    "display_speed_kph", "display_speed_mph", "display_soc_pct",
    "display_motor_rpm", "Mech_RPM", "Elec_RPM",
    "cg_iq_ref_a", "cg_iq_a", "cg_id_a",
    "cg_iu_a", "cg_iv_a", "cg_iw_a",
    "cg_vd_req_v", "cg_vq_req_v", "cg_vlimit_scale", "cg_dclink_target_a",
    "cg_dclink_limit_active",
    "vdc_v", "dclink_i_a", "dclink_p_w", "bms_pack_v", "bms_pack_a",
    "thr_a_norm", "thr_regen_available_a",
    "temp_inv1_c", "temp_inv2_c", "temp_inv3_c", "temp_motor_c",
]
STRING_SIGNALS = ["control_state", "print"]

# Brand-neutral palette, consistent across all six figures.
C = {
    "speed": "#1f77b4", "throttle": "#ff7f0e", "rpm": "#2a6f97",
    "motor": "#d62728", "regen": "#2e8b57", "ref": "#6a51a3",
    "meas": "#d62728", "pack": "#1f77b4", "inv": "#d62728",
    "soc": "#2e8b57", "volt": "#ff7f0e", "scale": "#6a51a3",
    "fit": "#d62728", "t1": "#1f77b4", "t2": "#ff7f0e", "t3": "#d62728",
}

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.grid": True, "grid.color": "#e3e6e8", "grid.linewidth": 0.8,
    "axes.axisbelow": True, "axes.edgecolor": "#444444",
    "font.size": 13, "axes.titlesize": 14.5, "axes.labelsize": 14,
    "xtick.labelsize": 12.5, "ytick.labelsize": 12.5,
    "legend.fontsize": 11.5, "figure.titlesize": 16.5,
    "lines.linewidth": 1.1,
})


def mmss(x, _pos=None):
    x = max(x, 0)
    return f"{int(x // 60)}:{int(x % 60):02d}"


def style_time_axis(ax):
    ax.xaxis.set_major_formatter(FuncFormatter(mmss))
    ax.xaxis.set_major_locator(MaxNLocator(8, integer=True, prune="lower"))
    ax.set_xlabel("Session time (m:ss)")


def load_series():
    stamp = str(RAW.stat().st_mtime_ns)
    if CACHE.exists():
        z = np.load(CACHE, allow_pickle=True)
        if z["stamp"].item() == stamp:
            series = {n: (z[f"{n}__t"], z[f"{n}__v"]) for n in z["names"]}
            strings = json.loads(z["strings"].item())
            return series, strings
    series = {n: [[], []] for n in SIGNALS}
    strings = {n: [] for n in STRING_SIGNALS}
    proc = subprocess.Popen(
        ["zstd", "-dcq", "--long=31", str(RAW)], stdout=subprocess.PIPE,
        bufsize=1 << 20)
    n_lines = 0
    for raw in proc.stdout:
        n_lines += 1
        try:
            rec = json.loads(raw)
        except ValueError:
            continue
        rtype = rec.get("type")
        if rtype == "telemetry":
            t = rec["t"]
            for name, v in rec["values"].items():
                if name in series:
                    series[name][0].append(t)
                    series[name][1].append(v)
        elif rtype == "state":
            name = rec.get("signal")
            if name in strings:
                strings[name].append((rec["t"], rec["value"]))
        elif rtype == "log" or rtype == "print":
            if "print" in strings:
                strings["print"].append((rec.get("t", 0.0),
                                         rec.get("value", rec.get("message", ""))))
    proc.wait()
    out = {n: (np.asarray(t, dtype=np.float64), np.asarray(v, dtype=np.float64))
           for n, (t, v) in series.items()}
    save = {"stamp": np.array(stamp), "names": np.array(list(out)),
            "strings": np.array(json.dumps(strings))}
    for n, (t, v) in out.items():
        save[f"{n}__t"], save[f"{n}__v"] = t, v
    np.savez(CACHE, **save)
    print(f"parsed {n_lines} JSONL lines", file=sys.stderr)
    return out, strings


def decode_pack_a(v):
    # Wrapping unsigned 16-bit: values >= 32768 are negative. This session's
    # channel also carries a 65535 sentinel for "invalid" — reject it first.
    i = np.round(v).astype(np.int64) & 0xFFFF
    out = np.where(i >= 0x8000, i - 0x10000, i).astype(np.float64)
    out[i == 0xFFFF] = np.nan
    return out


def rolling_median(v, win=19):
    """Centered rolling median with a sliding-window views trick (win odd)."""
    if win % 2 == 0:
        win += 1
    n = len(v)
    if n < win:
        return v.copy()
    pad = win // 2
    padded = np.pad(v, pad, mode="edge")
    view = np.lib.stride_tricks.sliding_window_view(padded, win)
    return np.median(view, axis=1)


def rolling_mean_series(t, v, win):
    """Trailing `win`-second mean of v over irregular timestamps."""
    cs = np.concatenate(([0.0], np.cumsum(v[:-1] * np.diff(t))))
    lo = np.searchsorted(t, t - win)
    idx = np.arange(len(t))
    tot = cs[idx] - cs[lo]
    dur = t - t[lo]
    with np.errstate(invalid="ignore", divide="ignore"):
        return tot / dur


def interp(t_src, v_src, t_dst):
    return np.interp(t_dst, t_src, v_src)


class Data:
    """Computed session series and scalar stats shared by all figures."""

    def __init__(self, s, strings):
        def ts(name):
            t, v = s[name]
            ok = ~np.isnan(v)
            return t[ok], v[ok]

        self.t_kph, self.kph = ts("display_speed_kph")
        self.t_mph, self.mph = ts("display_speed_mph")
        self.t_rpm, self.rpm = ts("Mech_RPM")
        self.t_erpm, self.erpm = ts("Elec_RPM")
        self.t_iq, self.iq = ts("cg_iq_a")
        self.t_id, self.id_ = ts("cg_id_a")
        self.t_iqr, self.iqr = ts("cg_iq_ref_a")
        self.t_p, self.pw = ts("dclink_p_w")
        self.t_di, self.di = ts("dclink_i_a")
        self.t_vdc, self.vdc = ts("vdc_v")
        self.t_pkv, self.pkv = ts("bms_pack_v")
        self.t_pka, _pka = ts("bms_pack_a")
        _pkd = decode_pack_a(_pka)
        _ok = ~np.isnan(_pkd)
        self.t_pka, self.pka = self.t_pka[_ok], _pkd[_ok]
        self.pk_a_raw_lo = int((_pka < 1000).sum())
        self.pk_a_sentinel = int((np.round(_pka).astype(np.int64) & 0xFFFF
                                  == 0xFFFF).sum())
        self.t_soc, self.soc = ts("display_soc_pct")
        self.t_vs, self.vls = ts("cg_vlimit_scale")
        self.t_vd, self.vd = ts("cg_vd_req_v")
        self.t_vq, self.vq = ts("cg_vq_req_v")
        self.t_thr, self.thr = ts("thr_a_norm")
        self.t_t1, self.t1 = ts("temp_inv1_c")
        self.t_t2, self.t2 = ts("temp_inv2_c")
        self.t_t3, self.t3 = ts("temp_inv3_c")
        self.t_drpm, self.drpm = ts("display_motor_rpm")
        self.motor_temp_finite = int((~np.isnan(s["temp_motor_c"][1])).sum())
        self.t_iu, self.iu = ts("cg_iu_a")
        self.t_iv, self.iv = ts("cg_iv_a")
        self.t_iw, self.iw = ts("cg_iw_a")
        self.t_lim, self.lim = ts("cg_dclink_limit_active")

        # Consistent sign: positive = out of pack (motoring). Median-window
        # copies reject the single-sample glitches (±800 A) on both channels.
        self.p_out = -self.pw
        self.i_out = -self.di
        self.p_out_med = rolling_median(self.p_out, 19)
        self.i_out_med = rolling_median(self.i_out, 19)
        self.glitch_i = int((np.abs(self.i_out) > 800).sum())
        self.glitch_p = int((np.abs(self.p_out_med - self.p_out) > 20e3).sum())

        # Global stats.
        self.dur = float(max(self.t_iq[-1], self.t_kph[-1], self.t_p[-1]))
        self.dist_mi = float(np.trapezoid(self.mph, self.t_mph) / 3600.0)
        self.avg_mph = self.dist_mi / (self.dur / 3600.0)
        i = int(np.nanargmax(self.mph))
        self.top_mph, self.top_t = float(self.mph[i]), float(self.t_mph[i])
        self.top_kph = float(np.nanmax(self.kph))
        self.peak_iq = float(self.iq.max())
        self.peak_iq_med = float(rolling_median(self.iq, 19).max())
        self.peak_phase = float(max(self.iu.max(), -self.iu.min(),
                                    self.iv.max(), -self.iv.min(),
                                    self.iw.max(), -self.iw.min()))
        self.peak_phase_med = float(max(
            rolling_median(self.iu, 19).max(),
            -rolling_median(self.iu, 19).min(),
            rolling_median(self.iv, 19).max(),
            -rolling_median(self.iv, 19).min(),
            rolling_median(self.iw, 19).max(),
            -rolling_median(self.iw, 19).min()))
        e_out = float(np.trapezoid(np.clip(self.p_out_med, 0, None),
                                   self.t_p) / 3600)
        e_in = float(np.trapezoid(np.clip(-self.p_out_med, 0, None),
                                  self.t_p) / 3600)
        self.e_out, self.e_in = e_out, e_in
        p2s = rolling_mean_series(self.t_p, self.p_out_med, 2.0)
        self.pk_mot = float(self.p_out_med.max() / 1e3)
        self.pk_mot_raw = float(self.p_out.max() / 1e3)
        self.pk_mot2s = float(np.nanmax(p2s) / 1e3)
        self.pk_mot_i2s = float(np.nanmax(
            rolling_mean_series(self.t_di, self.i_out_med, 2.0)))
        self.pk_reg = float((-self.p_out_med).max() / 1e3)
        self.pk_reg2s = float(np.nanmax(
            rolling_mean_series(self.t_p, -self.p_out_med, 2.0)) / 1e3)
        # Vehicle pack channel power (1 Hz channels, this session: wrap-decoded
        # signed amps x pack volts)
        pk_pow = self.pka * interp(self.t_pkv, self.pkv, self.t_pka)
        self.pk_pack = float(np.nanmax(pk_pow) / 1e3)
        self.pk_pack_pair = (float(self.pka[np.nanargmax(pk_pow)]),
                             float(self.pkv[np.nanargmax(pk_pow)]))

        self.t_start = None
        for t, msg in strings["print"]:
            if "control" in str(msg) and "start" in str(msg):
                self.t_start = t
                break
        runs = [t for t, v in strings["control_state"] if str(v) == "RUNNING"]
        self.t_running = min(runs) if runs else None
        if self.t_start is None:
            self.t_start = self.t_running

        # Gearing fit and pole-pair ratio.
        rpm_k = interp(self.t_rpm, self.rpm, self.t_kph)
        ok = (self.kph > 1.0) & (rpm_k > 5)
        self.slope, self.icept = np.polyfit(self.kph[ok], rpm_k[ok], 1)
        r = rpm_k[ok] - (self.slope * self.kph[ok] + self.icept)
        self.r2 = 1 - np.sum(r ** 2) / np.sum((rpm_k[ok] - rpm_k[ok].mean()) ** 2)
        okp = (self.erpm > 0)
        rpm_e = interp(self.t_rpm, self.rpm, self.t_erpm)
        keep = okp & (rpm_e > 50)
        ratio = self.erpm[keep] / rpm_e[keep]
        self.pole_mean, self.pole_std = float(ratio.mean()), float(ratio.std())

        # Current-tracking stats, evaluated on the 190 Hz measured-current
        # grid with the 53 Hz reference interpolated onto it.
        self.iqr_on_iq = interp(self.t_iqr, self.iqr, self.t_iq)
        self.err = self.iq - self.iqr_on_iq
        self.bands = [(0, 50), (50, 200), (200, 500), (500, 700),
                      (700, 850), (850, 951)]
        self.table = []
        for lo, hi in self.bands:
            m = (self.iqr_on_iq >= lo) & (self.iqr_on_iq < hi)
            if m.sum() < 10:
                continue
            e = self.err[m]
            self.table.append((lo, hi, int(m.sum()), float(e.mean()),
                               float(e.std()),
                               float(np.sum(self.iq[m]) / np.sum(self.iqr_on_iq[m]))))
        m_regen = self.iqr_on_iq <= -40
        self.regen_track_mean = float(self.iq[m_regen].mean())
        spd_g = interp(self.t_kph, self.kph, self.t_iq)
        vls_g = interp(self.t_vs, self.vls, self.t_iq)
        m_low = (self.iqr_on_iq > 850) & (vls_g > 0.95) & (spd_g < 50)
        self.low_meas, self.low_ref = (float(self.iq[m_low].mean()),
                                       float(self.iqr_on_iq[m_low].mean()))
        m_high = (self.iqr_on_iq > 850) & (spd_g > 70)
        self.high_meas = float(self.iq[m_high].mean())
        self.high_spd = float(spd_g[m_high].mean())
        self.high_vls = (float(vls_g[m_high].min()), float(vls_g[m_high].max()))
        self.overshoot = float(self.err.max())

        di_at_pk = interp(self.t_di, self.di, self.t_pka)
        self.pack_corr = float(np.corrcoef(self.pka, -di_at_pk)[0, 1])

    def print_stats(self):
        d = self
        top = d.top_t
        print("=== cross-check against report claims ===")
        print(f"duration                 {d.dur:.2f} s   (claim 917.05)")
        print(f"distance / avg speed     {d.dist_mi:.2f} mi / {d.avg_mph:.1f} mph")
        print(f"top speed                {d.top_mph:.1f} mph ({d.top_kph:.1f} km/h) at t={top:.1f} s ({int(top//60)}:{top%60:04.1f})   (claim 51)")
        print(f"peak Iq measured / med   {d.peak_iq:.1f} / {d.peak_iq_med:.1f} A")
        print(f"peak phase raw / med     {d.peak_phase:.1f} / {d.peak_phase_med:.1f} A   (claim ~183)")
        print(f"Iq ref cap               max {d.iqr.max():.0f} / min {d.iqr.min():.0f} A")
        print(f"overshoot over ref       {d.overshoot:.1f} A")
        print(f"fit slope / intercept    {d.slope:.2f} rpm/kmh / {d.icept:.1f}, R2={d.r2:.4f}   (test 11: 35.4/+36)")
        print(f"pole-pair ratio          {d.pole_mean:.4f} +/- {d.pole_std:.4f}   (expect 5)")
        print(f"display rpm peak         {d.drpm.max():.0f} vs encoder {d.rpm.max():.0f}   (claim ~2990)")
        print(f"power motoring med/2s    {d.pk_mot:.1f} / {d.pk_mot2s:.1f} kW (raw max {d.pk_mot_raw:.1f})")
        print(f"pack channel peak power  {d.pk_pack:.1f} kW = {d.pk_pack_pair[0]:.0f} A x {d.pk_pack_pair[1]:.1f} V   (claim 26.4 = 261 x ~107)")
        print(f"2s-avg current peak      {d.pk_mot_i2s:.0f} A")
        print(f"regen med peak (into pk) {d.pk_reg:.2f} kW; pack channel min {np.nanmin(d.pka):.0f} A   (claim: no regen)")
        print(f"dc-link glitches         |i|>800A: {d.glitch_i}; med-corr>20kW: {d.glitch_p}   (claim: single-sample glitches)")
        print(f"dclink limiter active    max {d.lim.max():.0f} (1=active)")
        print(f"energy out / in / net    {d.e_out:.0f} / {d.e_in:.0f} / {d.e_out - d.e_in:.0f} Wh")
        print(f"consumption              {(d.e_out - d.e_in) / d.dist_mi:.0f} Wh/mi ({(d.e_out - d.e_in) / (d.dist_mi * 1.60934):.0f} Wh/km)")
        print(f"SOC first -> last        {d.soc[0]:.0f} -> {d.soc[-1]:.0f} %   (claim 73 -> 69)")
        print(f"pack V first -> last     {d.pkv[0]:.1f} -> {d.pkv[-1]:.1f}; range {d.pkv.min():.1f}-{d.pkv.max():.1f}   (claim ~107 V class)")
        print(f"vdc range                {d.vdc.min():.1f}-{d.vdc.max():.1f} V")
        print(f"vlimit scale min         {d.vls.min():.2f}")
        print(f"vd req min               {d.vd.min():.1f} V")
        print(f"temp inv1 start/peak/end {d.t1[0]:.1f}/{d.t1.max():.1f}/{d.t1[-1]:.1f}")
        print(f"temp inv2 start/peak/end {d.t2[0]:.1f}/{d.t2.max():.1f}/{d.t2[-1]:.1f}")
        print(f"temp inv3 start/peak/end {d.t3[0]:.1f}/{d.t3.max():.1f}/{d.t3[-1]:.1f}   (claim: 42-50 band)")
        print(f"temp motor finite count  {d.motor_temp_finite}   (expect NaN all session)")
        print(f"control start / RUNNING  t={d.t_start} / t={d.t_running}")
        print(f"regen ref samples        mean {d.regen_track_mean:.1f} A")
        print(f"pack vs dclink corr      {d.pack_corr:.3f}")
        print("tracking table: band  n  err_mean  err_std  meas/ref")
        for lo, hi, n, em, es, ratio in d.table:
            print(f"  {lo:>3}-{hi:<4} {n:>7} {em:8.1f} {es:8.1f} {ratio:8.2f}")


def decimate(t, v, n=4000):
    step = max(1, len(t) // n)
    return t[::step], v[::step]


def fig01(d):
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(10, 8), dpi=150,
                                     sharex=True,
                                     gridspec_kw=dict(hspace=0.16))
    fig.suptitle(
        f"Zero DSR road run — {d.dist_mi:.1f} mi over {d.dur / 60:.1f} min "
        f"(Gen7 control board, foc_demo graph)", y=0.995)

    a1.set_title("Road speed and throttle")
    a1.plot(d.t_kph, d.kph, color=C["speed"], lw=1.0,
            label="Road speed (display)")
    a1.set_ylabel("Speed (km/h)", color=C["speed"])
    a1.tick_params(axis="y", labelcolor=C["speed"])
    a1.set_ylim(0, max(100, d.top_kph * 1.08))
    a1b = a1.twinx()
    a1b.plot(d.t_thr, d.thr, color=C["throttle"], lw=0.7, alpha=0.85,
             label="Throttle A (norm)")
    a1b.set_ylabel("Throttle (0–1)", color=C["throttle"])
    a1b.tick_params(axis="y", labelcolor=C["throttle"])
    a1b.set_ylim(0, 1.02)
    a1b.grid(False)
    h1, l1 = a1.get_legend_handles_labels()
    h2, l2 = a1b.get_legend_handles_labels()
    a1.legend(h1 + h2, l1 + l2, loc="upper left", ncol=2)
    if d.t_start is not None:
        for ax in (a1, a2, a3):
            ax.axvline(d.t_start, color="#555555", ls="--", lw=1.0)
        if d.t_start < 0.05 * d.dur:
            a1.annotate(f"control already RUNNING from t = {d.t_start:.1f} s "
                        f"(dashed line)",
                        xy=(0.035, 0.05), xycoords="axes fraction",
                        fontsize=11.5, color="#333333",
                        bbox=dict(fc="white", ec="#cccccc", alpha=0.9))
        else:
            a1.annotate(f"control started → RUNNING (t = {d.t_start:.1f} s)",
                        xy=(d.t_start, a1.get_ylim()[1] * 0.55),
                        xytext=(d.t_start + 130, a1.get_ylim()[1] * 0.62),
                        arrowprops=dict(arrowstyle="->", color="#555555"),
                        fontsize=12, color="#333333")

    a2.set_title("DC-link power (positive = out of pack)")
    p_kw = d.p_out / 1e3
    tp, pk = decimate(d.t_p, p_kw, 20000)
    a2.axhline(0, color="#444444", lw=1.0)
    a2.fill_between(tp, pk, 0, where=pk >= 0, color=C["motor"], alpha=0.55,
                    lw=0, label="Motoring (from pack)")
    a2.fill_between(tp, pk, 0, where=pk < 0, color=C["regen"], alpha=0.65,
                    lw=0, label="Regen (to pack)")
    a2.set_ylabel("DC-link power (kW)")
    a2.legend(loc="lower left", ncol=2)

    a3.set_title("Torque current: reference vs measured")
    t_, r_ = decimate(d.t_iqr, d.iqr, 20000)
    a3.plot(t_, r_, color=C["ref"], lw=0.8, label="Iq ref")
    t_, m_ = decimate(d.t_iq, d.iq, 20000)
    a3.plot(t_, m_, color=C["meas"], lw=0.7, alpha=0.75, label="Iq measured")
    a3.set_ylabel("Iq (A)")
    a3.legend(loc="upper right", ncol=2)
    style_time_axis(a3)
    fig.align_ylabels()
    fig.savefig(HERE / "fig-01-ride-overview.png")
    plt.close(fig)


def fig02(d):
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(10, 8), dpi=150,
                                     sharex=True,
                                     gridspec_kw=dict(hspace=0.16))
    fig.suptitle("Energy and battery (positive = out of pack)", y=0.995)

    a1.set_title("DC-link and pack current (discharge positive)")
    t_, v_ = decimate(d.t_di, d.i_out, 20000)
    a1.plot(t_, v_, color=C["inv"], lw=0.7, alpha=0.85,
            label="Inverter DC-link current")
    a1.plot(d.t_pka, d.pka, color=C["pack"], lw=1.2,
            label="vehicle pack current (int16 decoded)")
    a1.axhline(0, color="#444444", lw=0.8)
    a1.set_ylabel("Current (A)")
    a1.legend(loc="lower left", ncol=2)

    dt = np.diff(d.t_p)
    e_out_t = np.concatenate(([0.0], np.cumsum(
        np.clip(d.p_out, 0, None)[:-1] * dt))) / 3600.0
    e_in_t = np.concatenate(([0.0], np.cumsum(
        np.clip(-d.p_out, 0, None)[:-1] * dt))) / 3600.0
    a2.set_title("Cumulative energy")
    t_, v_ = decimate(d.t_p, e_out_t)
    a2.plot(t_, v_, color=C["motor"], lw=1.6,
            label=f"Energy out of pack (motoring): {d.e_out:,.0f} Wh")
    t_, v_ = decimate(d.t_p, e_in_t)
    a2.plot(t_, v_, color=C["regen"], lw=1.6,
            label=f"Energy into pack (regen): {d.e_in:,.0f} Wh")
    t_, v_ = decimate(d.t_p, e_out_t - e_in_t)
    a2.plot(t_, v_, color="#444444", lw=1.4, ls="--",
            label=f"Net from pack: {d.e_out - d.e_in:,.0f} Wh")
    a2.set_ylabel("Energy (Wh)")
    a2.legend(loc="upper left")

    a3.set_title("State of charge and pack voltage")
    a3.plot(d.t_soc, d.soc, color=C["soc"], lw=1.8, drawstyle="steps-post",
            label="State of charge (display)")
    a3.set_ylabel("SOC (%)", color=C["soc"])
    a3.tick_params(axis="y", labelcolor=C["soc"])
    a3.set_ylim(min(80, float(d.soc.min()) - 2), 100)
    a3b = a3.twinx()
    a3b.plot(d.t_pkv, d.pkv, color=C["volt"], lw=1.0, alpha=0.85,
             label="vehicle pack voltage")
    a3b.set_ylabel("Pack voltage (V)", color=C["volt"])
    a3b.tick_params(axis="y", labelcolor=C["volt"])
    a3b.grid(False)
    h1, l1 = a3.get_legend_handles_labels()
    h2, l2 = a3b.get_legend_handles_labels()
    a3.legend(h1 + h2, l1 + l2, loc="lower left", ncol=2)
    style_time_axis(a3)
    fig.align_ylabels()
    fig.savefig(HERE / "fig-02-energy-battery.png")
    plt.close(fig)


def _launch_window(d):
    after = d.t_iqr[d.t_iqr > (d.t_running or 0)]
    vr = d.iqr[d.t_iqr > (d.t_running or 0)]
    idx = np.argmax(vr > 100)
    t0 = max(after[idx] - 1.0, 0)
    return t0, t0 + 6.0


def fig03(d):
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), dpi=150,
                             gridspec_kw=dict(hspace=0.30, wspace=0.22))
    fig.suptitle("Torque-current tracking: reference vs measured", y=0.99)
    a1, a2, a3, a4 = axes.flat

    a1.set_title("Full session")
    t_, v_ = decimate(d.t_iqr, d.iqr, 20000)
    a1.plot(t_, v_, color=C["ref"], lw=0.7, label="Iq ref")
    t_, v_ = decimate(d.t_iq, d.iq, 20000)
    a1.plot(t_, v_, color=C["meas"], lw=0.6, alpha=0.7, label="Iq measured")
    a1.set_ylabel("Iq (A)")
    a1.legend(loc="upper right", ncol=2)
    a1.xaxis.set_major_formatter(FuncFormatter(mmss))
    a1.xaxis.set_major_locator(MaxNLocator(5, integer=True, prune="lower"))
    a1.set_xlabel("Session time (m:ss)")

    t0, t1 = _launch_window(d)
    m = (d.t_iqr >= t0) & (d.t_iqr <= t1)
    mm = (d.t_iq >= t0) & (d.t_iq <= t1)
    a2.set_title(f"First launch detail ({int(t0//60)}:{t0%60:04.1f} – "
                 f"{int(t1//60)}:{t1%60:04.1f})")
    a2.plot(d.t_iqr[m], d.iqr[m], color=C["ref"], lw=1.6, label="Iq ref")
    a2.plot(d.t_iq[mm], d.iq[mm], color=C["meas"], lw=1.2, alpha=0.85,
            label="Iq measured")
    a2.set_ylabel("Iq (A)")
    a2.legend(loc="upper left")
    a2.xaxis.set_major_formatter(FuncFormatter(mmss))
    a2.set_xlabel("Session time (m:ss)")

    tw0, tw1 = d.top_t - 75, d.top_t + 25
    m = (d.t_iqr >= tw0) & (d.t_iqr <= tw1)
    mm = (d.t_iq >= tw0) & (d.t_iq <= tw1)
    a3.set_title(f"Top-speed run ({int(tw0//60)}:{tw0%60:04.1f} – "
                 f"{int(tw1//60)}:{tw1%60:04.1f})")
    a3.plot(d.t_iqr[m], d.iqr[m], color=C["ref"], lw=1.4, label="Iq ref")
    a3.plot(d.t_iq[mm], d.iq[mm], color=C["meas"], lw=1.0, alpha=0.85,
            label="Iq measured")
    a3.set_ylabel("Iq (A)")
    a3.legend(loc="lower left")
    a3.xaxis.set_major_formatter(FuncFormatter(mmss))
    a3.set_xlabel("Session time (m:ss)")

    err = d.err
    keep = (d.t_iq > (d.t_running or 0))
    err = err[keep]
    a4.set_title("Tracking error (measured − ref)")
    n, bins, _ = a4.hist(np.clip(err, -400, 400), bins=100, range=(-400, 400),
                         color=C["inv"], alpha=0.8)
    a4.set_xlim(-400, 400)
    a4.set_xlabel("Error (A)")
    a4.set_ylabel("Samples (log scale)")
    a4.set_yscale("log")
    a4.axvline(0, color="#444444", lw=1.0)
    p99 = np.percentile(np.abs(err), 99)
    a4.annotate(f"n = {err.size:,}\nmean {err.mean():.1f} A, std {err.std():.1f} A\n"
                f"99% of |error| ≤ {p99:.0f} A",
                xy=(0.03, 0.95), xycoords="axes fraction", va="top",
                fontsize=11.5,
                bbox=dict(fc="white", ec="#cccccc", alpha=0.9))
    fig.savefig(HERE / "fig-03-current-tracking.png")
    plt.close(fig)


def fig04(d):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 8), dpi=150,
                                 gridspec_kw=dict(hspace=0.28,
                                                  height_ratios=[3, 2]))
    fig.suptitle("Motor speed vs road speed (gearing check)", y=0.99)

    rpm_k = interp(d.t_rpm, d.rpm, d.t_kph)
    ok = (d.kph >= 0) & (rpm_k >= 0)
    x, y = d.kph[ok], rpm_k[ok]
    step = max(1, len(x) // 6000)
    a1.plot(x[::step], y[::step], ".", ms=2.5, color=C["rpm"], alpha=0.35,
            rasterized=True)
    xs = np.linspace(0, d.top_kph * 1.05, 10)
    a1.plot(xs, d.slope * xs + d.icept, color=C["fit"], lw=2.2,
            label=f"fit: {d.slope:.1f} rpm per km/h "
                  f"(intercept {d.icept:+.0f}, R² = {d.r2:.4f})")
    a1.set_xlabel("Road speed (km/h)")
    a1.set_ylabel("Mech_RPM (encoder)")
    a1.set_xlim(0, d.top_kph * 1.06)
    a1.set_ylim(0, d.rpm.max() * 1.06)
    a1.legend(loc="upper left")
    a1.annotate(f"Elec_RPM / Mech_RPM = {d.pole_mean:.4f} ± {d.pole_std:.4f} "
                f"(5 pole pairs)", xy=(0.97, 0.05), xycoords="axes fraction",
                ha="right", fontsize=11.5,
                bbox=dict(fc="white", ec="#cccccc", alpha=0.9))

    resid = y - (d.slope * x + d.icept)
    okm = (y > 50) & (x > 1)
    a2.hist(resid[okm], bins=120, range=(-300, 300), color=C["rpm"], alpha=0.8)
    a2.set_xlim(-300, 300)
    a2.set_yscale("log")
    a2.axvline(0, color="#444444", lw=1.0)
    a2.set_xlabel("Fit residual (rpm)")
    a2.set_ylabel("Samples (log scale)")
    a2.annotate(f"std = {resid[okm].std():.0f} rpm "
                f"(n = {int(okm.sum()):,}, moving samples)",
                xy=(0.03, 0.93), xycoords="axes fraction", va="top",
                fontsize=11.5,
                bbox=dict(fc="white", ec="#cccccc", alpha=0.9))
    fig.savefig(HERE / "fig-04-speed-rpm.png")
    plt.close(fig)


def fig05(d):
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), dpi=150,
                             gridspec_kw=dict(hspace=0.32, wspace=0.38))
    fig.subplots_adjust(left=0.08, right=0.93, top=0.93, bottom=0.075)
    fig.suptitle("DC-link voltage and field weakening", y=0.99)
    a1, a2, a3, a4 = axes.flat

    a1.set_title("DC bus vs pack voltage")
    t_, v_ = decimate(d.t_vdc, d.vdc, 20000)
    a1.plot(t_, v_, color=C["inv"], lw=0.8, alpha=0.85,
            label="Inverter Vdc sense")
    a1.plot(d.t_pkv, d.pkv, color=C["pack"], lw=1.1, label="vehicle pack voltage")
    a1.set_ylabel("Voltage (V)")
    a1.legend(loc="lower left")
    a1.xaxis.set_major_formatter(FuncFormatter(mmss))
    a1.xaxis.set_major_locator(MaxNLocator(5, integer=True, prune="lower"))
    a1.set_xlabel("Session time (m:ss)")

    # Scatter on the v-limit (2.8 Hz) grid so the rare FW dips survive;
    # road speed (1.6 Hz) is interpolated onto it.
    kph_v = interp(d.t_kph, d.kph, d.t_vs)
    ok = (kph_v > 1) & (d.t_vs > (d.t_running or 0))
    x, y = kph_v[ok], d.vls[ok]
    a2.plot(x, y, ".", ms=3.5, color=C["scale"], alpha=0.35,
            rasterized=True)
    a2.set_xlabel("Road speed (km/h)")
    a2.set_ylabel("V-limit scale")
    a2.set_ylim(0.3, 1.03)
    # FW onset: lowest speed at which the running scale leaves ~1.0
    m = y < 0.98
    onset = float(x[m].min()) if m.any() else float("nan")
    if m.any():
        a2.axvline(onset, color="#555555", ls="--", lw=1.0)
        a2.annotate(f"FW onset ≈ {onset:.0f} km/h\nscale min {d.vls.min():.2f}",
                    xy=(onset, 0.45), xytext=(onset - 40, 0.40),
                    arrowprops=dict(arrowstyle="->", color="#555555"),
                    fontsize=12)

    tw0, tw1 = d.top_t - 75, d.top_t + 25
    mr = (d.t_iqr >= tw0) & (d.t_iqr <= tw1)
    mq = (d.t_iq >= tw0) & (d.t_iq <= tw1)
    a3.set_title("Top-speed run: Iq request vs delivered")
    a3.plot(d.t_iqr[mr], d.iqr[mr], color=C["ref"], lw=1.4, ls="--",
            label="Iq ref (request)")
    a3.plot(d.t_iq[mq], d.iq[mq], color=C["meas"], lw=1.0, alpha=0.85,
            label="Iq measured (delivered)")
    a3.set_ylabel("Iq (A)")
    a3b = a3.twinx()
    mv = (d.t_vs >= tw0) & (d.t_vs <= tw1)
    a3b.plot(d.t_vs[mv], d.vls[mv], color=C["scale"], lw=1.2, alpha=0.8,
             label="V-limit scale")
    a3b.set_ylabel("V-limit scale", color=C["scale"])
    a3b.tick_params(axis="y", labelcolor=C["scale"])
    a3b.set_ylim(0.3, 1.05)
    a3b.grid(False)
    h1, l1 = a3.get_legend_handles_labels()
    h2, l2 = a3b.get_legend_handles_labels()
    a3.legend(h1 + h2, l1 + l2, loc="upper right", ncol=2)
    a3.xaxis.set_major_formatter(FuncFormatter(mmss))
    a3.set_xlabel("Session time (m:ss)")
    a3.annotate(f"vd request min {d.vd.min():.0f} V (session)",
                xy=(0.03, 0.04), xycoords="axes fraction", fontsize=11.5,
                bbox=dict(fc="white", ec="#cccccc", alpha=0.9))

    m1 = (d.t_vdc >= tw0) & (d.t_vdc <= tw1)
    a4.set_title("Top-speed run: bus sag and FW depth")
    a4.plot(d.t_vdc[m1], d.vdc[m1], color=C["inv"], lw=1.2,
            label="Vdc (V)")
    a4.set_ylabel("Vdc (V)", color=C["inv"])
    a4.tick_params(axis="y", labelcolor=C["inv"])
    a4b = a4.twinx()
    a4b.plot(d.t_vs[mv], d.vls[mv], color=C["scale"], lw=1.4,
             label="V-limit scale")
    a4b.set_ylabel("V-limit scale", color=C["scale"])
    a4b.tick_params(axis="y", labelcolor=C["scale"])
    a4b.set_ylim(0.3, 1.05)
    a4b.grid(False)
    h1, l1 = a4.get_legend_handles_labels()
    h2, l2 = a4b.get_legend_handles_labels()
    a4.legend(h1 + h2, l1 + l2, loc="upper right", ncol=2)
    a4.xaxis.set_major_formatter(FuncFormatter(mmss))
    a4.set_xlabel("Session time (m:ss)")
    seg = d.vdc[m1]
    a4.annotate(f"bus sag to {seg.min():.1f} V", xy=(0.03, 0.05),
                xycoords="axes fraction", fontsize=11.5,
                bbox=dict(fc="white", ec="#cccccc", alpha=0.9))
    fig.savefig(HERE / "fig-05-voltage-field-weakening.png")
    plt.close(fig)


def fig06(d):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 8), dpi=150,
                                 gridspec_kw=dict(hspace=0.26))
    fig.suptitle("Inverter temperatures", y=0.995)

    a1.set_title("Temperature vs time")
    a1.plot(d.t_t1, d.t1, color=C["t1"], lw=1.4,
            label=f"Inverter T1 (peak {d.t1.max():.1f} °C)")
    a1.plot(d.t_t2, d.t2, color=C["t2"], lw=1.4,
            label=f"Inverter T2 (peak {d.t2.max():.1f} °C)")
    a1.plot(d.t_t3, d.t3, color=C["t3"], lw=1.4,
            label=f"Inverter T3 (peak {d.t3.max():.1f} °C)")
    a1.set_ylabel("Temperature (°C)")
    a1.legend(loc="upper left")
    style_time_axis(a1)
    if d.motor_temp_finite == 0:
        a1.annotate("motor temp channel NaN all session",
                    xy=(0.97, 0.06), xycoords="axes fraction", ha="right",
                    fontsize=11.5,
                    bbox=dict(fc="white", ec="#cccccc", alpha=0.9))

    a2.set_title("Max inverter temperature vs |DC-link power|")
    tmax = np.maximum.reduce((
        d.t1,
        interp(d.t_t2, d.t2, d.t_t1),
        interp(d.t_t3, d.t3, d.t_t1),
    ))
    p_at_t = np.abs(interp(d.t_p, d.p_out, d.t_t1)) / 1e3
    step = max(1, len(p_at_t) // 8000)
    a2.plot(p_at_t[::step], tmax[::step], ".", ms=2.5, color=C["t3"],
            alpha=0.25, rasterized=True)
    edges = np.arange(0, np.ceil(p_at_t.max()) + 1, 1.0)
    bmean, bmax, bmid = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p_at_t >= lo) & (p_at_t < hi)
        if m.sum() >= 30:
            bmid.append((lo + hi) / 2)
            bmean.append(tmax[m].mean())
            bmax.append(np.percentile(tmax[m], 95))
    a2.plot(bmid, bmax, color="#7a1f1f", lw=2.0, label="95th pct (1 kW bins)")
    a2.plot(bmid, bmean, color=C["pack"], lw=2.0, label="mean (1 kW bins)")
    a2.set_xlabel("|DC-link power| (kW)")
    a2.set_ylabel("Max inverter temp (°C)")
    a2.set_xlim(left=0)
    a2.set_ylim(bottom=max(0, tmax.min() - 3))
    a2.legend(loc="lower right")
    a2.annotate(f"session: peak {tmax.max():.1f} °C (T3), "
                f"max |P| = {d.pk_mot:.1f} kW",
                xy=(0.03, 0.93), xycoords="axes fraction", va="top",
                fontsize=11.5,
                bbox=dict(fc="white", ec="#cccccc", alpha=0.9))
    fig.savefig(HERE / "fig-06-thermal.png")
    plt.close(fig)


def main():
    stats_only = "--stats-only" in sys.argv
    s, strings = load_series()
    d = Data(s, strings)
    d.print_stats()
    if stats_only:
        return
    print("rendering figures...", file=sys.stderr)
    fig01(d)
    fig02(d)
    fig03(d)
    fig04(d)
    fig05(d)
    fig06(d)
    print("wrote fig-01..fig-06 PNGs", file=sys.stderr)


if __name__ == "__main__":
    main()
