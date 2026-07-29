# 08 — Data Structures for Embedded Systems

Embedded systems have strict constraints on memory and timing. The standard library
data structures (e.g., `std::vector`, `std::map`) are often inappropriate.
This module covers the embedded-friendly alternatives and patterns.

---

## Key Concepts

### Finite State Machine (FSM)
The most pervasive pattern in embedded firmware. Models the behavior of a system
that can be in exactly one of a finite set of states at any time.

**Implementation options:**
1. `switch` statement — simple, works for small FSMs
2. State table (2D array of `[state][event] → next_state + action`) — data-driven
3. Function-pointer table — clean separation of state entry/exit/event handlers

**Advice for interviews**: always use function-pointer tables for anything beyond
3–4 states. Shows awareness of scalability and maintainability.

### Static Linked List
Dynamic linked lists use `malloc`/`free` — forbidden in many embedded environments.
A **static linked list** pre-allocates all nodes in a fixed-size array and uses
integer indices (not pointers) to link them. A free-list tracks available nodes.

Operations are O(1) for push/pop at the head; O(n) for search.

### Priority Queue (Min-Heap)
Used in RTOS schedulers, timer wheels, and event queues. A binary min-heap over a
fixed-size array gives O(log n) insert/extract-min without dynamic allocation.

### Lookup Tables (LUT)
Pre-computed values stored in Flash. Trade ROM for speed and determinism.

Examples:
- CRC tables (256-entry `uint8_t` table → O(1) per byte instead of bit-by-bit)
- Sine/cosine tables for motor control
- LED gamma correction tables
- ADC-to-temperature conversion for a thermistor

Using `const` ensures the linker places the table in Flash, not RAM:
```c
static const uint8_t gamma_lut[256] = { /* ... */ };
```

### Ring Buffer (Circular Buffer)
Covered in Module 02; revisited here as a fundamental embedded data structure.
Used for: UART RX/TX, audio streaming, ADC samples, inter-task communication.

---

## Files in This Module

| File | Topic |
|------|-------|
| `state_machine.c` | FSM with function-pointer dispatch table, traffic-light example |
| `linked_list.c` | Static linked list using index-based free-list |
| `priority_queue.c` | Fixed-size binary min-heap with insert/extract-min |
| `lookup_tables.c` | CRC8 table, gamma correction LUT, temperature conversion |

---

## Common Interview Questions

1. **Why are `std::vector` and `std::map` often avoided in embedded C++?**
   > `std::vector` uses dynamic allocation and may reallocate — non-deterministic
   > timing and fragmentation risk. `std::map` uses a red-black tree with node-by-node
   > heap allocation. Both have per-call `malloc`/`free` overhead and don't work in
   > environments without a heap.

2. **Implement a finite state machine. What pattern do you prefer for larger FSMs?**
   > For small FSMs: `switch`. For larger: a 2D table `transitions[state][event]`
   > containing the next state and an action function pointer. Adding a new state
   > is a table row, not a new case buried in a switch.

3. **What is a static linked list? Why would you use it over a dynamic one?**
   > All nodes pre-allocated in an array; links are array indices. No `malloc` needed,
   > no fragmentation, O(1) alloc/free from a free-list. Downside: fixed maximum size.

4. **How does a binary min-heap work? What is the time complexity of insert?**
   > Parent is always ≤ children. Insert: place at end of array and "bubble up" by
   > swapping with parent while parent > new node. O(log n). Extract-min: swap root
   > with last element, reduce size, "sift down". O(log n).

5. **When would you use a lookup table instead of computing the value?**
   > When the function is expensive (e.g., `sin`, `sqrt`, CRC polynomial), is called
   > frequently (control loop), and the input domain is bounded and small enough to
   > fit in Flash. LUTs trade ROM for deterministic O(1) execution time.

6. **What is a CRC? How does a table-based CRC work?**
   > CRC (Cyclic Redundancy Check): a hash based on polynomial division in GF(2).
   > Table-based: pre-compute the CRC of all 256 possible byte values, store in a
   > 256-entry table. Per byte: `crc = table[crc ^ byte]` — O(1) per byte.

7. **How do you make a function-pointer dispatch table type-safe in C++?**
   > Use `std::function`, templates, or a `virtual` base class (if heap is allowed).
   > In C: typedef the function pointer type and use consistent signatures across all
   > table entries — enforced by the type system.

---

## Further Reading

- *Better Embedded System Software* — Philip Koopman, Chapter 9 (State Machines)
- *Embedded Systems Design* — Steve Heath, Chapter 7
- FreeRTOS scheduler source: `tasks.c` — priority ready list with multiple queues
