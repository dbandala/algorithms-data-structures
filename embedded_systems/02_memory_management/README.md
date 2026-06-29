# 02 — Memory Management

Embedded systems have tight and often fixed memory budgets. Understanding every
byte — where it lives, how it is allocated, and how it is accessed — is critical
for both correctness and reliability.

---

## Key Concepts

### Memory Regions on a Typical MCU

| Region | Location | Lifetime | Usage |
|--------|----------|----------|-------|
| Flash / ROM | On-chip NVM | Permanent | Code (`.text`), read-only data (`.rodata`) |
| SRAM | On-chip volatile | Power-on | Stack, `.data`, `.bss`, heap |
| External RAM | Off-chip (DRAM/PSRAM) | Power-on | Large buffers, framebuffers |
| Registers | CPU + peripherals | Instant | CPU state, peripheral control |
| Backup SRAM | Low-power domain | Battery-backed | RTC, persistent state across reset |

### Memory-Mapped I/O (MMIO)
Peripheral registers are accessed by reading/writing specific memory addresses — the
same mechanism as RAM, but the hardware acts on the value immediately.

**Critical rule:** all MMIO access variables/pointers MUST be `volatile`.

```c
// Simulated: in real hardware this address is fixed by the MCU datasheet
volatile uint32_t *GPIO_ODR = (volatile uint32_t *)0x40020C14;
*GPIO_ODR |= (1U << 5);  // Set pin 5
```

### Struct Alignment and Padding
The CPU prefers to read/write data at naturally-aligned addresses:
- `uint8_t` at any address
- `uint16_t` at even addresses
- `uint32_t` at addresses divisible by 4

The compiler inserts **padding bytes** to satisfy alignment. Order struct fields from
largest to smallest type to minimize wasted space.

```c
// Wastes 6 bytes
struct Bad  { char a; int b; char c; };  // sizeof = 12

// Wastes 0 bytes
struct Good { int b; char a; char c; };  // sizeof = 8
```

### Dynamic Allocation in Embedded Systems
`malloc`/`free` are usually **avoided** in deeply embedded code because:
- Non-deterministic timing (not real-time friendly)
- Heap fragmentation over time
- No heap in minimal startup environments
- Failure silent until crash

Alternatives:
- **Static allocation**: declare all objects at compile time
- **Memory pools**: fixed-size blocks, O(1) alloc/free, no fragmentation
- **Stack allocation**: for short-lived objects in a known-scope function

### Circular (Ring) Buffer
The most common lock-free data structure in embedded systems. Used for UART RX/TX
buffers, ADC sample buffers, logging, and inter-task communication.

Key insight: use power-of-2 size so head/tail wrapping is a bitwise AND, not modulo.

```c
head = (head + 1) & (SIZE - 1);  // Wraps without division
```

### Memory Pool
A fixed-size block allocator. Pre-allocates a large block, divides into equal-sized
chunks, and hands them out via a free-list. O(1) alloc/free, no fragmentation.

---

## Files in This Module

| File | Topic |
|------|-------|
| `memory_regions.c` | Placing variables in specific sections; startup initialization |
| `memory_mapped_io.c` | MMIO simulation, volatile pointer patterns, register struct overlay |
| `memory_alignment.c` | Struct padding, `offsetof`, `__attribute__((packed))`, aligned access |
| `dynamic_allocation.c` | malloc pitfalls, custom allocator, why embedded avoids dynamic alloc |
| `circular_buffer.c` | Lock-free ring buffer for UART/ADC, power-of-2 optimization |
| `memory_pool.c` | Fixed-block allocator with free-list, O(1) alloc/free |

---

## Common Interview Questions

1. **Why is `malloc` problematic in embedded systems?**
   > Non-deterministic timing breaks real-time guarantees; fragmentation can cause
   > allocation failures after hours of runtime; many bare-metal environments lack a
   > heap implementation.

2. **What is the difference between `.data` and `.bss`?**
   > `.data` holds initialized globals/statics — copied from Flash to RAM at startup.
   > `.bss` holds zero-initialized globals/statics — startup code zeroes this region,
   > saving Flash space (no initial values to store).

3. **How do you implement a lock-free circular buffer?**
   > One producer, one consumer: producer writes `head` only, consumer writes `tail`
   > only. Since both are single-word reads/writes on most architectures, no lock is
   > needed for single-producer/single-consumer.

4. **What is MMIO? Why must peripheral registers be `volatile`?**
   > MMIO maps hardware registers to memory addresses. `volatile` prevents the compiler
   > from caching the value — each access must actually read/write the hardware address.

5. **What is memory fragmentation? How does a memory pool prevent it?**
   > Fragmentation: free memory exists but not as a contiguous block large enough for
   > the request. Pools allocate same-size blocks — no fragmentation possible.

6. **How do you ensure a buffer is cache-line aligned for DMA?**
   > Use `__attribute__((aligned(32)))` (or the MCU's cache line size) so the DMA
   > buffer doesn't share a cache line with other variables (false sharing / cache
   > coherency issues).

7. **What does a linker script do? What is the difference between LMA and VMA?**
   > A linker script describes how sections are mapped to memory. LMA (Load Memory
   > Address) is where the data sits in Flash; VMA (Virtual Memory Address) is where
   > the CPU expects to find it at runtime. Startup code copies `.data` from LMA to VMA.

8. **What is a stack overflow in embedded? How do you detect one?**
   > Stack grows into another memory region (heap, `.bss`, or another task's stack),
   > corrupting data silently. Detected via stack canary (magic value at the bottom
   > of the stack checked periodically or by the RTOS).

---

## Further Reading

- *Making Embedded Systems* — Elecia White, Chapter 4 (Memory)
- ARM Cortex-M startup files — how `.data` copy and `.bss` zeroing work
- FreeRTOS heap implementations: `heap_1` through `heap_5`
