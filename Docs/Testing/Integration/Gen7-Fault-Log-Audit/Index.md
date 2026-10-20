---
doctype: Test Report
doc_id: OV-TEST-INT-FAULT-LOG-AUDIT
title: Gen7 Persisted Fault Log Download and Audit
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - application-profile-motorcycle
version: "0.1"
date: "2026-10-19"
description: First full download of the Gen7 control board's reboot-persisted in-memory fault log after the first two road rides; 29 records across 12 boots expose three recurring failure modes plus two one-off records, and confirm the log's intended post-incident retrieval workflow.
test_id: 13
nav_order: 374
normative_refs:
  - OV-TEST-INT-INDEX
---

# Gen7 Persisted Fault Log Download and Audit

After the two Zero DSR road rides ([test 11](../Zero-DSR-Road-Test/Index.md), [test 12](../Zero-DSR-Road-Test-2/Index.md)) the Gen7 control board was noticed to be accumulating faults that neither the live telemetry stream nor the console surfaces after the fact. This test is the first deliberate download of the board's **persisted in-memory fault log**: an RTE Android session (TLM1, live mode) connected to the stationary vehicle, during which the board replays its retained fault records over the `fault_log_record` signal, reports the newest entry on `fault_log_latest`, and advertises the retained count on `fault_log_count`.

**Summary: 29 persisted records covering 12 boots; three recurring failure modes (FDCAN error-passive at startup, coprocessor-safety latch records, software phase overcurrent) plus two one-off records (RAM ECC status IRQ, DC-link current feedback declared invalid). Nothing new was latched during the 103 s diagnostic connect itself, and no fault was live while connected.**

All numbers below are recomputed from the raw session export by `parse_fault_log.py` in this folder, which streams the zstd-compressed capture and decodes every record field structurally; fields whose semantics are not documented are printed raw and left labelled *unknown* rather than given an invented meaning.

## Test article and setup

- **Vehicle / test article:** identical to tests 11/12 — Zero DSR (MY2018), stock Z-Force motor, Gen7 control board on the vehicle harness, stationary (kickstand, no ride).
- **Logging:** RTE Android over USB, protocol TLM1, live mode, port "Control Board Gen 7". Session export `raw/runtime-session-2026-10-19T10-56-50.375Z-17521eb9.jsonl.zst` in `Data/Tests/INT-Gen7-Fault-Log-Audit/raw/` (48.5 MB decompressed, zstd-compressed); 102.7 s live window, full signal set.
- **Board state at connect:** motor control was already RUNNING when the session opened (`control_state` RUNNING from t = 1.34 s, board armed / gate power on), the motor was idle throughout (display rpm within −1.8 … +16.5 rpm, torque current within −3.4 … +2.7 A — sensor noise, no commutation).

## Session integrity

The export's `session_end` statistics report **21 608 good frames**, 1 `reject_header`, 0 CRC/length/payload rejects, and **4 260 `reject_unknown_id`** frames. The unknown-ID rejects are an evolving-protocol edge (the app meeting frame IDs newer than its decoder), not corruption of the stored evidence; they are logged as a follow-up below.

## The persisted log: 29 records across 12 boots

During the connect the board streamed the log as `fault_log_record` state lines. Each of the 29 unique sequence numbers was replayed 14–15 times (410 state samples in total — the board periodically re-streams the whole log, which is exactly what a passive diagnostic download needs); `fault_log_count` held at 29 in all 102 samples, and `fault_log_latest` pointed at the newest record (seq 29). The table lists one row per unique record; `boot ms` is the board millisecond clock within that boot, so records near 2 300–2 400 ms are startup-phase events.

| Seq | Boot | Boot ms | Sev | Source | Reason | Key fields |
|-----|------|---------|-----|------------------------|----------------------|---------------------------------------------------------|
| 1 | 1 | 2408 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 2 | 1 | 2403 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 12, generation 0x3, age 51 ms, trip reason/inputs = invalid (0xFF…) |
| 3 | 1 | 50370 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 17, generation 0x3, age 208 ms, reason 0x4, inputs 0x9 |
| 4 | 1 | 676587 | 2 | PhaseOvercurrent | software overcurrent | iu 2218.97 A, iv −1114.08 A, iw −1104.89 A, iq −2807.99 A, id −627.60 A, limit 1100 A |
| 5 | 2 | 2282 | 2 | RamEcc | RAM ECC status or IRQ | monitor 9, sr 2, far 0, fdrl EA62C0B2, fecr 0x60 (bit semantics unknown) |
| 6 | 2 | 2291 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 12, generation 0x3, age 50 ms, trip reason/inputs invalid |
| 7 | 2 | 2785 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 17, generation 0x3, age 38 ms, reason 0x4, inputs 0x9 |
| 8 | 3 | 2397 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 9 | 3 | 2394 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 12, generation 0x3, age 50 ms, trip reason/inputs invalid |
| 10 | 3 | 2394 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 17, generation 0x3, age 326 ms, reason 0x4, inputs 0x9 |
| 11 | 3 | 158006 | 2 | PhaseOvercurrent | software overcurrent | iu 2281.60 A, iv −1144.19 A, iw −1137.42 A, iq −2848.31 A, id −782.00 A, limit 1100 A |
| 12 | 4 | 2296 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 13 | 5 | 2399 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 14 | 6 | 2396 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 15 | 6 | 370559 | 2 | DcLinkCurrentFeedback | DC-link current uncalibrated, invalid or stale | current −0.487 A, age 4 ms, calibrated=1, valid=0, iq −0.422 A, iq request 0 |
| 16 | 6 | 370565 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 12, generation 0x9, age 50 ms, trip reason/inputs invalid |
| 17 | 6 | 370565 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 17, generation 0x9, age 76 ms, reason 0x4, inputs 0x8 |
| 18 | 7 | 2409 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000076B ecr=00100080 |
| 19 | 7 | 2405 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 12, generation 0x9, age 50 ms, trip reason/inputs invalid |
| 20 | 7 | 2591 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 17, generation 0x9, age 151 ms, reason 0x4, inputs 0x8 |
| 21 | 8 | 2407 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 22 | 8 | 2407 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 12, generation 0x9, age 50 ms, trip reason/inputs invalid |
| 23 | 8 | 2407 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 17, generation 0x9, age 321 ms, reason 0x4, inputs 0x8 |
| 24 | 9 | 2307 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 25 | 10 | 2400 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 26 | 11 | 2408 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 27 | 12 | 2403 | 0 | CanErrorPassive | FDCAN error-passive | psr=0000077B ecr=00100080 |
| 28 | 12 | 3464552 | 2 | PhaseOvercurrent | software overcurrent | iu −179.19 A, iv 1191.07 A, iw −1011.88 A, iq 1255.77 A, id −160.67 A, limit 1100 A |
| 29 | 12 | 3464556 | 2 | CoprocessorSafety | coprocessor safety fault latched | kind 12, generation 0x0C, age 50 ms, trip reason/inputs invalid |

Per-boot roll-up:

| Boot | Records | Content |
|------|---------|---------|
| 1 | 4 | FDCAN passive + 2× coprocessor-safety + phase overcurrent |
| 2 | 3 | RAM ECC + 2× coprocessor-safety |
| 3 | 4 | FDCAN passive + 2× coprocessor-safety + phase overcurrent |
| 4, 5 | 1 each | FDCAN passive only |
| 6 | 4 | FDCAN passive + DC-link feedback + 2× coprocessor-safety |
| 7, 8 | 3 each | FDCAN passive + 2× coprocessor-safety |
| 9, 10, 11 | 1 each | FDCAN passive only |
| 12 | 3 | FDCAN passive + phase overcurrent + coprocessor-safety (latest record) |

Source counts: CoprocessorSafety 13, CanErrorPassive 11, PhaseOvercurrent 3, RamEcc 1, DcLinkCurrentFeedback 1. Severities: 0 ×11, 2 ×18.

![Fault-log records by boot number and in-boot time; the startup latch band (~2.4 s) vs mid-boot terminal faults](fig-01-fault-log-timeline.png)

Two opaque fields are uniform across records and are quoted raw rather than interpreted. `bdtr` is `02001CC1` on 27 records and `02009CC1` on exactly the two different records of boot 6's DC-link fault and boot 12's overcurrent; `ccer` is `00000000` everywhere except those same two records, which carry `00000555`. `ccer` plausibly acts like a capture-flags register switch-flipped alongside `bdtr` on those fault captures; bit semantics are **unknown** and the two distinct `bdtr` values are noted here only for future correlation against the gate-driver fault registers. The `gate` field cycles through 1/4/5/7 with no documented meaning.

## Failure mode analysis

### FDCAN error-passive at every boot startup

The **CanErrorPassive** record (severity 0, firmware reason id 14, "FDCAN error-passive") appears at boot ms ≈ 2 300–2 410 in 11 of the 12 boots — boot 2 is the single exception and it instead latched the RAM ECC record. The raw `psr` snapshot is identical in 10 boots (`0000077B`; `0000076B` in boot 7) and `ecr` is always `00100080`. The constancy of both the timing and the register snapshots says this is a **mechanism, not a random event**: at roughly 2.4 s after the boot clock starts, the FDCAN cell accumulates enough errors to enter the error-passive state, with essentially the same error-counter signature every time. The most plausible reading is startup bus contention — a peer node (BMS, display, or another controller) hammering the bus before the Gen7 board completes its init and starts answering — but **purity of evidence**: no CAN-frame-level capture exists here, so "which peer" and even "transmit vs receive error counting" cannot be separated from these registers alone. Severity 0 means the event is logged for observability, not treated as a fault, and the bus recovers (all rides afterwards ran with live vehicle-pack CAN telemetry correctly received). Follow-up: probe the bus state around boot (a CAN trace on the vehicle harness during power-up, or instrument `psr/ecr` deltas in firmware at ±100 ms resolution) and consider init-order hardening (start the error handler/threshold after bus-off recovery rather than latching this boot-phase transition at all).

### Coprocessor-safety latch records — persisted-latch replay pattern

Thirteen **CoprocessorSafety** records (severity 2, reason id 56, "coprocessor safety fault latched") come in two structurally distinct shapes:

- **kind 12** (6 records) — `trip_reason`/`trip_inputs` are `FFFFFFFF` (unset/invalid), age is essentially constant at 50–51 ms, generation is per power-cycle group (0x3 for boots 1–3, 0x9 for boots 6–8, 0x0C for boot 12). A kind-12 record appears either **at boot-up (~2.4 s)** in boots 1, 2, 3, 7, 8 — or **4–6 ms after a terminal severity-2 fault in the same boot** (boot 6: 6 ms after the DC-link fault; boot 12: 4 ms after the overcurrent — and the boot-12 record is `fault_log_latest`).
- **kind 17** (7 records) — always `trip_reason 0x4` with `trip_inputs 0x9` in generation-3 boots and `0x8` in generation-9 boots, age variable (38–326 ms).

The chronology strongly suggests the kind-12/17 pairs that appear **at boot-up are a replay of the persisted latch**: boots never begin with a clean slate after a boot that ended on a severity-2 fault. Boot 1 ended its history on the overcurrent at 676 s; boot 2 opens with a coprocessor-safety pair (~2.3–2.8 s) plus the RAM ECC record. Boot 2's pair stands immediately behind the ECC latch; boot 3 again opens with a pair, then latched its own overcurrent at 158 s. Boot 6 ran clean until the DC-link fault at 370.6 s and latched its pair in the same boot; boots 7 and 8 then both opened with startup pairs replaying that same generation-9 latch — no new terminal fault in between, consistent with a latch that stays set across power cycles once raised. Boots 9–11 then show *no* startup pair, so the latch was presumably cleared (or rotated out) after boot 8; how clearing works is **unknown** from this data. Boots 11/12 plausibly correspond to the 2026-10-16 rides of tests 11/12 — boots carry no calendar timestamps, so the mapping is provisional, but the boot-12 overcurrent at 3 464.6 s of boot time (≈57.7 min of running — a full day of riding including the test-12 evening run) and the fresh latch 4 ms later fit the chronology.

The positive finding: **the log survives reboots and is retrievable by an ordinary telemetry session** — this session is exactly the post-incident-retrieval workflow the mechanism was designed for, and it works end to end. Follow-ups, before relying on these records in safety arguments: pin down the exact semantics of kind 12 vs 17, of `trip_reason 0x4` / `trip_inputs 0x8/0x9`, and of the generation counter, against the safety documentation and the fault-injection campaign ([OV-TEST-FAULT-INJECTION](../../Fault-Injection-Test-Plan/Index.md)), including how a latch is cleared.

### Software phase overcurrent ×3 — protection now latching on the glitch-like family

Three **PhaseOvercurrent** records (severity 2, reason id 4, "software overcurrent"; limit field = 1100 A on all three) carry fully coherent three-phase content: the boot-1 and boot-3 events are near images of each other (iu ≈ +2.2 kA, iv and iw ≈ −1.1 kA, summing to zero as a motor winding must; iq ≈ −2.8 to −2.85 kA, consistent with hard regen or a sign-convention inversion on a motoring spike), while the boot-12 event shows the opposite iq sign (+1 255.8 A) with the same zero-sum three-phase structure. This is the same pattern family as the ±800 A single-sample glitches documented on the phase-current channels in test 12 — but the magnitude now exceeds the **1 100 A software-protection threshold**, and the protection did its job: it latched at severity 2, and the boot-12 event raised the coprocessor-safety latch 4 ms later. This is no longer just telemetry noise.

Two honest observations limit the interpretation:

- **Coherence argues against pure single-sample ADC noise.** The three phase values sum to zero with the expected 120°-family proportions in all three events; an independent per-channel sample corruption would not produce that. If the capture is wrong, it is wrong as a coherent vector.
- **The magnitudes are physically impossible for this system.** 2.2–2.8 kA against an 1 100 A software limit and a drive whose genuine peaks are ~750 A (test 12: 753 A median peak, 792 A raw) cannot be literal motor current sustained long enough to be sampled by the control cycle — the hardware overcurrent comparators would have won the race.

The residual explanations are: a scaling/unit or capture-path computation bug in the fault-record writer (e.g. the snapshot taken in different units than the limit, or post-multiplied), a genuine single-PWM-cycle transient that the digital comparator correctly caught at absurd amplitude, or a real but extremely short bus event aliased by the `iq/id` snapshot. Distinguishing them needs one deliberate overcurrent injection under observation (see follow-ups); the presence of `iq id` with the same factor as `iu/iv/iw` (approximately −1.26×) points toward a common transform/scaling stage rather than three independent analog front errors.

### One-off records

- **DcLinkCurrentFeedback** (boot 6, 370 559 ms, severity 2, reason id 62, "DC-link current uncalibrated, invalid or stale") with `calibrated=1`, `valid=0`, `age 4 ms`, `iq request 0`, measured −0.487 A. The sensor was calibrated but its value was flagged invalid at 4 ms of age, at zero current request and near-zero measured current — a benign operating point failing a validity gate that then latched the coprocessor-safety pair 6 ms later. One occurrence; watch it, and correlate with the DC-link sensor health if it recurs.
- **RamEcc** (boot 2, 2 282 ms, severity 2, reason id 54): a RAM ECC status/IRQ record at startup with `fdrl EA62C0B2` and `fecr 0x60` (register-level semantics undocumented; `monitor 9`, `far 0`). One occurrence, replacing that boot's usual FDCAN error-passive slot. Treated as aleatory unless it recurs; adding ECC-correctable-error counters to the live telemetry would settle whether it is noise or an early workspace-health signal.

## The diagnostic connect itself (session evidence)

The connection did not perturb the board; equally, the board grew nothing new:

- **Operator action:** the operator issued one command, `control stop` at t = 5.99 s; the console replied `[SUP] STOPPED` and `[SHELL] control stopped: MAIN motor control (RTE graph)` at t = 6.01 s. This was a deliberate user stop of the (idle) control loop, not a fault.
- **`gate_reset_asserted` went 0 → 1 at t = 6.01 s** and stayed latched — the expected disarmed latch after a control stop, matching the behavior documented in tests 11/12.
- **No live fault activity:** every live fault flag stayed `0x0` throughout the session; `fault_log_count` never moved off 29, so **no record was created by the diagnostic session itself**.
- **Log retention across reboots is confirmed end-to-end** by the successful replay of 29 records (each unique record streamed 14–15 times during the window) for boots that span at least the road-test period.

## Findings and follow-ups

1. **Overcurrent protection fired three times on the glitch-like current family.** Now severity-2 latches with coherent 3-phase fields and the coprocessor-safety latch 4–6 ms after the boot-12 event. Investigate ADC scaling/units in the fault-record writer versus the 1 100 A limit, and run one controlled software-overcurrent injection (see [OV-TEST-FAULT-INJECTION](../../Fault-Injection-Test-Plan/Index.md)) with high-rate phase capture to resolve "scaling bug vs real transient". Until resolved, treat every such latch as a real protection event for operational purposes.
2. **FDCAN error-passive at every boot (11/12) is a mechanism.** Probe bus state around power-up (CAN trace; firmware-side psr/ecr sampling at ±100 ms) and consider init-order hardening so the documented startup contention does not pollute the log.
3. **Coprocessor-safety latch semantics are half-unknown.** kind 12 vs 17, `trip_reason 0x4`, `trip_inputs 0x8/0x9`, generation counting, and the clearing rule need to be verified against the safety documentation before these records are cited in safety arguments; fold latch-replay verification into [OV-TEST-FAULT-INJECTION](../../Fault-Injection-Test-Plan/Index.md).
4. **DC-link feedback one-off (boot 6).** Watch; if it recurs, correlate with DC-link sensor health. `calibrated=1 valid=0 age 4 ms iq_request 0` is the signature to match.
5. **RAM ECC one-off (boot 2).** Watch; expose ECC error counters in live telemetry to convert this from aleatory to measurable.
6. **4 260 unknown-ID frame rejects.** Protocol drift between the firmware's frame set and the app decoder as frames grow; regenerate the signal dictionary and re-test (no evidence lost in this session — the fault-log signals decoded fine).
7. **Adopt automatic fault-log exports for future rides.** The log replayed reliably over a passive TLM1 connect; make the export part of the post-ride routine so ride-linked records (boots 11/12 here) are captured before any future log rotation.

## Artifacts

| Artifact | Path |
|----------|------|
| Raw telemetry session | `Data/Tests/INT-Gen7-Fault-Log-Audit/raw/runtime-session-2026-10-19T10-56-50.375Z-17521eb9.jsonl.zst` (48.5 MB decompressed → 2.4 MB zstd) |
| Parse script (this report) | `parse_fault_log.py` in this folder — streams the zstd raw log, extracts the 29 records, prints the table and boot/source/severity summary; every number above is reproducible from it |
| Figure script + figure | `figures.py` in this folder (regenerates `fig-01-fault-log-timeline.png` from the raw log) |
