# 07 — Debugging & Tools

Debugging embedded systems is harder than debugging desktop software — you can't
always attach a debugger, print statements slow things down, and bugs may only
appear at full speed. This module covers the tools and techniques used by senior
embedded engineers.

---

## Key Concepts

### JTAG / SWD
Hardware debug interfaces that connect a debug probe to the target MCU.

| Feature | JTAG | SWD (Serial Wire Debug) |
|---------|------|-------------------------|
| Wires | 4 (TDI, TDO, TCK, TMS) + optional TRST | 2 (SWDIO, SWDCLK) |
| Standard | IEEE 1149.1 | ARM-specific |
| Capabilities | Debug + boundary scan | Debug only |
| Common with | Older MCUs, FPGAs, board testing | Modern ARM MCUs (Cortex-M) |

Both allow: halt/resume, breakpoints (HW + SW), single-step, memory read/write,
register inspection, flash programming.

### GDB with Embedded Targets
GDB connects to a debug probe (J-Link, ST-Link, CMSIS-DAP) via `gdbserver`/`OpenOCD`.

Useful GDB commands in embedded context:
```
target extended-remote :3333    # Connect to OpenOCD
load                            # Flash the binary
monitor reset halt              # Reset and halt
break main                      # Hardware breakpoint
info registers                  # Show all CPU registers
x/10xw 0x20000000               # Examine 10 words at SRAM start
backtrace                       # Stack trace (limited in deeply embedded)
set $pc = 0x8004120             # Manually set PC (useful after hard fault)
```

### Logic Analyzer & Oscilloscope
- **Logic analyzer**: captures digital signals, decodes protocols (SPI, I2C, UART, CAN)
  at the byte/packet level. Use for verifying timing, data correctness, protocol errors.
- **Oscilloscope**: shows analog waveforms — actual voltage levels, signal integrity,
  glitches, rise/fall times, noise. Use for hardware bring-up.

### Semihosting vs UART Logging
- **Semihosting**: routes `printf` to the host via the debug connection. Zero extra
  hardware but adds significant latency (each call halts CPU). Not suitable for
  time-critical code.
- **UART logging**: fast, runs in production (if UART is available), but uses
  a peripheral and pins. Use circular buffer + DMA for non-blocking output.
- **ITM (Instrumentation Trace Macrocell)**: ARM Cortex-M trace port — `printf` at
  hardware speed, no UART needed, minimal timing impact.

### Hard Fault Debugging (ARM Cortex-M)
When a hard fault fires, the CPU saves a stack frame. The fault handler can read:
- **PC** from the stack frame → the address that caused the fault
- **CFSR** (Configurable Fault Status Register) → which type of fault
- **BFAR/MMAR** → the faulting address (bus fault / mem manage fault)

### Defensive Programming
```c
// Assertion macro — halts or logs on failure
#define ASSERT(cond) \
    do { if (!(cond)) assert_failed(__FILE__, __LINE__); } while(0)

// Build-time assertion (no runtime cost)
_Static_assert(sizeof(MyStruct) == 8, "MyStruct size mismatch");
```

---

## Files in This Module

| File | Topic |
|------|-------|
| `assertions_embedded.c` | Runtime assertions, build-time assertions, assert_failed handler |
| `logging_uart.c` | Lightweight ring-buffer UART logger with log levels |

---

## Common Interview Questions

1. **How do you debug a hard fault on ARM Cortex-M?**
   > 1. Write a hard fault handler that captures the stacked PC (from MSP or PSP).
   > 2. Read CFSR/HFSR to identify fault type.
   > 3. Read BFAR/MMAR for the faulting address.
   > 4. Map the PC to source using the `.map` file or addr2line.
   > Common causes: null pointer dereference, stack overflow, unaligned access.

2. **What is the difference between a hardware breakpoint and a software breakpoint?**
   > HW breakpoint: implemented in the debug hardware (ARM has 4–8 FPB units) — works
   > on code in Flash. SW breakpoint: replaces the instruction with a BKPT opcode —
   > only works if code is in RAM (can't modify Flash at runtime).

3. **Explain the difference between JTAG and SWD.**
   > JTAG uses 4 pins and supports boundary scan for board testing. SWD uses only 2
   > pins and is ARM-specific — preferred on modern Cortex-M due to fewer pins and
   > comparable debugging capabilities.

4. **Why is `printf` dangerous for debugging time-critical embedded code?**
   > `printf` is slow (formatted string processing + UART TX) and blocking — it alters
   > the timing of the system, causing Heisenbugs (bugs that disappear under debugging).
   > Use non-blocking logging (ring buffer + DMA) or ITM trace instead.

5. **What is a stack canary? How does it help detect stack overflows?**
   > A known magic value written at the bottom of the stack. Periodically checked
   > (or checked on context switch in FreeRTOS). If the value is overwritten, a stack
   > overflow has occurred — trap it before it corrupts unrelated memory.

6. **How do you use a logic analyzer to debug an I2C issue?**
   > Connect the probe to SDA and SCL. Trigger on a START condition. Decode the
   > transaction: check the address byte, direction bit, and whether each byte gets
   > an ACK or NACK. NACKs indicate address mismatch or device not ready.

7. **What is ITM tracing? Advantages over UART?**
   > ITM (Instrumentation Trace Macrocell) is a hardware peripheral on ARM Cortex-M
   > that routes trace data over the SWO pin. Data appears in the debugger host without
   > using a UART peripheral. Minimal timing impact and no extra pins (just SWO).

---

## Further Reading

- OpenOCD documentation: https://openocd.org/doc/html/
- ARM CoreSight Technical Reference Manual
- *The Definitive Guide to ARM Cortex-M3/M4* — Joseph Yiu, Chapter 12 (Fault Handling)
