# Recording review — 19 October 2026

All four original JSONL files are structurally intact. Full streaming validation
covered **9,640,893 records**, including **9,283,472 numeric telemetry records**.
Each file has exactly one opening record, a clean closing record, a final newline,
monotonic file timestamps, and signal summaries that match independently computed
sample counts, finite counts, minima, maxima and means. No malformed JSON, invalid
UTF-8, duplicate JSON keys, undefined saved numeric signals, or malformed embedded
firmware manifests were found. Every SHA-256 still matches the phone-transfer
manifest. The original recordings were not modified.

This means no detected file corruption. It does **not** mean every transmitted
frame was retained, or that every correctly stored sensor reading is physically
accurate. Startup gaps and a DC-current validity issue are described below.

## Each recording

Times below are PDT on 19 October. Original filenames use UTC.

| Recording | Local start | Duration | Numeric records | Findings |
| --- | --- | --- | ---: | --- |
| [1 — 10-01-39 UTC](../runtime-session-2026-10-19T10-01-39.716Z-7e350b5f.jsonl) | 03:01:39.716 | 7m 22.773s | 1,998,482 | Starts idle; `precharge start` at 204.267s and `control start` at 214.763s. No new shutdown fault. Startup sequence gaps only. |
| [2 — 10-09-45 UTC](../runtime-session-2026-10-19T10-09-45.670Z-a6bcc7f6.jsonl) | 03:09:45.670 | 13m 32.139s | 4,265,905 | Riding, then explicit `control stop` at 730.653s. No new shutdown fault. Startup sequence gap only. |
| [3 — 10-44-50 UTC](../runtime-session-2026-10-19T10-44-50.484Z-a2e60235.jsonl) | 03:44:50.484 | 8m 13.961s | 2,657,299 | New critical `PhaseOvercurrent` shutdown at approximately 107.399s, then coprocessor `PowerFeedbackLost`. Faults cleared; control successfully restarted at 210.427s. No sequence gaps anywhere in this file. |
| [4 — 10-56-50 UTC](../runtime-session-2026-10-19T10-56-50.375Z-17521eb9.jsonl) | 03:56:50.375 | 1m 42.721s | 361,786 | Essentially stationary. Explicit `control stop` at 5.992s. No new shutdown fault; prior fault history is replayed. Startup gaps and one rejected header. |

## Completeness and startup behavior

| Recording | Valid received frames in footer | Unrepresented sequence numbers | Rejected packets | Unknown-ID rejects |
| --- | ---: | ---: | ---: | ---: |
| 1 | 88,591 | 2,127 in 3 jumps | 0 | 2,554 |
| 2 | 155,237 | 483 in 1 jump | 0 | 2,409 |
| 3 | 97,469 | 0 | 0 | 0 |
| 4 | 21,608 | 693 in 19 jumps | 1 header reject | 4,260 |

**Every sequence jump occurs within the first second of its file.** There are no
subsequent sequence jumps in any of the four recordings. No file has an in-file
host frame gap greater than 250ms or a sequence reset. The third file's complete
sequence coverage includes the fault and recovery.

Unrepresented sequence numbers are not automatically the number of physically
lost packets: received frames containing no loggable events can also leave no
frame-associated record. Subtracting all accepted frames from the sequence span
gives minimum deficits of 2,074 / 467 / 0 / 639 frames respectively, subject to the
logger's interval-counter interpretation. Per-file JSON reports retain both
measurements rather than treating them as identical.

The largest startup discontinuities are:

- Recording 1: 9.942s of device time crossed at host t=0.088s.
- Recording 2: 2.533s of device time crossed at host t=0.026s.
- Recording 4: 3.232s of device time crossed at host t=0.031s.

These are device-time discontinuities near recording startup, not equivalent
wall-clock pauses inside the file. They are consistent with connection/startup
buffering or dropping data while the signal catalog becomes available. The
unknown-ID counters show additional startup decoding omissions; the unavailable
values cannot be recovered from these files. None of this damaged the JSONL
records that were saved. There were no recorded CRC, length or payload-parse
rejects in any file, and no automatic logger-error `recording_gap` records.

## Pause/resume and boundaries

The logger closes the current file on Pause. Resume opens a fresh file with time
reset to zero; it does not create one file with a long internal pause. New session
also opens a fresh file. Existing files have no explicit end-reason or user-action
marker distinguishing those actions from disconnect/reconnect.

| Boundary | Time without a recording |
| --- | --- |
| 1 → 2 | 43.181s |
| 2 → 3 | 21m 32.675s |
| 3 → 4 | 3m 45.930s |

Recording 3 starts with **158 cached signal definitions at t=0**, whereas the
other files start without cached definitions. The source logger clears its cache
when a new USB session begins and retains it for file rotation/resume. Therefore
recording 3 is the strongest candidate for a resumed or manually rotated segment
of an existing connection. That evidence cannot distinguish Resume from New
session. Gap length alone cannot establish the user's action: the 43s gap is
also compatible with stopping/reconnecting recording, and the 21m gap could
contain unrecorded riding/commands. Device uptime continues forward across all
four files; no recorded main-processor reboot was identified.

## New fault in recording 3

The original source is
`runtime-session-2026-10-19T10-44-50.484Z-a2e60235.jsonl`.
The main fault/shutdown appears at **107.399s**, approximately **03:46:37.883 PDT**.
This is a new **software phase-overcurrent** event, distinct from the earlier
October 16 TorqueLoss investigation.

The persistent journal supplies a snapshot from before the main's software
shutdown, boot 12 / sequence 28 / main uptime **3,464,552ms**:

| Captured field | Value |
| --- | ---: |
| Measured phase channel `iu_a` | -179.192 A |
| Measured phase channel `iv_a` | +1,191.07 A |
| Configured phase-current trip threshold | 1,100 A |
| Reconstructed `iw_a` | -1,011.88 A |
| Iq feedback included in snapshot | +1,255.77 A |
| Id feedback included in snapshot | -160.673 A |
| PWM BDTR | `0x02009CC1` — MOE set |
| PWM CCER | `0x00000555` — phase outputs enabled |
| Gate-input bits | `0x7` — main power on, reset released, ready high, /FAULT not asserted |

The measured channel is about **8.3% above the recorded threshold**. The snapshot
describes what the detector measured; it does not independently establish whether
the excursion was physical current, switching interference or a sensing error.
The source protection requires three consecutive threshold violations; the
journal retains one evidence snapshot rather than the three underlying samples.
The snapshot's sensor-channel labels should not be assumed identical to the
generated graph's PWM-phase mapping without checking that build's mapping.

Immediately beforehand the published command is near full throttle and
approximately 897–900 A Iq reference, with periodic Iq readings around 890–940 A.
Near t=107.389s the published bus voltage is about 92.38V and DC current about
-399.8A, but see the DC-validity caveat below. Inverter temperatures immediately
before the event are approximately **41.8 / 43.9 / 45.6°C**. BMS power-ready,
freshness and contactor-closed stay high throughout the recording.

At 107.399s the main reports critical shutdown and disables control/gate power.
At 107.408s the console reports `PhaseOvercurrent` and the coprocessor reports
`PowerFeedbackLost`. Phase-current readings fall to near zero by 107.408s.
The roughly 200Hz periodic stream does not capture the 1,191A detector sample;
that value comes from the separate fault snapshot. This is an expected bandwidth
limitation rather than a file-summary mismatch.

Journal sequence 29 records receipt of the coprocessor fault report at main
uptime **3,464,556ms**, 4ms after the overcurrent snapshot. Its `age_ms=50` reflects
the source's brief wait for optional detailed evidence before journaling; the
record explicitly uses the earlier receipt time. Neither field is a native
coprocessor physical-trip timestamp.

The recorded sequence supports **main overcurrent shutdown followed by a
coprocessor power-feedback fault**. The physical origin of the current excursion
is unresolved. This episode does not provide evidence that a bent feedback pin
initiated it. A coincident earlier electrical event cannot be categorically
excluded because native coprocessor trip timing/inputs are unavailable:
`coprocessor_trip_reason` and `coprocessor_trip_inputs` remain -1, and the journal
uses `FFFFFFFF` for those unavailable fields.

Recovery is visible: first clear at 187.110s restores the coprocessor, a start at
189.720s is refused because the supervisor is still faulted, another clear at
198.184s returns it to IDLE, and the final start at 210.427s succeeds. There is no
further critical shutdown through the end of this recording.

### Why a 900 A command can still produce an overcurrent trip

The saved target and effective Iq reference both remain at or below **900 A**.
The cap is on the controller's requested current, not a hardware instantaneous
current ceiling. The PI controller regulates actual current by adjusting voltage;
finite response time, PWM ripple, disturbances and measurement error can produce
readings above its target.

There is also a measurement-path difference in the locally available source:
the generated current acquisition averages two points within each ADC burst,
then feedback can combine adjacent up/down midpoint samples. The phase-overcurrent
detector instead checks the first burst point directly, after calibration/mapping,
and trips after three consecutive callbacks in which either measured channel is
above the threshold. These samples are not interchangeable with the averaged Iq
display. With Id near zero, the amplitude-invariant transforms make a 900 A Iq
target correspond approximately to a 900 A ideal phase-current peak; there is no
automatic RMS conversion that alone explains the 1,191 A reading.

In the last 190ms of published pre-trip data (t=107.200–107.390s):

| Signal | Published range | Arithmetic sample mean |
| --- | --- | --- |
| Iq reference / effective reference | 894.95–900.00 A | 898.34 A |
| Feedback Iq | 845.33–942.68 A | 899.92 A |
| Latest raw Iq | 839.78–988.26 A | 907.65 A |

These are sparse publication statistics, not control-rate waveforms or
time-weighted averages. The last published voltage-clamp scale remains 1 and the
voltage guard remains inactive before the trip, with requested and output voltages
agreeing; no published voltage-saturation event explains the excursion there.
The fault snapshot subsequently retains 1,191 A in one phase channel and 1,256 A
in its included Iq feedback. Thus there is evidence of a brief **measured**
excursion beyond the command, rather than a command above 900 A. It is too large
to dismiss as simple rounding. The ~200Hz recording misses the native-rate
samples needed to decide between genuine current overshoot/ripple, acquisition
noise, or another control/angle disturbance. A synchronized pre-trigger capture
of raw phase signal/reference counts, d/q feedback, reference, voltage/PWM and
encoder angle would be needed to determine the initiating mechanism.

[Pre-trip statistics](current-limit-pretrip-statistics.json) retain the values
above. No control gains, current limits or trip thresholds were changed.

### Traction-loss hypothesis and other telemetry clues

Loss of traction followed by regrip could disturb mechanical load and provoke a
control transient, but this recording has **no affirmative evidence of that
sequence**. It cannot conclusively rule out a very short event between samples.

An essential source check: `display_speed_mph` is **not phone GPS**.
`ZeroDisplayService::updateZeroDisplay()` feeds `encoder.controlRpmMech()` to
`ZeroDisplay::update()`, which calculates road speed from configured gearing and
wheel circumference. Both speed and fast RPM therefore share the motor encoder.
The Android GPS manager feeds the speed UI/calibration but no independent GPS
samples are saved in these files. There is no independent front-wheel speed or
traction/slip signal in the saved catalog. Comparing displayed mph with RPM
cannot establish tire slip; GPS or front-wheel speed would be needed.

Fast RPM progresses from about 1,014 at t=106.0s to 1,390 at 106.5s, 1,770 at
107.0s, 1,909 at 107.2s and 2,040 at 107.389s. Fitted acceleration is approximately
768 RPM/s over 106.0–106.5s, 753 RPM/s over 106.5–107.0s and 727 RPM/s over
107.0–107.389s. The last 100ms gain is about 59 RPM; earlier 100ms gains are
roughly 66–83 RPM. There is no large pre-trip spin-up or slowdown resolved by
this stream. The first shutdown publication at 107.399s includes 2,063 RPM;
subsequent publications fall to 1,992 RPM at 107.408s and 1,934 RPM at 107.414s,
then partly recover. The first clearly recorded dip is at/after shutdown, so it
does not establish a prior regrip. A 10ms speed filter and roughly 200Hz
publication limit the timing inference.

Other keys do not provide a clear competing initiating event:

- No BMS-ready/contactor/freshness loss; no new undervoltage-derate or regen-block
  flag. Bus voltage sags under acceleration to about 92V, then recovers when
  current disappears. This is not a logged collapse of the HV supply.
- Current sample validity stays high with approximately 24.6us sample age.
  Encoder rejection count stays zero. Raw sine/cosine stays near its normal
  loaded amplitude through the first shutdown sample; its amplitude contracts
  by approximately 3% afterward. This does not show a preceding encoder failure,
  but accepted-sample telemetry cannot exclude a short undetected angle error.
- Controller/ADC ISR rates stay near 5kHz before the fault, and the application
  loop stays around 345–354Hz. No telemetry-key overflows, UART errors, RX drops
  or dropped fault-journal records appear around the event.
- The current target is near 900A well before the fault; there is no new large
  throttle step at the instant of failure. The voltage guard is inactive and
  voltage clamp scale remains 1 in the available pre-trip publications.
- The live inverter temperatures are moderate, with no new thermal fault.

The sustained low DC-validity flag deserves separate diagnosis. A 40-sample
filter fed once per approximately 345Hz application-loop pass would span about
113ms between oldest and newest samples, exceeding the source's 100ms validity
bound. That is consistent with the flag becoming false during active control
and recovering at the faster idle loop rate. Actual filter timestamps are not
logged, so this is an explanatory hypothesis rather than a proven diagnosis;
it is not evidence that traction was lost or DC power disappeared.

The strongest remaining avenues are native-rate current-control/switching
transients and current/angle acquisition errors. The source averages feedback
while checking a less-averaged phase sample for overcurrent, so a synchronized
raw-ADC/control/encoder pre-trigger capture is needed to distinguish physical
current excursion from a measurement disturbance. The sparse recording cannot
select one exact cause.

### Comparison with other high-current pulls

The 1,191 A captured phase reading is **32.3% above the 900 A maximum request**;
the included Iq feedback of 1,255.77 A is **39.5% above it**. The fact that a
reference cap does not mathematically clamp physical current explains how an
excursion is possible, but does not establish that this excursion is acceptable
or expected. The rider reports this is the first such shutdown in approximately
six hours; the locally reviewed files do not cover that entire exposure.

I compared today's first three files using effective reference >=850 A, enabled
control and fast RPM 1,000–2,500. These are cached publication packets, not
synchronized native-rate samples. The fault file is limited to t<107.395s.

| Recording | Qualifying publications | Median absolute Iq-reference error | Largest positive error |
| --- | ---: | ---: | ---: |
| 1 | 41 | 11.0 A | +34.8 A |
| 2 | 165 | 24.8 A | +70.8 A |
| 3, before fault | 243 | 19.7 A | +58.0 A |

For the closer speed/bus subset (1,850–2,200 RPM, 90–100 V), recording 1 has 34
publications with Iq 843–932 A and recording 3 has 47 publications with Iq
845–943 A. These are similar ranges, with no obvious progressive departure
toward 1,200 A before the short event. The comparison is sparse and does not
prove sub-millisecond excursions were absent from previous pulls.

The available branch comparison from the regular base `ea246c5` to the recorded
graph's development branch `4ba5b36` changes reference conditioning and the DC
limiter path, but not `PhaseCurrentADC.cpp` or `CurrentLoopMath.h`. This rules out
attributing the change simply to a newly reduced three-sample count or altered
inner PI math in that comparison. It does not establish that new reference-path
behavior, changed operating exposure or an unrelated disturbance had no effect.
The new voltage guard is inactive in the published interval around this fault,
and target/effective current remain <=900 A.

Treat this as an unexplained transient in control or sensing. Repeated correlated
ADC interference, current-reference/measurement disturbance, or real current
overshoot/ripple remain open. The existing recording cannot choose between them.
Native-rate pre-trigger evidence is required before adjusting the protection or
claiming a controller fix.

[Comparison statistics](high-current-comparison.json) retain the selection
criteria, sample counts and distributions. No gains or thresholds were changed.

## Fault history versus new faults

The firmware repeatedly sends retained journal records. The first two files
contain the same **27 historical records**, spanning boots 1–12. Those include
older PhaseOvercurrent, RAM ECC and DC-current events; receiving them again does
not make them new ride failures. Boot 12's existing sequence 27 is a warning-level
`CanErrorPassive` event from uptime 2,403ms, long before these recordings.

Recording 3 adds exactly **two journal records**, sequences 28 and 29, belonging
to the one shutdown episode above. Recording 4 replays the resulting 29-record
history but adds nothing. Active fault states are clear in recording 4.
No malformed raw v1 fault-history strings were found. These files have no
derived `fault_record` JSON rows, but the complete raw records remain saved as
`fault_log_latest` / `fault_log_record` string values and are decoded in the
per-file `.review.json` exports.

## General measurement review

- **DC-current validity deserves follow-up.** `cg_dclink_valid=0` essentially
  coincides with active riding: from 214.873s to the end of recording 1,
  0.582–730.676s in recording 2, and most running portions of recording 3,
  including the overcurrent event. The readings continue changing; this is not
  proof of a frozen stream or JSON corruption. In the locally available
  `.worktrees/next-changes` image source, which matches the recordings' disabled
  limiter diagnostics (`limit_active=0`, `iq_limit=-1`, `target=0`), this flag is
  diagnostic only. The DC sensor's validity check includes the age of the oldest
  sample in its 40-sample average, with a 100ms bound. We cannot establish which
  condition failed from these logs. Published DC-current/power peaks should be
  treated as provisional until this freshness issue is understood. Phase-current
  validity is a separate signal and remains high.
- **Encoder/current acquisition:** `enc_rejects` stays 0, `cg_sample_valid` stays
  1, and current sample ages remain approximately 23–33.5us. These support live
  acquisition, without proving absolute sensor calibration or rotor alignment.
  Smoothed `Mech_RPM` can lag the faster `cg_rpm_control` substantially during
  acceleration; do not compare them as identical-time estimators.
- **Temperatures:** all three inverter temperature channels are finite; the
  largest observed value is approximately 48.9°C. `temp_motor_c` is null in all
  four files, meaning motor temperature is unavailable rather than a broken
  JSON record.
- **Recording 4:** RPM is effectively zero and phase currents are at the noise
  level. Tiny positive denormal smoothed RPM values represent a filter settling
  toward zero. Iq request can remain nonzero while the drive is idle; effective
  Iq is 0 throughout this file, so a stored request alone is not delivered torque.
- **Firmware identity:** all saved manifests identify graph `foc_demo`, hash
  `84929517e9ee5331`. That identifies the generated graph, not a unique base-image
  revision. Source interpretations above remain subject to that limitation.

## Evidence exports

- Per-file `*.validation.json`: full structural, footer-summary, signal and
  sequence analysis, with `*.summary.json` versions omitting large signal tables.
- Per-file `*.review.json`: decoded, deduplicated fault history and state/command
  transitions, plus checksums and startup frame evidence.
- [Recording boundaries](recording-boundaries.json).
- [Fault window, original numeric samples](fault-window-104-112s.csv) and
  [JSON series](fault-window-104-112s.json), t=104–112s of recording 3.
- [Saved graph manifest](firmware-manifest.json).
- [Review extraction script](review_recordings.py); the full validator is
  `tools/validate_telemetry_log.py` in the app workspace.

No device commands, firmware changes, app changes, or original-file edits were
performed as part of this validation/review.
