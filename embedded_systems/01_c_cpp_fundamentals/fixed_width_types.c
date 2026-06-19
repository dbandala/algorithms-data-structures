// Fixed-width integer types and macros vs inline functions
// Covers: stdint.h types, why plain int is dangerous, macro pitfalls,
//         type-safe inline functions, compile-time assertions
// Time complexity: N/A
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out fixed_width_types.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// ─── 1. Why Fixed-Width Types Matter ─────────────────────────────────────────
//
// Plain `int` is at least 16 bits — but can be 16, 32, or 64 bits depending on
// the platform and compiler. On an 8-bit MCU, `int` may be 16 bits; on a 64-bit
// host, it is 32 bits. This silently changes arithmetic and struct layout.
//
// Rule: use fixed-width types for all protocol fields, register maps, and buffers.
//       Use `int` / `size_t` only for loop counters and sizes.

void type_sizes_demo(void) {
    printf("=== Type Sizes on This Platform ===\n");
    printf("char:      %zu byte(s)\n", sizeof(char));
    printf("short:     %zu byte(s)\n", sizeof(short));
    printf("int:       %zu byte(s)\n", sizeof(int));
    printf("long:      %zu byte(s)\n", sizeof(long));
    printf("long long: %zu byte(s)\n", sizeof(long long));
    printf("uint8_t:   %zu byte (always 1)\n", sizeof(uint8_t));
    printf("uint16_t:  %zu bytes (always 2)\n", sizeof(uint16_t));
    printf("uint32_t:  %zu bytes (always 4)\n", sizeof(uint32_t));
    printf("uint64_t:  %zu bytes (always 8)\n", sizeof(uint64_t));
    printf("size_t:    %zu bytes\n", sizeof(size_t));
    printf("uintptr_t: %zu bytes (pointer size)\n", sizeof(uintptr_t));
}

// ─── 2. Macro Pitfalls ───────────────────────────────────────────────────────

// BAD: macro with multiple evaluation side-effects
#define MAX_MACRO(a, b) ((a) > (b) ? (a) : (b))

// GOOD: type-safe inline function (preferred in embedded C/C++)
static inline int32_t max_int32(int32_t a, int32_t b) {
    return (a > b) ? a : b;
}

// BAD: macro with no type information — silently wrong on promotion
#define SQUARE_MACRO(x) ((x) * (x))

// GOOD: inline — type-checked, no double evaluation
static inline int32_t square_i32(int32_t x) { return x * x; }
static inline float   square_f32(float x)   { return x * x; }

void macro_pitfall_demo(void) {
    printf("\n=== Macro vs Inline Pitfalls ===\n");

    int a = 3;
    // Macro double-evaluation: if a++ is passed, it increments twice!
    // MAX_MACRO(a++, 5) expands to ((a++) > (5) ? (a++) : (5))
    // Use the inline function instead:
    int result = max_int32(a, 5);
    printf("max_int32(3, 5) = %d (expect 5)\n", result);

    // SQUARE: macro with side effect input
    // int b = 3;
    // SQUARE_MACRO(b++) → ((b++) * (b++)) — b incremented twice, UB!
    int b = 4;
    printf("square_i32(4) = %d (expect 16)\n", square_i32(b));
    printf("square_f32(1.5f) = %.2f (expect 2.25)\n", square_f32(1.5f));
}

// ─── 3. Compile-Time Assertions ───────────────────────────────────────────────
//
// Use _Static_assert to catch struct size mismatches at compile time.
// Zero runtime cost — errors appear as compiler errors, not runtime crashes.

typedef struct {
    uint8_t  type;      // 1 byte
    uint8_t  flags;     // 1 byte
    uint16_t length;    // 2 bytes
    uint32_t checksum;  // 4 bytes
} PacketHeader;        // expected total: 8 bytes

// This line causes a compile error if the struct size is not exactly 8 bytes
_Static_assert(sizeof(PacketHeader) == 8,
               "PacketHeader must be exactly 8 bytes for protocol compatibility");

void static_assert_demo(void) {
    printf("\n=== Compile-Time Assertion ===\n");
    printf("sizeof(PacketHeader) = %zu (expect 8)\n", sizeof(PacketHeader));
    // If padding changed the size, _Static_assert would catch it at compile time
}

// ─── 4. Integer Promotion and Overflow Traps ─────────────────────────────────

void overflow_demo(void) {
    printf("\n=== Integer Overflow / Promotion Traps ===\n");

    uint8_t a = 200U;
    uint8_t b = 100U;

    // Trap: result of arithmetic on uint8_t is promoted to int — no wrap here
    // but when assigned back to uint8_t it wraps
    uint8_t sum8 = (uint8_t)(a + b);  // 300 wraps to 44
    printf("uint8_t (200+100) wraps to: %u (expect 44)\n", sum8);

    // Safe pattern: do arithmetic in a wider type, then check/clip
    uint32_t sum32 = (uint32_t)a + (uint32_t)b;  // 300 — no overflow
    uint8_t  clipped = (sum32 > 255U) ? 255U : (uint8_t)sum32;
    printf("saturated at 255: %u (expect 255)\n", clipped);

    // Trap: unsigned subtraction underflow
    uint8_t x = 5U, y = 10U;
    uint8_t diff = (uint8_t)(x - y);  // wraps to 251
    printf("uint8_t (5-10) wraps to: %u (expect 251)\n", diff);
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    type_sizes_demo();
    macro_pitfall_demo();
    static_assert_demo();
    overflow_demo();
    return 0;
}
