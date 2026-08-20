"""DC-link capacitor ripple current and thermal load plots for OV-C2-DD-DCLINK-RIPPLE.

Regenerate with:  ../../../.venv/bin/python plots.py   (from this folder)
or:               .venv/bin/python Docs/Hardware/Power-Stages/C2/Design-Documents/DC-Link-Ripple/plots.py

All datasheet values are from the Nichicon UCS series catalog (CAT.8100N),
https://www.nichicon.co.jp/english/series_items/catalog_pdf/e-ucs.pdf
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Inverter operating envelope (OV-C2-DD-THERMAL v1.1)
M_MOD = 1.0        # modulation index
COS_PHI = 0.8      # load power factor
N_CANS = 60        # capacitors in parallel
FREQS = [2000, 6000, 8000]  # PWM switching frequencies [Hz]

# ---------------------------------------------------------------------------
# Nichicon UCS catalog data (e-ucs.pdf, CAT.8100N)
# (part, C [uF], Vrated, rated ripple [A rms] @ 105 C / 100 kHz, tan delta @ 120 Hz)
CAP_200V = dict(name="UCS2D331MHD", C=330e-6, V=200, I_rated_100k=3.22, tand=0.20)
CAP_450V = dict(name="UCS2W680MHD", C=68e-6, V=450, I_rated_100k=1.575, tand=0.24)

# Frequency coefficient of rated ripple current (catalog p.1):
# 50 Hz 0.40 / 120 Hz 0.50 / 1 kHz 0.80 / 10 kHz 0.90 / >=100 kHz 1.00
# Log-linear interpolation between the 1 kHz and 10 kHz anchors.
def freq_coeff(f):
    f = np.asarray(f, dtype=float)
    k = np.empty_like(f)
    lo = f <= 1e3
    hi = f >= 1e5
    mid1 = (f > 1e3) & (f < 1e4)
    mid2 = (f >= 1e4) & (f < 1e5)
    k[lo] = 0.50  # 120 Hz value; conservative flat below 1 kHz
    k[mid1] = 0.80 + 0.10 * np.log10(f[mid1] / 1e3)
    k[mid2] = 0.90 + 0.10 * np.log10(f[mid2] / 1e4)
    k[hi] = 1.00
    return k

# Effective ESR model.
# Anchor: ESR at 100 kHz assumed 0.15 x the 120 Hz tan-delta maximum [ASM].
# Frequency shaping from the squared inverse of the catalog frequency
# coefficient, so that I_rated(f)^2 * ESR(f) = const (the datasheet method).
def esr_120hz_max(cap):
    return cap["tand"] / (2 * np.pi * 120 * cap["C"])

def esr_100k(cap):
    return 0.15 * esr_120hz_max(cap)  # [ASM] typical snap-in ratio

def esr_f(cap, f):
    return esr_100k(cap) / freq_coeff(f) ** 2

# ---------------------------------------------------------------------------
# DC-link capacitor RMS ripple current, Kolar & Round (IEE Proc. EPA, 2006),
# phase-current-referred, 2-level inverter, SVPWM/center-aligned PWM:
def ripple_factor(m=M_MOD, cos_phi=COS_PHI):
    return np.sqrt(2 * m * (np.sqrt(3) / (4 * np.pi)
                            + cos_phi ** 2 * (np.sqrt(3) / np.pi - 9 * m / 16)))

KF = ripple_factor()
print(f"Ripple factor I_cap,rms / I_phase,rms = {KF:.4f} (m={M_MOD}, cos phi={COS_PHI})")

I_phase = np.linspace(0, 600, 121)
I_can = KF * I_phase / N_CANS  # per-can ripple, frequency independent (RMS)

# ---------------------------------------------------------------------------
# Console table: key operating points
print("\nPer-can ripple current and bank loss at key points:")
print(f"{'I_phase':>8} {'f_sw':>6} | {'I_can(200V/450V)':>18} {'I_rated 200V':>13} "
      f"{'x rated':>8} {'P_bank 200V':>12} {'I_rated 450V':>13} {'x rated':>8} {'P_bank 450V':>12}")
for Iph in [100, 200, 300, 400, 500, 600]:
    for f in FREQS:
        ic = KF * Iph / N_CANS
        row = [f"{Iph:>8} {f/1000:>5.0f}k | {ic:>9.2f} {ic:>9.2f}"]
        for cap in (CAP_200V, CAP_450V):
            ir = cap["I_rated_100k"] * freq_coeff(f)
            pb = N_CANS * ic ** 2 * esr_f(cap, f)
            row.append(f"{ir:>13.2f} {ic/ir:>8.2f} {pb:>12.1f}")
        print(" ".join(row))

# Current at which the 200 V bank reaches its ripple rating
for f in FREQS:
    ir = CAP_200V["I_rated_100k"] * freq_coeff(f)
    print(f"200 V bank ripple limit reached at I_phase = {N_CANS*ir/KF:.0f} A ({f/1000:.0f} kHz)")

# Phase current at which the 200 V bank dissipates 40 W
for f in FREQS:
    e = esr_f(CAP_200V, f)
    i40 = np.sqrt(40.0 / (N_CANS * e)) * N_CANS / KF
    print(f"200 V bank hits 40 W at I_phase = {i40:.0f} A ({f/1000:.0f} kHz)")

# ---------------------------------------------------------------------------
# Plot (a): per-can ripple current vs phase current, rated-ripple limit lines
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharex=True)
colors = {2000: "C0", 6000: "C1", 8000: "C2"}
for ax, cap in zip(axes, (CAP_200V, CAP_450V)):
    ax.plot(I_phase, I_can, "k-", lw=2, label="Per-can ripple current")
    for f in FREQS:
        ir = cap["I_rated_100k"] * freq_coeff(f)
        ax.axhline(ir, color=colors[f], ls="--",
                   label=f"Rated ripple {f/1000:.0f} kHz: {ir:.2f} A")
    ax.set_title(f"{cap['name']} ({cap['C']*1e6:.0f} uF / {cap['V']} V)")
    ax.set_xlabel("Phase current (A rms)")
    ax.set_ylabel("Per-can ripple current (A rms)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xlim(0, 600)
    ax.set_ylim(0, None)
fig.suptitle("Per-can DC-link ripple current vs phase current (m=1, cos phi=0.8, 60-can bank)")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "DCLinkRipplePerCan.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot (b): total bank I^2*ESR heat vs phase current, per frequency
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharex=True)
for ax, cap in zip(axes, (CAP_200V, CAP_450V)):
    for f in FREQS:
        p_bank = N_CANS * I_can ** 2 * esr_f(cap, f)
        ax.plot(I_phase, p_bank, color=colors[f], lw=2, label=f"{f/1000:.0f} kHz")
    ax.axhline(40, color="k", ls=":", lw=1.5, label="40 W (thermal-doc figure)")
    ax.set_title(f"{cap['name']} ({cap['C']*1e6:.0f} uF / {cap['V']} V)")
    ax.set_xlabel("Phase current (A rms)")
    ax.set_ylabel("Total bank I$^2$R heat (W)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xlim(0, 600)
    ax.set_ylim(0, None)
fig.suptitle("DC-link bank ripple loss vs phase current (m=1, cos phi=0.8)")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "DCLinkRippleBankHeat.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot (c): lifetime multiplier vs can temperature (Arrhenius 10 K rule,
# base 10000 h at 105 C from the UCS endurance spec)
T = np.linspace(40, 105, 200)
mult = 2 ** ((105 - T) / 10)
fig, ax = plt.subplots(figsize=(6, 4.2))
ax.plot(T, mult, "C0", lw=2)
ax.axhline(1, color="k", ls=":", lw=1)
ax.axvline(105, color="k", ls=":", lw=1)
ax.set_yscale("log", base=2)
ax.set_xlabel("Capacitor hot-spot temperature (deg C)")
ax.set_ylabel("Lifetime multiplier vs rated endurance")
ax.set_title("UCS lifetime model: L = 10000 h x 2^((105 - T_hs)/10) [EST]")
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "DCLinkRippleLifetime.png"), dpi=150)
plt.close(fig)

print("\nPNGs written to", OUT)
