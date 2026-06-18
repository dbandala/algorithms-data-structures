// Bit manipulation fundamentals for embedded systems
// Covers: SET, CLEAR, TOGGLE, CHECK, EXTRACT, INSERT, count, reverse
// Time complexity: O(1) per operation (except count_bits O(log n) with Kernighan)
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out bit_manipulation.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// ─── Basic Register Operations ────────────────────────────────────────────────

// Set bit at position n (0 = LSB)
static inline uint32_t bit_set(uint32_t reg, uint8_t n) {
    return reg | (1U << n);
}

// Clear bit at position n
static inline uint32_t bit_clear(uint32_t reg, uint8_t n) {
    return reg & ~(1U << n);
}

// Toggle bit at position n
static inline uint32_t bit_toggle(uint32_t reg, uint8_t n) {
    return reg ^ (1U << n);
}

// Check whether bit n is set — returns true/false
static inline bool bit_check(uint32_t reg, uint8_t n) {
    return (reg >> n) & 1U;
}

// ─── Multi-bit Field Operations ───────────────────────────────────────────────

// Extract a bit-field: extract 'width' bits starting at 'start'
// e.g. extract_field(0xABCD, 4, 4) → bits [7:4] → 0xC
static inline uint32_t extract_field(uint32_t reg, uint8_t start, uint8_t width) {
    uint32_t mask = (1U << width) - 1U;
    return (reg >> start) & mask;
}

// Insert a bit-field: write 'val' into bits [start + width - 1 : start]
static inline uint32_t insert_field(uint32_t reg, uint32_t val,
                                    uint8_t start, uint8_t width) {
    uint32_t mask = ((1U << width) - 1U) << start;
    return (reg & ~mask) | ((val << start) & mask);
}

// ─── Interview Classics ───────────────────────────────────────────────────────

// Count set bits — Brian Kernighan's algorithm
// Each iteration clears the lowest set bit: n &= (n - 1)
// Time complexity: O(k) where k = number of set bits
int count_bits(uint32_t n) {
    int count = 0;
    while (n) {
        n &= (n - 1);   // clears the lowest set bit
        count++;
    }
    return count;
}

// Check if n is a power of 2 (exactly one bit set, n > 0)
bool is_power_of_two(uint32_t n) {
    return n && !(n & (n - 1));
}

// Find position of the lowest set bit (1-indexed; returns 0 if n == 0)
int lowest_set_bit_pos(uint32_t n) {
    if (n == 0) return 0;
    int pos = 1;
    while (!(n & 1U)) {
        n >>= 1;
        pos++;
    }
    return pos;
}

// Reverse bits of a 32-bit integer
uint32_t reverse_bits(uint32_t n) {
    uint32_t result = 0;
    for (int i = 0; i < 32; i++) {
        result = (result << 1) | (n & 1U);
        n >>= 1;
    }
    return result;
}

// Swap two integers without a temporary variable using XOR
// Note: undefined behaviour if a == b (same memory location)
void swap_xor(int *a, int *b) {
    if (a == b) return;     // guard: same address would zero both
    *a ^= *b;
    *b ^= *a;
    *a ^= *b;
}

// ─── Tests ────────────────────────────────────────────────────────────────────

int main(void) {
    // Basic operations on a simulated control register
    uint32_t reg = 0x00000000;

    reg = bit_set(reg, 5);   printf("set  bit 5:  0x%08X (expect 0x00000020)\n", reg);
    reg = bit_set(reg, 0);   printf("set  bit 0:  0x%08X (expect 0x00000021)\n", reg);
    reg = bit_clear(reg, 5); printf("clr  bit 5:  0x%08X (expect 0x00000001)\n", reg);
    reg = bit_toggle(reg, 3);printf("tog  bit 3:  0x%08X (expect 0x00000009)\n", reg);
    printf("chk  bit 3:  %d (expect 1)\n", bit_check(reg, 3));
    printf("chk  bit 1:  %d (expect 0)\n", bit_check(reg, 1));

    // Bit-field operations (simulating a UART config register)
    // Bits [5:3] = baud divider (3 bits), bits [7:6] = parity mode (2 bits)
    uint32_t uart_cfg = 0;
    uart_cfg = insert_field(uart_cfg, 5, 3, 3);   // baud divider = 5
    uart_cfg = insert_field(uart_cfg, 2, 6, 2);   // parity mode  = 2
    printf("\nuart_cfg after inserts: 0x%02X (expect 0xA8)\n", uart_cfg);
    printf("baud divider extracted: %u (expect 5)\n", extract_field(uart_cfg, 3, 3));
    printf("parity mode extracted:  %u (expect 2)\n", extract_field(uart_cfg, 6, 2));

    // Interview classics
    printf("\ncount_bits(0xFF):      %d (expect 8)\n",  count_bits(0xFF));
    printf("count_bits(0x10040):   %d (expect 2)\n",  count_bits(0x10040));
    printf("is_power_of_two(64):   %d (expect 1)\n",  is_power_of_two(64));
    printf("is_power_of_two(63):   %d (expect 0)\n",  is_power_of_two(63));
    printf("lowest_set_bit(0x18):  %d (expect 4)\n",  lowest_set_bit_pos(0x18));
    printf("reverse_bits(1):       0x%08X (expect 0x80000000)\n", reverse_bits(1));

    int x = 3, y = 9;
    swap_xor(&x, &y);
    printf("\nswap_xor(3,9): x=%d y=%d (expect x=9 y=3)\n", x, y);

    return 0;
}
