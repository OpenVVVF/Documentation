# Overcurrent path traced in the regular RTE checkout

Inspected `/home/aidan/Documents/RTE/`, regular checkout HEAD `ea246c5`.
No firmware or settings were changed and no device commands were sent.
The software-overcurrent decision block, first-burst-point selection, and ADC1
completion callback also match the available voltage-aware-throttle build-source
copy byte for byte. That comparison does not independently identify the flashed
binary, but the saved software-overcurrent reason and 1,100 A threshold agree
with this path.

## The recorded software phase-overcurrent fault requires three callbacks

1. TIM1 update events trigger ADC1's four-rank injected sequence. ADC2 supplies
   simultaneous reference measurements. Each phase has two points within the
   burst. `configureAdcChannels()` selects **ADC_EOC_SEQ_CONV** on both ADCs:
   [PhaseCurrentADC.cpp:100](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Drivers/Sensors/PhaseCurrentADC.cpp:100).
2. HAL injected start enables **JEOS**, end-of-sequence, rather than per-rank
   JEOC interrupts:
   [stm32h7xx_hal_adc_ex.c:876](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Drivers/STM32H7xx_HAL_Driver/Src/stm32h7xx_hal_adc_ex.c:876).
   The shared IRQ handles ADC1 and ADC2, but the application callback calls the
   protection handler **only for ADC1**:
   [PhaseCurrentADC.cpp:836](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Drivers/Sensors/PhaseCurrentADC.cpp:836).
   Consequently, one burst does not count as four violations because it has four
   ranks, or as two violations because two ADCs are involved.
3. The handler selects the **first burst point** of each measured phase,
   converts signal/reference counts into amps, subtracts offsets, and applies
   the phase mapping. It does not average the second burst point into this
   software-overcurrent measurement:
   [PhaseCurrentADC.cpp:598](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Drivers/Sensors/PhaseCurrentADC.cpp:598).
4. With a positive software threshold, the handler tests whether **either**
   measured phase has absolute current strictly greater than the threshold.
   A violation increments one shared counter. When both phases are at or below
   the threshold, the counter resets to zero. At count 3, it resets the counter
   and raises `PhaseOvercurrent / PhaseOvercurrentSoftware`:
   [PhaseCurrentADC.cpp:638](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Drivers/Sensors/PhaseCurrentADC.cpp:638).
   `OC_CONSEC_SAMPLES=3U` and the default software threshold is 1,100 A:
   [PhaseCurrentADC.h:291](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Inc/Inverter/Drivers/Sensors/PhaseCurrentADC.h:291).
5. `PhaseOvercurrent` is Critical. `FaultManager::raise()` snapshots PWM
   registers, then writes **TIM1 EGR.BG immediately in the IRQ**. It journals
   the evidence and latches the source; it does not wait for a console message,
   JSONL write, or next application-loop pass to break PWM:
   [FaultManager.cpp:207](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Control/FaultManager.cpp:207).
6. The application loop subsequently calls `executeSafetyActions()`, which
   stops the safety heartbeat, disables control, asserts gate reset, cuts main
   gate power and updates control state:
   [FaultManager.cpp:507](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Control/FaultManager.cpp:507).

Examples of counter behavior (each entry means a completed injected sequence):

| Sequence | Result |
| --- | --- |
| Above, normal, above | Counts 1, 0, 1 — no trip |
| Above, above, above | Counts 1, 2, trip |
| U above, then V above, then U above | Also trips: counter is shared |

The event log records roughly **5,000 ADC callbacks/s** before this shutdown.
That means about 200 microseconds between callbacks and approximately **400
microseconds from the first above-threshold callback to the third**. An excursion
beginning between callbacks has additional time until the first observation.
This is a sample-count filter, not a 3ms or 150ms debounce. Correlated noise over
three callbacks can still trip; the code cannot establish that the measured
current is physically correct.

Additional details: the check is not gated by generated `cg_sample_valid`, a
quiet-window result, or drive-output enable. It has no explicit elapsed-time or
sample-sequence test. Its count concerns consecutive processed callbacks, not
three points proving continuous analog current throughout the interval. The
reconstructed third phase is retained as evidence but not separately tested in
this particular two-channel condition. Some comments call the software path
"filtered"; the explicit numeric filtering here is the consecutive-event count,
not the controller's multi-sample averaging.

## Other paths can act on a single event

- **ADC analog watchdog:** ADC1 watches its injected absolute-count window.
  One out-of-window conversion can assert AWD1; its callback immediately breaks
  PWM and raises **AdcWatchdog / AdcWatchdogTrip**, without the three-callback
  counter. Its window uses separate configuration and reference-envelope padding:
  [PhaseCurrentADC.cpp:345](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Drivers/Sensors/PhaseCurrentADC.cpp:345),
  [callback at 863](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Drivers/Sensors/PhaseCurrentADC.cpp:863).
  The recording does not establish its exact active threshold/configuration.
- **Gate-driver /FAULT / TIM1 break input:** the physical break can disable PWM
  directly. The callback attributes a qualified physical event to
  **PwmBreak / DesatBreak**:
  [FaultCallbacks.cpp:51](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Control/FaultCallbacks.cpp:51).
  This is independent of the software phase-current counter.
- **OverTorque:** a separate counter checks absolute generated Iq against 110%
  of calibrated maximum torque current, also requiring three consecutive ADC
  callbacks when enabled. It raises **OverTorque**, a different source:
  [PhaseCurrentADC.cpp:663](/home/aidan/Documents/RTE/Images/Gen7FW/MainProcessor/Src/Inverter/Drivers/Sensors/PhaseCurrentADC.cpp:663).

The new ride fault is explicitly **PhaseOvercurrent: software overcurrent**.
The journal contains its final evidence snapshot, not the two preceding
above-threshold callbacks. Thus this source trace supports a three-callback
decision and does not support calling it a lone bad conversion. It still cannot
decide whether a sub-millisecond sequence was true current, repeated sampling
interference, or another measurement/control disturbance.
