// Bit manipulation interview problems with solutions
// 20+ problems covering common embedded and algorithmic bit tricks
// Time complexity: O(1) per problem unless noted
//
// Compile: gcc -Wall -Wextra -std=c11 -o out bit_tricks.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// ─── 1. Count set bits (Kernighan's algorithm) ────────────────────────────────
int count_bits(uint32_t n) {
    int count = 0;
    while (n) { n &= (n - 1); count++; }
    return count;
}

// ─── 2. Check if power of 2 ──────────────────────────────────────────────────
bool is_power_of_two(uint32_t n) { return n && !(n & (n - 1)); }

// ─── 3. Find lowest set bit position (1-indexed, 0 if none) ──────────────────
int lowest_set_bit(uint32_t n) {
    if (!n) return 0;
    int pos = 1;
    while (!(n & 1U)) { n >>= 1; pos++; }
    return pos;
}

// ─── 4. Isolate the lowest set bit ───────────────────────────────────────────
// x & (-x) isolates the rightmost set bit
uint32_t isolate_lowest_bit(uint32_t n) { return n & (uint32_t)(-(int32_t)n); }

// ─── 5. Clear the lowest set bit ─────────────────────────────────────────────
uint32_t clear_lowest_bit(uint32_t n) { return n & (n - 1); }

// ─── 6. Reverse bits of 32-bit integer ───────────────────────────────────────
uint32_t reverse_bits(uint32_t n) {
    uint32_t r = 0;
    for (int i = 0; i < 32; i++) { r = (r << 1) | (n & 1U); n >>= 1; }
    return r;
}

// ─── 7. Swap two integers without a temp ─────────────────────────────────────
void swap_no_temp(int *a, int *b) {
    if (a == b) return;
    *a ^= *b; *b ^= *a; *a ^= *b;
}

// ─── 8. Check if two integers have opposite signs ────────────────────────────
bool opposite_signs(int a, int b) { return (a ^ b) < 0; }

// ─── 9. Compute absolute value without branching ─────────────────────────────
int abs_no_branch(int n) {
    int mask = n >> (sizeof(int) * 8 - 1);  // 0x00..00 if positive, 0xFF..FF if negative
    return (n + mask) ^ mask;
}

// ─── 10. Round up to next power of 2 ─────────────────────────────────────────
uint32_t next_power_of_two(uint32_t n) {
    if (n == 0) return 1;
    n--;
    n |= n >> 1; n |= n >> 2; n |= n >> 4;
    n |= n >> 8; n |= n >> 16;
    return n + 1;
}

// ─── 11. Count bits that differ (Hamming distance) ───────────────────────────
int hamming_distance(uint32_t a, uint32_t b) { return count_bits(a ^ b); }

// ─── 12. Parity of a byte (even=0, odd=1) ────────────────────────────────────
uint8_t byte_parity(uint8_t b) {
    b ^= b >> 4; b ^= b >> 2; b ^= b >> 1;
    return b & 1U;
}

// ─── 13. Rotate left ─────────────────────────────────────────────────────────
uint32_t rotate_left(uint32_t val, uint8_t shift) {
    shift &= 31U;
    return (val << shift) | (val >> (32U - shift));
}

// ─── 14. Rotate right ────────────────────────────────────────────────────────
uint32_t rotate_right(uint32_t val, uint8_t shift) {
    shift &= 31U;
    return (val >> shift) | (val << (32U - shift));
}

// ─── 15. Set a range of bits ──────────────────────────────────────────────────
uint32_t set_bits_range(uint32_t reg, uint8_t start, uint8_t len) {
    uint32_t mask = ((1U << len) - 1U) << start;
    return reg | mask;
}

// ─── 16. Clear a range of bits ───────────────────────────────────────────────
uint32_t clear_bits_range(uint32_t reg, uint8_t start, uint8_t len) {
    uint32_t mask = ((1U << len) - 1U) << start;
    return reg & ~mask;
}

// ─── 17. Extract a bit field ──────────────────────────────────────────────────
uint32_t extract_field(uint32_t reg, uint8_t start, uint8_t len) {
    return (reg >> start) & ((1U << len) - 1U);
}

// ─── 18. Detect if any byte in uint32_t is zero (null-byte trick) ────────────
bool has_zero_byte(uint32_t v) {
    return ((v - 0x01010101UL) & ~v & 0x80808080UL) != 0;
}

// ─── 19. Multiply by power of 2 without * operator ───────────────────────────
uint32_t mul_pow2(uint32_t n, uint8_t k) { return n << k; }

// ─── 20. Divide by power of 2 (unsigned) ─────────────────────────────────────
uint32_t div_pow2(uint32_t n, uint8_t k) { return n >> k; }

// ─── 21. Align n up to multiple of m (m must be power of 2) ──────────────────
uint32_t align_up(uint32_t n, uint32_t m) { return (n + m - 1U) & ~(m - 1U); }
uint32_t align_down(uint32_t n, uint32_t m) { return n & ~(m - 1U); }

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== Bit Manipulation Interview Problems ===\n\n");

    printf("1.  count_bits(0xFF)          = %d  (expect 8)\n",   count_bits(0xFF));
    printf("1.  count_bits(0x10040)       = %d  (expect 2)\n",   count_bits(0x10040));

    printf("2.  is_power_of_two(64)       = %d  (expect 1)\n",   is_power_of_two(64));
    printf("2.  is_power_of_two(63)       = %d  (expect 0)\n",   is_power_of_two(63));

    printf("3.  lowest_set_bit(0x18)      = %d  (expect 4)\n",   lowest_set_bit(0x18));

    printf("4.  isolate_lowest_bit(0x6C)  = 0x%02X (expect 0x04)\n", isolate_lowest_bit(0x6C));

    printf("5.  clear_lowest_bit(0x6C)    = 0x%02X (expect 0x68)\n", clear_lowest_bit(0x6C));

    printf("6.  reverse_bits(1)           = 0x%08X (expect 0x80000000)\n", reverse_bits(1));

    int a = 3, b = 9;
    swap_no_temp(&a, &b);
    printf("7.  swap(3,9)                 → a=%d b=%d (expect 9 3)\n", a, b);

    printf("8.  opposite_signs(5,-3)      = %d  (expect 1)\n",   opposite_signs(5,-3));
    printf("8.  opposite_signs(5, 3)      = %d  (expect 0)\n",   opposite_signs(5, 3));

    printf("9.  abs_no_branch(-7)         = %d  (expect 7)\n",   abs_no_branch(-7));
    printf("9.  abs_no_branch(7)          = %d  (expect 7)\n",   abs_no_branch(7));

    printf("10. next_power_of_two(5)      = %u  (expect 8)\n",   next_power_of_two(5));
    printf("10. next_power_of_two(8)      = %u  (expect 8)\n",   next_power_of_two(8));

    printf("11. hamming_distance(3,5)     = %d  (expect 2)\n",   hamming_distance(3,5));

    printf("12. byte_parity(0x7F)         = %u  (expect 1 odd)\n", byte_parity(0x7F));
    printf("12. byte_parity(0xFF)         = %u  (expect 0 even)\n", byte_parity(0xFF));

    printf("13. rotate_left(0x01,4)       = 0x%08X (expect 0x00000010)\n", rotate_left(1,4));
    printf("14. rotate_right(0x80000000,4)= 0x%08X (expect 0x08000000)\n", rotate_right(0x80000000U,4));

    printf("15. set_bits_range(0,4,3)     = 0x%02X  (expect 0x70)\n", set_bits_range(0,4,3));
    printf("16. clear_bits_range(0xFF,4,3)= 0x%02X  (expect 0x8F)\n", clear_bits_range(0xFF,4,3));
    printf("17. extract_field(0xABCD,4,4) = 0x%X   (expect 0xC)\n",  extract_field(0xABCD,4,4));

    printf("18. has_zero_byte(0x01020300) = %d  (expect 1)\n",   has_zero_byte(0x01020300U));
    printf("18. has_zero_byte(0x01020304) = %d  (expect 0)\n",   has_zero_byte(0x01020304U));

    printf("19. mul_pow2(5, 3)            = %u  (expect 40)\n",  mul_pow2(5,3));
    printf("20. div_pow2(40, 3)           = %u  (expect 5)\n",   div_pow2(40,3));

    printf("21. align_up(13, 8)           = %u  (expect 16)\n",  align_up(13,8));
    printf("21. align_down(13, 8)         = %u  (expect 8)\n",   align_down(13,8));

    return 0;
}
