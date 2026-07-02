# 03 — Interrupts

Interrupts are the backbone of responsive embedded firmware. Understanding how they
work at the hardware level, how to write correct ISRs, and how to safely share data
between interrupt and main context is essential for any senior embedded role.

---

## Key Concepts

### How an Interrupt Works (Hardware Level)
1. Hardware event occurs (timer overflow, GPIO edge, UART byte received)
2. CPU finishes current instruction (or sometimes the current pipeline stage)
3. CPU saves context: PC, PSR, and caller-saved registers pushed to stack
4. CPU sets PC to the Interrupt Vector — the address of the ISR
5. ISR runs; must clear the hardware interrupt flag before returning
6. CPU pops context (IRET / `BX LR` on ARM) and resumes normal code

On ARM Cortex-M, the hardware automatically saves R0–R3, R12, LR, PC, xPSR ("8-word
stack frame"). The ISR must save any other registers it uses (callee-saved: R4–R11).

### Rules for Writing an ISR
- **Keep it short and fast** — don't do work in the ISR; signal main code instead
- **Clear the interrupt flag** — or the ISR will fire again immediately
- **No blocking calls** — no `sleep()`, no mutexes that can block, no `printf`
- **No FreeRTOS API calls unless they end in `FromISR`**
- **All shared variables MUST be `volatile`**
- **Disable interrupts for multi-byte read-modify-write of shared state**

### Volatile in ISR Context
```c
volatile uint8_t byte_received;  // Modified in ISR, read in main

void USART_IRQHandler(void) {
    byte_received = UART->DR;   // Read clears the interrupt flag on many MCUs
}

int main(void) {
    while (1) {
        if (byte_received) {    // Without volatile, compiler may optimize this out
            process(byte_received);
            byte_received = 0;
        }
    }
}
```

### Critical Sections
A critical section protects a sequence of operations that must run atomically
(not interrupted). On bare-metal:
```c
__disable_irq();   // ARM: CPSID I
// ... critical code ...
__enable_irq();    // ARM: CPSIE I
```

On FreeRTOS: `taskENTER_CRITICAL()` / `taskEXIT_CRITICAL()`

### Nested Interrupts (ARM Cortex-M / NVIC)
- Each interrupt has a configurable **priority level** (0 = highest)
- A higher-priority interrupt can preempt a running ISR
- **BASEPRI** register masks interrupts below a given priority threshold — used by
  FreeRTOS `taskENTER_CRITICAL()` to only mask lower-priority interrupts

### Debouncing
Mechanical switches produce multiple transitions ("bounces") within ~5–50 ms.
Solutions:
- **Hardware**: RC low-pass filter + Schmitt trigger
- **Software**: ignore transitions within a timeout after the first edge (timer-based)
- **Counter-based**: require N consecutive samples in the same state

---

## Files in This Module

| File | Topic |
|------|-------|
| `isr_concepts.c` | ISR structure, flag clearing, volatile shared variable pattern |
| `interrupt_flags.c` | Flag-based ISR ↔ main communication, atomic flag patterns |
| `critical_sections.c` | Simulated disable/enable IRQ, nested critical section guard |
| `debouncing.c` | Timer-based debounce state machine, counter-based debounce |
| `nested_interrupts.c` | Priority levels, BASEPRI concept, tail-chaining simulation |

---

## Common Interview Questions

1. **What must you always do inside an ISR before returning?**
   > Clear the hardware interrupt flag (pending bit). Failing to do so causes the
   > ISR to re-enter immediately after returning — an infinite loop.

2. **Why can't you call `printf` or `malloc` inside an ISR?**
   > Both use mutexes/locks internally (in most libc implementations). If the main
   > context holds that lock when the interrupt fires, calling it in the ISR causes
   > a deadlock. Also, `printf` is too slow for interrupt context.

3. **How do you share data between an ISR and main code safely?**
   > Declare the shared variable as `volatile`. For multi-byte values (e.g., a
   > `uint32_t` on an 8-bit MCU), use a critical section to prevent a torn read.

4. **What is a "spurious interrupt"? How do you handle it?**
   > An interrupt that fires without a valid cause — often caused by electrical noise
   > or a flag that was set before the handler was ready. Handled by always reading
   > and clearing the flag at the start of the ISR and verifying the source.

5. **On ARM Cortex-M, what registers are automatically saved when an interrupt fires?**
   > R0–R3, R12, LR (link register), PC (return address), xPSR (status register).
   > The C ABI caller-saved registers — so a C ISR function just needs to preserve R4–R11.

6. **Explain the difference between IRQ priority and interrupt latency.**
   > Priority determines which interrupt preempts which. Latency is the time from
   > interrupt signal to first ISR instruction — affected by pipeline flush, stack push,
   > and vector table fetch.

7. **What is tail-chaining on ARM Cortex-M?**
   > When an interrupt is pending while another ISR is completing, the CPU skips the
   > pop+push of the stack frame and immediately vectors to the next ISR — reducing
   > latency to ~6 cycles vs ~12.

8. **How do you implement a software debounce?**
   > Start a timer on the first edge. Ignore further edges until the timer expires.
   > If the pin state is still changed at timer expiry, accept the event.

---

## Further Reading

- ARM Cortex-M3/M4 Technical Reference Manual — NVIC chapter
- *The Definitive Guide to ARM Cortex-M3/M4* — Joseph Yiu, Chapters 8–9
- FreeRTOS: "Deferred Interrupt Processing" pattern
