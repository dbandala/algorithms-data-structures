# 01 — C/C++ Fundamentals for Embedded Systems

Solid mastery of C and C++ fundamentals is the foundation of embedded systems work.
This module covers the language features that appear most frequently in hardware-level
code and senior technical interviews.

---

## Key Concepts

### Bit Manipulation
Embedded code constantly manipulates hardware registers at the bit level.
Operations: `SET`, `CLEAR`, `TOGGLE`, `CHECK`, `EXTRACT`, `INSERT` bits.

```c
// Set bit n
reg |= (1U << n);

// Clear bit n
reg &= ~(1U << n);

// Toggle bit n
reg ^= (1U << n);

// Check bit n
bool set = (reg >> n) & 1U;
```

### `volatile`
Tells the compiler: *"this variable may change outside normal program flow."*
Required for:
- Memory-mapped peripheral registers
- Variables modified inside ISRs
- Variables in shared memory between cores or tasks

Without `volatile`, the compiler may cache the value in a register and never re-read
from the actual address, causing bugs that only appear in optimized builds.

### `const volatile`
Both qualifiers together mean: *"this value may change externally, but this code
must not write to it."* Used for read-only hardware status registers.

### Endianness
- **Big-endian**: most significant byte at the lowest address (network byte order)
- **Little-endian**: least significant byte at the lowest address (most x86/ARM MCUs)

Matters when: serializing structs to bytes, reading multi-byte registers, protocol parsing.

### Memory Layout
A compiled C program has these segments:

| Segment | Contents | Initialized? |
|---------|----------|--------------|
| `.text` | Code, string literals, `const` globals | ROM — read-only |
| `.data` | Initialized global/static variables | Copied from ROM to RAM at startup |
| `.bss` | Zero-initialized global/static variables | Zeroed at startup by startup code |
| Stack | Local variables, function call frames | Grows downward (typically) |
| Heap | Dynamic allocation (`malloc`) | Allocated at runtime |

### Unions and Bit-fields
Unions allow interpreting the same memory as different types — common for
register overlays and protocol frame parsing.

Bit-fields (`uint8_t flag : 1;`) let you name individual bits in a struct,
but their layout is **implementation-defined** — avoid for cross-platform protocols;
use explicit bit masking instead.

### Fixed-Width Integer Types (`<stdint.h>`)
Always use `uint8_t`, `int16_t`, `uint32_t`, etc. in embedded code. Plain `int`
has implementation-defined size. `size_t` for sizes; `uintptr_t` for pointer arithmetic.

### Macros vs `inline` Functions
| | Macros | `inline` functions |
|--|--------|-------------------|
| Type checking | No | Yes |
| Debuggable | No (no symbol) | Yes |
| Multiple evaluation | Yes (dangerous) | No |
| Preferred in embedded? | Constants only | Yes for small functions |

---

## Files in This Module

| File | Topic |
|------|-------|
| `bit_manipulation.c` | SET/CLEAR/TOGGLE/CHECK, bit tricks for interview |
| `pointers_and_memory.c` | Pointer arithmetic, function pointers, void pointers |
| `volatile_const_restrict.c` | `volatile`, `const volatile`, `restrict` with hardware examples |
| `endianness.c` | Detection at runtime, byte-swap, network byte order conversion |
| `memory_layout.c` | Visualizing `.text`/`.data`/`.bss`/stack/heap segment placement |
| `inline_macros.c` | Macro pitfalls vs type-safe inline functions |
| `unions_bitfields.c` | Register overlay with union, bit-field struct, safe vs unsafe use |
| `fixed_width_types.c` | Why `uint32_t` matters; size of `int` vs fixed types |

---

## Common Interview Questions

1. **What does `volatile` do? Give a real example where omitting it causes a bug.**
   > Without `volatile`, the compiler optimizes a polling loop to read the variable
   > once. An ISR updating the variable has no visible effect in the loop.

2. **What is `const volatile uint32_t *`? When would you use it?**
   > Read-only hardware status register. `const` prevents writes from this code;
   > `volatile` ensures every read goes to the actual hardware address.

3. **How do you set bit 5, clear bit 3, and toggle bit 7 of a register in one expression?**
   > `reg = (reg | (1U << 5)) & ~(1U << 3) ^ (1U << 7);`

4. **What is the size of `struct { char a; int b; char c; }` on a 32-bit system?**
   > Typically 12 bytes due to alignment padding. Use `__attribute__((packed))` or
   > reorder fields to minimize waste.

5. **How do you detect endianness at runtime without invoking undefined behavior?**
   > Write a known multi-byte value into a `union` that overlaps a `uint8_t` array,
   > then read the first byte.

6. **What is the difference between a null pointer, a void pointer, and a dangling pointer?**
   > Null: deliberately points to address 0 (invalid). Void: typeless pointer, requires
   > cast before dereference. Dangling: points to freed/out-of-scope memory — UB.

7. **Why are bit-fields not recommended for protocol parsing?**
   > Bit-field layout (bit order, padding) is implementation-defined. Two compilers
   > may produce different layouts for the same struct.

8. **What is a function pointer? Write the syntax for a pointer to `int f(int, int)`.**
   > `int (*fp)(int, int) = f;` — used heavily in embedded for jump tables, callbacks,
   > and state machine dispatch tables.

---

## Further Reading

- C99/C11 standard: bit manipulation, `<stdint.h>`, `volatile`
- *C Programming: A Modern Approach* — K.N. King, Chapters 10, 12
- ARM Cortex-M Technical Reference Manual — volatile and memory ordering
