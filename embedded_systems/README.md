# Embedded Systems Foundations

A complete course covering embedded systems fundamentals, C/C++ low-level programming,
RTOS, hardware interfaces, power management, and interview preparation for senior
embedded systems engineer/developer roles.

---

## Learning Path

Follow the modules in order for a structured experience, or jump to any topic directly.

```
01_c_cpp_fundamentals  →  02_memory_management  →  03_interrupts
                                                          ↓
06_power_management  ←  05_hardware_interfaces  ←  04_rtos
         ↓
07_debugging_and_tools  →  08_data_structures_for_embedded  →  09_interview_questions
                                                                         ↓
                                                               10_mini_projects
```

---

## Modules

| # | Module | Core Topics |
|---|--------|-------------|
| 01 | [C/C++ Fundamentals](01_c_cpp_fundamentals/README.md) | Bit manipulation, pointers, `volatile`, endianness, memory layout, unions/bit-fields |
| 02 | [Memory Management](02_memory_management/README.md) | Memory regions, MMIO, alignment, circular buffers, memory pools |
| 03 | [Interrupts](03_interrupts/README.md) | ISRs, critical sections, flags, debouncing, nesting |
| 04 | [RTOS](04_rtos/README.md) | Tasks, scheduling, semaphores, mutexes, queues, priority inversion |
| 05 | [Hardware Interfaces](05_hardware_interfaces/README.md) | GPIO, UART, SPI, I2C, PWM, ADC, CAN |
| 06 | [Power Management](06_power_management/README.md) | Sleep modes, watchdog, clock gating, low-power design patterns |
| 07 | [Debugging & Tools](07_debugging_and_tools/README.md) | JTAG/SWD, GDB, logic analyzers, assertions, UART logging |
| 08 | [Data Structures for Embedded](08_data_structures_for_embedded/README.md) | State machines, static lists, priority queues, lookup tables |
| 09 | [Interview Questions](09_interview_questions/README.md) | Bit tricks, volatile/memory quizzes, protocol Q&A, system design |
| 10 | [Mini Projects](10_mini_projects/README.md) | LED blinker FSM, UART command parser, RTOS producer-consumer |

---

## Senior Embedded Engineer Interview Checklist

### C / C++ Language & Low-Level
- [ ] Explain `volatile` — when and why to use it; what the compiler does without it
- [ ] Difference between `const`, `volatile`, and `const volatile`
- [ ] What are bit-fields? When are they useful? What are their caveats?
- [ ] Explain endianness — how do you detect it at runtime? How do you convert?
- [ ] Memory layout of a C program: `.text`, `.data`, `.bss`, stack, heap
- [ ] Struct alignment and padding — how to calculate struct size, how to minimize waste
- [ ] Difference between `#define` macros and `inline` functions — pros/cons in embedded
- [ ] Fixed-width integer types (`uint8_t`, `int32_t`) — why they matter for portability

### Memory
- [ ] Stack vs heap — when is each used in embedded? Why prefer static allocation?
- [ ] Memory-mapped I/O — how does it work? Why must peripheral registers be `volatile`?
- [ ] Circular/ring buffer — lock-free implementation using head/tail indices
- [ ] Memory pool — implement a fixed-block allocator; advantages over `malloc`
- [ ] Explain memory fragmentation — why it is dangerous in long-running embedded systems
- [ ] Linker script — what are sections, load address vs run address, BSS initialization?

### Interrupts
- [ ] What happens when an interrupt fires? (stack frame, PC, registers)
- [ ] Rules for writing an ISR — what you must NOT do inside an ISR
- [ ] How do you share data safely between an ISR and main code?
- [ ] Explain critical sections — how do you implement one without an RTOS?
- [ ] Nested interrupts — how are priorities managed on ARM Cortex-M (NVIC)?
- [ ] Software debouncing — implement a timer-based debounce

### RTOS
- [ ] Explain preemptive vs cooperative scheduling
- [ ] Difference between a semaphore and a mutex — when do you use each?
- [ ] Priority inversion — what is it? How does priority inheritance solve it?
- [ ] Deadlock — four necessary conditions; how to prevent in embedded systems
- [ ] Context switching — what does the kernel save/restore?
- [ ] Explain FreeRTOS task states: Ready, Running, Blocked, Suspended
- [ ] Message queues vs shared memory — trade-offs in RTOS IPC

### Hardware Interfaces
- [ ] SPI — CPOL/CPHA modes; draw waveforms for all 4 modes
- [ ] I2C — addressing, ACK/NACK, clock stretching, multi-master arbitration
- [ ] UART — framing (start, data, parity, stop bits); common baud rates; baud error calculation
- [ ] CAN bus — frame format, bit stuffing, arbitration (dominant/recessive), error frames
- [ ] PWM — duty cycle and frequency; how to generate with a timer peripheral
- [ ] ADC — resolution, LSB value, sampling theorem (Nyquist), anti-aliasing

### Power Management
- [ ] MCU sleep modes — explain run, sleep, stop, standby in terms of power/wake latency
- [ ] Watchdog timer — how does it work? Where does it live? What should reset it?
- [ ] Clock gating — what is it? How do you enable/disable a peripheral clock?
- [ ] Event-driven vs polling — power impact and when each is appropriate

### System Design
- [ ] Design a sensor data logger with a microcontroller, ADC, and UART output
- [ ] Design a motor controller with fault detection and safe-state logic
- [ ] How would you update firmware in the field? (OTA / bootloader concepts)
- [ ] Explain DMA — when to use DMA vs CPU for data transfer
- [ ] Hard real-time vs soft real-time — definitions and examples

---

## Compiling the Examples

All `.c` and `.cpp` files compile on a host machine (no embedded toolchain required).
Hardware-specific parts are clearly commented or simulated via structs/defines.

```bash
# C example
gcc -Wall -Wextra -std=c11 -o out <file>.c && ./out

# C++ example
g++ -Wall -Wextra -std=c++17 -o out <file>.cpp && ./out
```

---

## References

- *The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors* — Joseph Yiu
- *Making Embedded Systems* — Elecia White
- *Real-Time Concepts for Embedded Systems* — Qing Li & Caroline Yao
- *Better Embedded System Software* — Philip Koopman
- FreeRTOS documentation: https://www.freertos.org/Documentation/RTOS_book.html
