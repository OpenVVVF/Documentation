---
doctype: Design Document
doc_id: OV-C2-DD-DCLINK-THERMAL
title: DC Link Thermal Analysis
product_line: openvvvf
applies_to:
  - chassis-size-2
version: "1.3"
date: "2026-08-23"
description: DC-link capacitor bank standoff heat-path and thermal resistance analysis for Chassis Size 2.
nav_order: 242
normative_refs:
  - OV-C2-DD-INDEX
  - OV-C2-DD-THERMAL
---

# Thermal Analysis - DC Link Module Standoff Heat Path

Heat load at rated ripple was calculated to be 40 W across all capacitors.

> **Open item (v1.1) - addressed by `OV-C2-DD-DCLINK-RIPPLE` v0.1:** the derivation of the 40 W figure is not recorded in this document, and the ripple-current rating of the 60-can bank had not been checked against the full-load operating point. `OV-C2-DD-DCLINK-RIPPLE` derives the bank ripple current (0.511 A RMS per A of phase current RMS at m = 1, cos phi = 0.8) and checks it against the Nichicon UCS datasheet ratings: the 200 V bank is ripple-limited above ~330 A RMS (465 A peak) phase current - which sets the 330 A RMS continuous rating (`OV-C2-DD-THERMAL` v1.3 §6.4) - and at the 600 A peak (424 A RMS) design point the per-can ripple is 1.28x the 6 kHz rating with a computed bank loss of ~110 - 125 W (subject to the [ASM] ESR ratio there; at the 600 A RMS / 848 A pk sweep bound it is 1.8 - 1.9x and 239 - 274 W). Its v0.2 also models the real three-branch DC link (CeraLink ceramics + MKP1848S film at the IGBT terminals, electrolytics behind the rod standoffs): the film/ceramic branches divert only ~1 % of the switching-frequency ripple, so the electrolytic verdict is unchanged. The 40 W figure corresponds to ~240 A RMS operation; it is about right at part load and optimistic by ~3x at the 424 A RMS design point. Note, however, that the ripple loss is generated in the can hot-spot and is partly rejected by convection/radiation, which this conduction-only model neglects, so the +32.4 K rise (even rescaled) is an upper bound; the designer's field experience is that the cans run much cooler than this model predicts. Until the ESR measurement and dyno correlation in `OV-C2-DD-DCLINK-RIPPLE` open items land, every absolute plate temperature in this document carries an unquantified upward bias risk. [ASM]

## Nomenclature

| Symbol | Meaning | Units |
|---|---|---|
| $A$ | Cross-sectional area (generic) | m² |
| $A_{standoff}$ | Cross-sectional area of one standoff | m² |
| $k$ | Thermal conductivity (generic material) | W/(m·K) |
| $k_{Al}$ | Thermal conductivity of the aluminium heat-spreader plate | W/(m·K) |
| $k_{standoff}$ | Thermal conductivity of the standoff material | W/(m·K) |
| $L$ | Standoff length (thermal conduction path) | m |
| $n$ | Number of standoffs | - |
| $Q$ | Heat flow from capacitor bank ripple current | W |
| $r_{cell}$ | Effective radius of the aluminium spreading cell around one standoff | m |
| $r_{inner}$ | Standoff inner (hole) radius | m |
| $r_{outer}$ | Standoff outer radius | m |
| $r_{standoff}$ | Standoff outer radius (used in spreading model) | m |
| $R_{contact}$ | Contact resistance across one standoff-to-plate or standoff-to-heatsink interface pair | K/W |
| $R_{spread}$ | Aluminium heat-spreader plate spreading resistance | K/W |
| $R_{standoff}$ | Standoff conduction thermal resistance | K/W |
| $R_{th}$ | Generic thermal resistance | K/W |
| $t_{Al}$ | Aluminium heat-spreader plate thickness | m |
| $\Delta T$ | Temperature rise / difference | K or °C |
| $\rho_{contact}$ | Contact resistivity | m²·K/W |

## Methodology

All calculations use one-dimensional steady-state thermal resistance:

$$\Delta T = Q \times R_{th}$$

where

$$R_{th} = \frac{L}{k \, A}$$

Total system resistance is the sum of three series components:

1. **Standoff conduction**
   $$R_{standoff} = \frac{L}{k_{standoff} \, A_{standoff} \, n}$$
2. **Contact resistance** (both faces in series)
   $$R_{contact} = \frac{2 \, \rho_{contact}}{n \, A_{standoff}}$$
3. **Aluminium spreading**
   $$R_{spread} \approx \frac{\ln(r_{cell} / r_{standoff}) - 0.5}{2\pi \, k_{Al} \, t_{Al}}$$

### Material properties

| Material | Thermal conductivity $k$ [W/(m·K)] |
|----------|-------------------------------------|
| Aluminium (6063 / generic) | 200 |
| Brass (C36000) | 120 |
| Copper (C11000) | 400 |
| Carbon steel | 50 |
| 18-8 Stainless steel | 16 |

### Contact resistivity values

| Condition | Resistivity $\rho_{contact}$ [m²·K/W] |
|-----------|--------------------------------------|
| Dry metal-to-metal | $1.0 \times 10^{-4}$ |
| With thermal paste / thin pad | $5.0 \times 10^{-5}$ |

### Geometry constants

- Heat-spreader plate: 6.35 mm (1/4 in) thick aluminium *(HW-C2-PLT-CHSP-B; thickened from 3.18 mm in rev A for better heat dissipation and capacitor height clearance — this halves the spreading resistance compared with v1.2 and earlier, which used 3.18 mm)*
- Standoff length: 55 mm (final design)
- Number of standoffs: 6 (final design)
- Standoff spacing: assumed ~100 mm centre-to-centre (spreading cell radius $r_{cell} \approx 50$ mm)

---

## Design Evolution

### Initial concepts (for reference)

| Configuration | $k$ [W/m·K] | Area [mm²] | $R_{standoff}$ [K/W] | $\Delta T_{standoff}$ [°C] | Total $\Delta T$ (paste) [°C] |
|-------------|-------------|------------|----------------------|---------------------------|-------------------------------|
| 8 mm hex brass, hollow M5 | 120 | 35.8 | 2.13 | 85.4 | 123 |
| 10 mm hex Al, hollow M5 | 200 | 67.0 | 0.684 | 27.4 | 53.9 |
| 16 mm round Al, hollow M8 | 200 | 150.8 | 0.304 | 12.2 | 29.9 |
| 16 mm round Al, solid | 200 | 201.1 | 0.228 | 9.1 | 25.8 |

*All at 40 W, 6 standoffs, 55 mm long. Values rounded.*

### Selected design - 13 mm round aluminium spacers

**Final part specification:**
- Outer diameter: 13.0 mm
- Inner diameter (M6 clearance): 6.3 mm  
  *(Note: M6 major diameter = 6.0 mm; 6.3 mm ID provides thread engagement or clearance depending on part type)*
- Wall thickness: 3.35 mm
- Length: 55 mm
- Material: Aluminium
- Thread: M6 × 1 (male-female or through-hole with bolt)
- Quantity: 6

**Cross-sectional area:**

$$A = \pi (r_{outer}^2 - r_{inner}^2) = \pi (6.5^2 - 3.15^2) \times 10^{-6} = 101.6 \times 10^{-6} \ \text{m}^2$$

---

## Final Design Calculation

### Standoff conduction resistance

$$R_{standoff} = \frac{L}{k_{Al} \, A \, n} = \frac{0.055}{200 \times 101.6 \times 10^{-6} \times 6} = 0.451 \ \text{K/W}$$

$$\Delta T_{standoff} = 40 \times 0.451 = \mathbf{18.1 \ ^\circ\text{C}}$$

### Contact resistance (both faces)

With thermal paste:

$$R_{contact} = \frac{2 \times 5.0 \times 10^{-5}}{6 \times 101.6 \times 10^{-6}} = 0.164 \ \text{K/W}$$

$$\Delta T_{contact} = 40 \times 0.164 = \mathbf{6.6 \ ^\circ\text{C}}$$

Dry metal-to-metal:

$$R_{contact} = \frac{2 \times 1.0 \times 10^{-4}}{6 \times 101.6 \times 10^{-6}} = 0.328 \ \text{K/W}$$

$$\Delta T_{contact} = 40 \times 0.328 = \mathbf{13.1 \ ^\circ\text{C}}$$

### Aluminium spreading resistance

$$R_{spread} = \frac{\ln(50 / 6.5) - 0.5}{2\pi \times 200 \times 0.00635} \approx 0.193 \ \text{K/W}$$

$$\Delta T_{spread} = 40 \times 0.193 = \mathbf{7.7 \ ^\circ\text{C}}$$

*(Spreading resistance is independent of standoff material; it depends only on plate conductivity, thickness, and cell geometry. The rev-B plate at 6.35 mm halves this term versus the 3.18 mm rev-A plate — 0.193 vs 0.385 K/W.)*

### Total temperature rise

| Condition | $\Delta T_{total}$ |
|-----------|---------------------|
| **With thermal paste** | $18.1 + 6.6 + 7.7 = \mathbf{32.4 \ ^\circ\text{C}}$ |
| Dry metal-to-metal | $18.1 + 13.1 + 7.7 = \mathbf{38.9 \ ^\circ\text{C}}$ |

### Absolute temperatures (heatsink base = 40 °C)

| Condition | Aluminium plate temperature |
|-----------|----------------------------|
| With thermal paste | **~72 °C** |
| Dry metal-to-metal | **~79 °C** |

The table above assumes a 40 °C heatsink base. Under inverter load the heatsink surface is much warmer than that; because the 32.4 K rise is a series resistance to the heatsink, the plate tracks the local heatsink surface 1:1. See the next subsection.

### Plate temperature at the inverter operating points (v1.3)

`OV-C2-DD-THERMAL` v1.3 derives the maximum heatsink surface temperature $T_s$ for each operating point (heatsink sized to the 85 °C module-baseplate limit, 40 °C ambient, $R_G = 2.7 \ \Omega$ gate drive; design point 424 A RMS = 600 A peak). Adding the +32.4 K paste-path rise (rev-B 6.35 mm plate):

| Operating point | Max $T_s$ (°C) | Plate temperature (°C, upper bound) |
|-----------|----------------------------|----------------------------|
| 424 A rms (600 A pk) / 320 V / 2 kHz | 74.4 | **106.8** |
| 424 A rms (600 A pk) / 320 V / 6 kHz (60 s peak duty) | 70.8 | **103.2** |
| 424 A rms (600 A pk) / 320 V / 8 kHz (beyond envelope) | 69.0 | **101.4** |
| 424 A rms (600 A pk) / 140 V / 2 kHz | 75.3 | **107.7** |
| 424 A rms (600 A pk) / 140 V / 6 kHz | 73.8 | **106.2** |
| 330 A rms (465 A pk) / 320 V / 6 kHz (continuous rating) | 74.2 | **106.6** |

These rows size the heatsink exactly to the 85 °C baseplate limit at each point; against a **fixed** 0.006 K/W margin-target heatsink the plate bound is much lower: 424 A RMS / 320 V gives $T_s \approx 55 / 59$ °C at 2 / 6 kHz, i.e. plate ≈ **87 / 92 °C**, and the 330 A RMS continuous point gives $T_s \approx 55$ °C, plate ≈ **87 °C**. Per `OV-C2-DD-THERMAL` v1.3 the plate temperature is an **informational upper bound on the capacitor environment**, not a pass/fail rating constraint: the governed quantity is the capacitor can temperature (ripple rating and hot-spot), and the conduction-only model here neglects convection/radiation, so real plate/can temperatures are expected to be materially lower.

**Consequence and resolution (v1.3):** the adopted rating is **465 A peak (330 A RMS) continuous / 600 A peak (424 A RMS) for 60 s** (`OV-C2-DD-THERMAL` §6.4), set by the electrolytic ripple limit. With the rev-B plate:

- **At the 330 A RMS continuous rating (6 kHz, 0.006 K/W heatsink):** $T_s \approx 55$ °C at 320 V, plate bound ≈ **87 °C** - below the FSR-08 90 °C derate onset even on this no-convection bound (the rev-A 3.18 mm plate gave ≈ 95 °C, above onset; and before that, the plate bound at 220 A RMS sat exactly at onset). The plate path no longer constrains the continuous rating.
- **At the 600 A peak (424 A RMS) / 60 s:** the steady-state plate bound at the peak point is ≈ 92 °C (0.006 K/W heatsink); with the minutes-class plate+heatsink time constant [EST], a compliant 60 s peak from the continuous point captures only a fraction of the ~5 K delta: end-of-peak plate ≈ **88 - 89 °C**, below the 90 °C derate onset. The rolling 10-min RMS ≤ 330 A RMS duty requirement remains the verifiable peak-duty definition.
- Raising the continuous rating beyond 330 A RMS requires capacitor-bank changes (ripple-limited; see `OV-C2-DD-DCLINK-RIPPLE`) - the plate path has margin to spare after rev B. Plate-thermocouple and can-NTC validation during the dyno (thermal test plan T-05) would quantify how conservative this bound is. [ASM] - plate-to-capacitor-can thermal coupling is unmodeled; the capacitor NTC reading vs plate temperature must be correlated on the dyno, and the NTC mounting location (plate vs can) is an open item in `OV-C2-DD-THERMAL` v1.3.

**450 V capacitor-only upgrade:** The 450 V upgrade is a single part-number swap to 60&times; Nichicon UCS2W680MHD 68 &micro;F / 450 V capacitors (4.08 mF total). These parts are 5 mm shorter than the 200 V UCS2D331MHD, so the standoff length is reduced by 5 mm (from 55 mm to 50 mm). The same 13 mm OD aluminium standoff thermal path applies, with marginally lower conduction resistance due to the shorter length.

---

## Sensitivity & Margin

### Effect of standoff material

If stainless steel (18-8, $k = 16$ W/m·K) were used instead of aluminium:

$$\Delta T_{standoff} = \frac{40 \times 0.055}{16 \times 101.6 \times 10^{-6} \times 6} \approx 226 \ ^\circ\text{C}$$

**Total rise would exceed 240 °C.** Stainless steel is **not acceptable** for this thermal path.

### Effect of quantity

| Standoff count | $R_{standoff}$ [K/W] | $\Delta T_{standoff}$ [°C] | Total $\Delta T$ (paste) [°C] |
|----------------|----------------------|---------------------------|-------------------------------|
| 4 | 0.677 | 27.1 | 41.4 |
| 6 (selected) | 0.451 | 18.1 | 32.4 |
| 8 | 0.338 | 13.5 | 27.8 |

Six standoffs provides adequate margin; eight would be better but is not required at 40 W.

### Effect of length

| Length [mm] | $\Delta T_{standoff}$ [°C] | Total $\Delta T$ (paste) [°C] |
|-------------|---------------------------|-------------------------------|
| 30 | 9.9 | 24.2 |
| 55 (selected) | 18.1 | 32.4 |
| 65 | 21.4 | 35.7 |

---

## Recommendations

1. **Use aluminium standoffs/spacers only.** Do not substitute stainless or carbon steel.
2. **Apply thermal paste** (or a thin graphite / indium thermal pad) at both the plate-to-standoff and standoff-to-heatsink interfaces. This saves ~6.5 °C and improves long-term thermal stability.
3. **Ensure adequate clamping force** on the M6 bolts to minimize contact resistance. Target ~5–10 N·m on steel bolts into aluminium.
4. **Verify standoff placement** is reasonably distributed across the plate. Uneven distribution will increase local spreading resistance and hot-spot temperatures.
5. **If power increases above ~60 W**, consider upgrading to 8 standoffs or thicker-wall spacers (e.g., 16 mm OD / 6 mm ID).

---

## Assumptions & Limitations

- One-dimensional conduction assumed; actual 3D spreading may vary ±20 %.
- Contact resistivity values are typical estimates; actual values depend on surface finish, flatness, and clamping pressure.
- Heat generation is assumed uniform across the aluminium plate. Localised hot spots will increase peak temperatures.
- Radiation and natural convection from the plate are neglected; in reality they provide additional heat rejection, so actual plate temperature may be slightly lower.
- Ambient / heatsink base temperature is assumed constant at 40 °C; if the heatsink warms up under load, the absolute plate temperature rises proportionally. This is not hypothetical: at the 600 A peak (424 A RMS) operating points the heatsink surface reaches 69–75 °C (`OV-C2-DD-THERMAL` v1.3), putting the plate bound in the FSR-08 derate/SSO band on an exactly-sized heatsink - see "Plate temperature at the inverter operating points" above. On the 0.006 K/W margin-target heatsink the plate bound stays below the 90 °C derate onset at the continuous rating.
- The 40 W heat load is under review (open item at the top of this document); if the bank ripple check shows a higher loss, all $\Delta T$ values scale linearly with heat load.

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-13 | Initial release. |
| 1.1 | 2026-08-20 | Engineering revision. Added normative reference to `OV-C2-DD-THERMAL`. Flagged the 40 W ripple heat load as an open item: derivation not recorded and the 60-can bank ripple rating at 600 A RMS not yet checked (bank may be ripple-limited; heat load may be higher). New subsection "Plate temperature at the inverter operating points" integrates the v1.1 heatsink surface temperatures from `OV-C2-DD-THERMAL` (plate = $T_s$ + 40.1 K): the plate exceeds the FSR-08 90 °C derate threshold at every full-load point and the 105 °C SSO / capacitor rating at several, making the DC-link plate the binding constraint on the 600 A continuous claim. Assumptions updated accordingly. |
| 1.2 | 2026-08-20 | Ratings alignment. Conclusion restated against the adopted rating (220 A RMS continuous / 600 A RMS peak for 60 s, `OV-C2-DD-THERMAL` §6.4): at the continuous point the plate sits at 90.0 °C (320 V) / 87.5 °C (140 V), i.e. at or below the FSR-08 derate onset; the 60 s peak produces a bounded excursion to ~92 - 97 °C end-of-peak via the minutes-class plate/heatsink time constant, staying ≥8 K below the 105 °C SSO. The 600 A rows of the plate table are relabeled as 60 s peak duty; 8 kHz marked beyond the clamped envelope. The plate remains the constraint that sets the 220 A continuous figure. |
| 1.3 | 2026-08-23 | Rev-B heat-spreader plate (HW-C2-PLT-CHSP-B, 6.35 mm, thickened from 3.18 mm for better heat dissipation and capacitor height clearance) plus the `OV-C2-DD-THERMAL` v1.3 convention correction (600 A = peak = 424 A RMS) and re-rating. Spreading resistance halves (0.385 → 0.193 K/W); paste-path rise 40.1 → 32.4 K. Operating-point table rebuilt on the v1.3 heatsink surface temperatures (424 A RMS design point). Continuous rating raised to **465 A peak (330 A RMS)**, set by the electrolytic ripple limit: at the continuous point the plate bound is ≈ 87 °C (320 V, 0.006 K/W heatsink), below the FSR-08 derate onset, so the plate no longer constrains the rating and plate numbers are informational upper bounds on the capacitor environment per `OV-C2-DD-THERMAL` v1.3 framing. Peak restated as **600 A peak (424 A RMS) for 60 s**; end-of-peak plate ≈ 88 - 89 °C. Sensitivity tables and the stainless-substitution total recomputed. |

---

*Prepared for DC link module thermal design review.*
