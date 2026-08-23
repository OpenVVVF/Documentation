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

# ---------------------------------------------------------------------------
# v0.2: three-branch DC-link structure and ripple current sharing
#
# Real structure (hardware designer, 2026-08):
#   - Ceramics: 12x TDK CeraLink B58031U9254M062 (4 per half-bridge),
#     sandwiched between the IGBT terminals. Own the commutation edge.
#   - Film: 6x Vishay MKP1848S DC-Link (2 per half-bridge), ~80-90 uF total,
#     on a board mounted directly on the busbars at the IGBT terminals.
#   - Electrolytics: 60x Nichicon UCS on the DC-link board ABOVE the film
#     board, connected through the aluminium rod standoffs (~40 mm rods).

# Ceramics [DS]: TDK product page B58031U9254M062 (CeraLink LP, 900 V):
#   250 nF nominal / 130 nF effective, ESL 3 nH, 5 A rms @ 100 kHz.
#   ESR: 40 mΩ class [ASM] (EIA-2220 CeraLink typical, not in the LP table).
CER = dict(n=12, C_each=130e-9, ESL_each=3e-9, ESR_each=40e-3,
           I_rated_each=5.0)  # at 100 kHz [DS]

# Film [DS]: Vishay MKP1848S DC-Link catalog 26010 (rev. 26-Mar-2024).
#   Assumed fitted part: 500 V class, 15 uF, h=15 mm, 4-pin
#   (MKP1848S61550JP*B): I_RMS 7 A @ 10 kHz/85 C, ESR 5 mΩ typ @ 10 kHz.
#   6 x 15 uF = 90 uF ~= the designer's "~80 uF total" [ASM: exact fitted
#   capacitance not confirmed; 13 uF intermediate value would give 78 uF].
#   ESL: catalog gives "self inductance < 1 nH per mm of lead spacing"
#   (pitch 37.5 mm); mounted 4-pin ESL taken as 20 nH [ASM].
FILM = dict(n=6, C_each=15e-6, ESR_each=5e-3, ESL_each=20e-9,
            I_rated_each=7.0)  # at 10 kHz, 85 C [DS]

# Electrolytic branch: 60-can UCS2D331MHD bank behind the rod standoffs.
# Rod loop inductance, parallel round conductors: L = (mu0/pi) * l * ln(s/r)
#   l = 63 mm one-way rod length (go and return form the loop),
#   r = 6.5 mm (13 mm OD standoff, DC-Link-Thermal geometry),
#   s = 50 mm nominal go-return spacing (thermal-doc cell radius; renders
#   show rods distributed across the module footprint), sweep 30-100 mm.
MU0 = 4 * np.pi * 1e-7
def rod_pair_L(l=0.063, s=0.050, r=0.0065):
    return MU0 / np.pi * l * np.log(s / r)

L_PAIR = rod_pair_L()
print(f"\nRod go-return pair inductance: {L_PAIR*1e9:.1f} nH "
      f"(l=63 mm, s=50 mm, r=6.5 mm); sweep s=30-100 mm: "
      f"{rod_pair_L(s=0.030)*1e9:.1f}-{rod_pair_L(s=0.100)*1e9:.1f} nH")

# 6 rods = 3 go-return pairs in parallel (one per phase module) [ASM];
# plus ~10 nH electrolytic-board/can-bank ESL [ASM].
L_ROD_BRANCH = L_PAIR / 3 + 10e-9   # ~27 nH nominal
L_ROD_SWEEP = (10e-9, 100e-9)       # [ASM] branch-inductance sweep range
print(f"Electrolytic branch inductance (3 parallel pairs + board ESL): "
      f"{L_ROD_BRANCH*1e9:.1f} nH nominal, sweep "
      f"{L_ROD_SWEEP[0]*1e9:.0f}-{L_ROD_SWEEP[1]*1e9:.0f} nH [ASM]")

def branch_impedances(f, l_rod=L_ROD_BRANCH):
    """Complex branch impedances of the three DC-link capacitor branches."""
    w = 2 * np.pi * np.asarray(f, dtype=float)
    # Electrolytic bank: bank ESR and C behind the rod + board inductance
    Z_ely = esr_f(CAP_200V, f) / N_CANS + 1j * (w * l_rod - 1 / (w * 19.8e-3))
    # Film bank
    Z_film = (FILM["ESR_each"] / FILM["n"]
              + 1j * (w * FILM["ESL_each"] / FILM["n"]
                      - 1 / (w * FILM["n"] * FILM["C_each"])))
    # Ceramic bank
    Z_cer = (CER["ESR_each"] / CER["n"]
             + 1j * (w * CER["ESL_each"] / CER["n"]
                     - 1 / (w * CER["n"] * CER["C_each"])))
    return Z_ely, Z_film, Z_cer

def branch_shares(f, l_rod=L_ROD_BRANCH):
    """Magnitude of each branch's share of a total ripple current injected
    into the three parallel branches (current divider on admittances)."""
    Z = branch_impedances(f, l_rod)
    Y = [1 / z for z in Z]
    Ytot = sum(Y)
    return [np.abs(y / Ytot) for y in Y]

print("\nRipple split at 600 A RMS phase current (bank ripple 307 A RMS):")
print(f"{'f_sw':>6} | {'I_ely (A)':>10} {'share':>7} {'per-can (A)':>12} "
      f"{'x rating':>9} | {'I_film (A)':>11} {'share':>7} {'x film rating':>14} "
      f"| {'I_cer (A)':>10} {'share':>7}")
for f in FREQS:
    s_ely, s_film, s_cer = branch_shares(f)
    i_tot = KF * 600
    i_ely, i_film, i_cer = i_tot * s_ely, i_tot * s_film, i_tot * s_cer
    ic = i_ely / N_CANS
    ir = CAP_200V["I_rated_100k"] * freq_coeff(f)
    film_rated = FILM["n"] * FILM["I_rated_each"]
    print(f"{f/1000:>5.0f}k | {i_ely:>10.1f} {s_ely*100:>6.2f}% {ic:>12.2f} "
          f"{ic/ir:>9.2f} | {i_film:>11.1f} {s_film*100:>6.2f}% "
          f"{i_film/film_rated:>14.2f} | {i_cer:>10.2f} {s_cer*100:>6.2f}%")

# Crossover frequency: |Z_ely| = |Z_film| (film takes over above this)
f_scan = np.logspace(3, 7, 4000)
Ze, Zf, Zc = branch_impedances(f_scan)
ix = np.argmin(np.abs(np.abs(Ze) - np.abs(Zf)))
print(f"\nFilm/electrolytic impedance crossover: ~{f_scan[ix]/1e3:.0f} kHz "
      f"(LC resonance of film C with rod L; sweep {L_ROD_SWEEP[0]*1e9:.0f}-"
      f"{L_ROD_SWEEP[1]*1e9:.0f} nH moves it "
      f"{1/(2*np.pi*np.sqrt(L_ROD_SWEEP[1]*90e-6))/1e3:.0f}-"
      f"{1/(2*np.pi*np.sqrt(L_ROD_SWEEP[0]*90e-6))/1e3:.0f} kHz)")

# ---------------------------------------------------------------------------
# Plot (d): branch impedance vs frequency
fig, ax = plt.subplots(figsize=(7, 4.6))
ax.loglog(f_scan, np.abs(Ze) * 1e3, "C3", lw=2,
          label=f"Electrolytic bank + rods ({L_ROD_BRANCH*1e9:.0f} nH)")
ax.loglog(f_scan, np.abs(Zf) * 1e3, "C0", lw=2,
          label=f"Film bank (6x MKP1848S, {FILM['n']*FILM['C_each']*1e6:.0f} uF)")
ax.loglog(f_scan, np.abs(Zc) * 1e3, "C2", lw=2,
          label="Ceramic bank (12x CeraLink)")
for f in FREQS:
    ax.axvline(f, color="k", ls=":", lw=1, alpha=0.5)
    ax.text(f * 1.1, 2e2, f"{f/1000:.0f} kHz", fontsize=8, rotation=90)
ax.axvline(f_scan[ix], color="C7", ls="--", lw=1)
ax.text(f_scan[ix] * 1.1, 2e2, f"crossover ~{f_scan[ix]/1e3:.0f} kHz",
        fontsize=8, rotation=90)
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Branch impedance |Z| (m$\\Omega$)")
ax.set_title("DC-link branch impedances vs frequency")
ax.grid(alpha=0.3, which="both")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "DCLinkRippleBranchImpedance.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot (e): per-branch ripple current share vs frequency
shares = np.array([branch_shares(f) for f in f_scan]) * 100
fig, ax = plt.subplots(figsize=(7, 4.6))
ax.semilogx(f_scan, shares[:, 0], "C3", lw=2, label="Electrolytic bank")
ax.semilogx(f_scan, shares[:, 1], "C0", lw=2, label="Film bank")
ax.semilogx(f_scan, shares[:, 2], "C2", lw=2, label="Ceramic bank")
for f in FREQS:
    ax.axvline(f, color="k", ls=":", lw=1, alpha=0.5)
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Share of total ripple current (%)")
ax.set_title("Ripple current sharing between DC-link branches")
ax.set_ylim(0, 105)
ax.grid(alpha=0.3, which="both")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "DCLinkRippleBranchShare.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot (f): per-can electrolytic ripple vs phase current, with and without
# the three-branch sharing (Bank A, 200 V)
fig, ax = plt.subplots(figsize=(6.5, 4.6))
ax.plot(I_phase, I_can, "k-", lw=2, label="No sharing (v0.1 model)")
for f in FREQS:
    s_ely, _, _ = branch_shares(f)
    ax.plot(I_phase, I_can * s_ely, color=colors[f], lw=1.5,
            label=f"With sharing, {f/1000:.0f} kHz")
for f in FREQS:
    ir = CAP_200V["I_rated_100k"] * freq_coeff(f)
    ax.axhline(ir, color=colors[f], ls="--", alpha=0.7,
               label=f"Rated ripple {f/1000:.0f} kHz: {ir:.2f} A")
ax.set_xlabel("Phase current (A rms)")
ax.set_ylabel("Per-can electrolytic ripple (A rms)")
ax.set_title("UCS2D331MHD bank: per-can ripple with/without branch sharing")
ax.grid(alpha=0.3)
ax.legend(fontsize=8)
ax.set_xlim(0, 600)
ax.set_ylim(0, None)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "DCLinkRipplePerCanShared.png"), dpi=150)
plt.close(fig)

print("\nPNGs written to", OUT)
