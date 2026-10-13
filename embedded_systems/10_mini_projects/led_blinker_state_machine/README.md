# LED Blinker State Machine

A minimal embedded project demonstrating a hardware abstraction layer, FSM-based
LED control, and timer-driven state transitions. Compiles and runs on a host machine.

---

## What This Demonstrates

- Hardware abstraction: `led_hal.h` decouples the FSM from hardware specifics
- FSM: function-pointer dispatch table (see Module 08)
- Timer callback pattern: periodic tick drives state transitions
- Non-blocking design: no `sleep()` inside the FSM; the FSM returns on each tick

---

## States

```
      TIMER_EXPIRE          TIMER_EXPIRE
OFF ──────────────► ON ──────────────► OFF (loops)

Optional FAULT state:
ON/OFF ──FAULT_EVENT──► FAULT (blink fast) ──CLEAR──► OFF
```

---

## Build and Run

```bash
gcc -Wall -Wextra -std=c11 -o led_blinker led_blinker.c && ./led_blinker
```
