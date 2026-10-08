# 09 — Interview Questions

Curated problems and Q&A for senior embedded systems engineer interviews.
Covers every topic in this course with a focus on depth, correctness, and the
"why" behind each answer.

---

## Files in This Module

| File | Topic |
|------|-------|
| `bit_tricks.c` | 20+ bit manipulation problems with solutions |
| `volatile_quiz.c` | Spot-the-bug quiz: `volatile` and ISR interactions |
| `memory_quiz.c` | Pointer, struct layout, and memory region quiz |
| `protocol_questions.md` | Hardware protocol deep-dive Q&A (UART/SPI/I2C/CAN) |
| `system_design_embedded.md` | System design interview walkthroughs |

---

## Quick-Reference: Top Questions by Category

### Bit Manipulation
- Count set bits in a 32-bit integer (Brian Kernighan's algorithm)
- Check if a number is a power of 2
- Reverse the bits of a 32-bit integer
- Swap two variables without a temporary variable
- Find the position of the rightmost set bit
- Clear/set/toggle a range of bits

### `volatile` and ISRs
- What is the output of this code? (Loop over non-volatile ISR-modified variable)
- Is this ISR safe? (Show an ISR that modifies a multi-byte value without critical section)
- Why does removing optimization `-O0` make the bug go away?
- Explain the `volatile sig_atomic_t` type from `<signal.h>`

### Memory and Pointers
- What is the output of `sizeof(struct X)`? (Padding question)
- Explain `const int *p` vs `int * const p` vs `const int * const p`
- What does `int (*arr)[10]` declare?
- Write a function that takes any array and returns its last element (using pointer arithmetic)
- What is a memory leak? How do you detect one on a resource-constrained device?

### RTOS / Concurrency
- Describe a priority inversion scenario with three tasks
- What happens if two tasks call `xQueueSend` on the same queue simultaneously?
- When does FreeRTOS `xSemaphoreGive` not need a critical section?
- Describe the FreeRTOS tick ISR — what does it do?

---

## Behavioral / System-Level Questions

These are the open-ended questions that distinguish senior candidates:

1. **Describe the most difficult embedded bug you have debugged. What made it hard?**
   > Interviewers look for: systematic approach (reproduce → isolate → hypothesize →
   > test → confirm), hardware/software boundary awareness, use of tools.

2. **How do you approach firmware architecture for a new product?**
   > Layered architecture: hardware abstraction (HAL/BSP) → drivers → middleware
   > (RTOS, protocol stacks) → application. Interviewers look for: separation of
   > concerns, testability, portability considerations.

3. **How do you ensure your firmware is reliable for 10+ years in the field?**
   > Watchdog timers, defensive coding (ASSERT), deterministic memory allocation,
   > safe-state logic, firmware update capability (OTA/bootloader), error logging,
   > thorough testing (unit + integration + HIL).

4. **How do you handle a situation where a sensor gives intermittent bad readings?**
   > Input validation (range/sanity checks), outlier filtering (median filter, Kalman
   > filter), redundancy (cross-check with other sensors), fault counters, fail-safe
   > state when fault threshold exceeded.

5. **Walk me through the boot sequence of an ARM Cortex-M MCU.**
   > 1. CPU reads Stack Pointer from vector table[0] (0x00000000)
   > 2. CPU reads Reset Handler address from vector table[1]
   > 3. Reset Handler runs: copies `.data` from Flash to RAM, zeros `.bss`
   > 4. Calls `SystemInit()` (clock/PLL setup)
   > 5. Calls `main()`

6. **What is DMA? When should you use it instead of CPU-driven transfers?**
   > DMA (Direct Memory Access): hardware controller moves data between memory and
   > peripherals without CPU involvement. Use when: high data rates (ADC streaming,
   > UART/SPI bulk transfers), and CPU should be doing other work (or sleeping).

7. **How do you implement safe firmware update (OTA) on a microcontroller?**
   > Dual-bank flash or staging area: write new firmware to inactive partition while
   > running from active partition. Verify CRC/hash of new image. Atomic swap (single
   > word write to flag). Rollback on failed boot (boot counter watchdog).

8. **What is the difference between hard real-time and soft real-time?**
   > Hard: missing a deadline is a system failure (e.g., anti-lock brake control,
   > pacemaker). Soft: occasional deadline misses degrade quality but don't cause
   > failure (e.g., video playback, HMI update). RTOS + interrupt-driven design for
   > hard RT; quality-of-service mechanisms for soft RT.

---

## Further Reading

- *Embedded Interview Questions* — Luca Neri (free PDF available online)
- *Programming Embedded Systems in C and C++* — Michael Barr
- Barr Group Embedded C Coding Standard
