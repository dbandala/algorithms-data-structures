# 06 — Power Management

Minimizing power consumption is a critical requirement in battery-powered and
energy-harvesting embedded systems. Power management spans MCU sleep modes, peripheral
control, and software architecture.

---

## Key Concepts

### MCU Power Modes (Typical Progression)

| Mode | CPU | Peripherals | RAM | Wake Sources | Power |
|------|-----|-------------|-----|--------------|-------|
| Run | Active | Active | Retained | — | ~mA range |
| Sleep | Halted | Active | Retained | Any IRQ | Slightly less |
| Stop/Deep Sleep | Halted | Mostly off | Retained | Select IRQs, RTC | µA range |
| Standby | Halted | Off | Lost (BKPSRAM only) | WKUP pin, RTC | ~1–2 µA |
| Shutdown | Halted | Off | Lost | WKUP pin | <1 µA |

Wake latency increases with depth: Run mode resume is immediate; deep sleep may require
PLL re-lock (hundreds of µs).

### Watchdog Timer (WDT / IWDG)
An independent timer that resets the MCU if it is not "kicked" (refreshed) before
it expires. Prevents the system from hanging silently.

- **Independent (IWDG)**: runs off its own low-speed oscillator — not affected by
  main clock failure
- **Window watchdog (WWDG)**: must be kicked in a specific time window — detects
  both too-early and too-late kicks (detects runaway code that loops faster than expected)

Rules:
- Kick the watchdog only from a known-good point in the main loop
- Never disable the watchdog in production firmware
- Feed it from a single location — multiple feed points mask hangs

### Clock Gating
Disabling the clock to peripherals not currently in use. Zero dynamic power when
clocked off (static leakage remains). In STM32-family MCUs: `RCC->AHB1ENR &= ~(1 << n)`.

### Event-Driven Low-Power Architecture
Replace polling loops with interrupt-driven (event-driven) code:
```
while(1) {
    process_pending_events();  // do work
    __WFI();                   // Wait For Interrupt — CPU halts until next IRQ
}
```
`__WFI()` (ARM Wait For Interrupt) or `__WFE()` (Wait For Event) puts the CPU into
sleep mode immediately. The next interrupt wakes it in <1 µs.

### Dynamic Voltage and Frequency Scaling (DVFS)
Reduce CPU clock frequency (and sometimes voltage) during low-demand periods.
Lower voltage means lower dynamic power: $P \propto C V^2 f$.

---

## Files in This Module

| File | Topic |
|------|-------|
| `sleep_modes.c` | Sleep mode state machine, WFI pattern, wake-source tracking |
| `watchdog_timer.c` | Watchdog init, kick pattern, window watchdog concept |
| `clock_gating.c` | Enable/disable peripheral clocks, power impact simulation |
| `low_power_patterns.c` | Event-driven main loop, peripheral shutdown before sleep |

---

## Common Interview Questions

1. **Explain the difference between sleep and standby mode.**
   > Sleep: CPU halted, peripherals running, RAM retained — any IRQ wakes it.
   > Standby: almost everything off, RAM lost (except backup domain), only a few
   > wake sources (WKUP pin, RTC alarm). Much lower power but longer wake latency.

2. **What is a watchdog timer? Where should you kick it?**
   > A hardware timer that resets the MCU if not refreshed before expiry. Kick it
   > once per main loop iteration, from a single well-known location. Multiple kick
   > points hide the real system state.

3. **What is the difference between IWDG and WWDG on STM32?**
   > IWDG: independent oscillator, must be kicked before timeout (only detects hangs).
   > WWDG: must be kicked within a window — too early or too late triggers a reset
   > (detects runaway code and hangs).

4. **What is `__WFI()`? How does it reduce power?**
   > ARM instruction that halts the CPU core clock until an interrupt occurs, saving
   > dynamic power. Peripheral clocks and RAM are maintained; wake latency is ~1 µs.

5. **How does clock gating save power?**
   > Dynamic power $P = C V^2 f$ — stopping the clock to an unused peripheral drives
   > its f to zero, eliminating dynamic switching power. Only leakage current remains.

6. **What is the difference between `__WFI` and `__WFE`?**
   > WFI wakes on any unmasked interrupt. WFE also wakes on "events" — signals from
   > other cores or peripherals that don't necessarily generate an interrupt. Used in
   > multi-core synchronization (SEV/WFE handshake).

7. **How do you measure the actual current draw of your embedded system?**
   > Measure across a precision shunt resistor in series with VCC using a
   > multimeter (for average) or an oscilloscope/current probe (for dynamic waveforms).
   > Tools like the Nordic PPK2 or Otii Arc can log µA-resolution power over time.

8. **What is DVFS? When is it practical on a microcontroller?**
   > Dynamic Voltage and Frequency Scaling — reduce clock and supply voltage during
   > light workloads. Practical on MCUs with built-in voltage regulators and PLL
   > (e.g., STM32L series). Trade-off: DVFS switching overhead and complexity.

---

## Further Reading

- STM32 Application Note AN4760: Optimizing power consumption
- *Making Embedded Systems* — Elecia White, Chapter 11 (Power Management)
- ARM Cortex-M Power Management application notes
