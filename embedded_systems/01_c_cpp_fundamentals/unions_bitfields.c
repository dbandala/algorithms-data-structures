// Unions and bit-fields for embedded register access
// Covers: union for type-punning, bit-field struct for register maps,
//         safe vs unsafe use, alternative: explicit masking
// Time complexity: O(1)
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out unions_bitfields.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <string.h>

// ─── 1. Union as Type Punning ─────────────────────────────────────────────────
//
// Access the same memory region as different types without undefined behaviour
// (C99/C11 explicitly permits union type-punning).
// Common use: split a uint32_t register into bytes, or parse protocol frames.

typedef union {
    uint32_t word;
    uint16_t half[2];
    uint8_t  bytes[4];
} WordView;

void union_type_punning_demo(void) {
    WordView v;
    v.word = 0x12345678U;

    printf("=== Union Type Punning ===\n");
    printf("word  = 0x%08X\n", v.word);
    printf("half[0] = 0x%04X  half[1] = 0x%04X\n", v.half[0], v.half[1]);
    printf("bytes: [0]=0x%02X [1]=0x%02X [2]=0x%02X [3]=0x%02X\n",
           v.bytes[0], v.bytes[1], v.bytes[2], v.bytes[3]);
    // On little-endian: bytes[0]=0x78 (LSB), bytes[3]=0x12 (MSB)
}

// ─── 2. Bit-field Struct for Register Overlay ─────────────────────────────────
//
// Gives named access to individual bit-fields in a hardware register.
// Readable code, but layout is compiler/platform dependent — never use for
// cross-platform protocol parsing. Acceptable for MCU peripheral register maps
// when targeting a specific compiler (e.g., CMSIS headers do this with GCC).

// Example: UART Status Register (simulated)
// Bit 0: TX_EMPTY — 1 when transmit buffer is empty
// Bit 1: RX_FULL  — 1 when receive buffer has data
// Bits [3:2]: ERROR_CODE — 00=none, 01=parity, 10=framing, 11=overrun
// Bits [7:4]: RESERVED

typedef union {
    struct {
        uint8_t tx_empty   : 1;  // bit 0
        uint8_t rx_full    : 1;  // bit 1
        uint8_t error_code : 2;  // bits [3:2]
        uint8_t reserved   : 4;  // bits [7:4]
    } bits;
    uint8_t byte;
} UartStatus_t;

void bitfield_demo(void) {
    UartStatus_t status;
    status.byte = 0x00;

    // Write via bit-fields
    status.bits.tx_empty   = 1;
    status.bits.rx_full    = 1;
    status.bits.error_code = 2;  // framing error

    printf("\n=== Bit-field Register Overlay ===\n");
    printf("status.byte = 0x%02X\n", status.byte);
    // Expected: 0b00001011 = 0x0B
    // tx_empty=1 (bit0), rx_full=1 (bit1), error_code=10 (bits3:2)
    printf("tx_empty=%u  rx_full=%u  error_code=%u\n",
           status.bits.tx_empty,
           status.bits.rx_full,
           status.bits.error_code);

    // Read the same byte back via the union word member
    printf("Read as raw byte: 0x%02X (expect 0x0B)\n", status.byte);
}

// ─── 3. SAFE ALTERNATIVE: Explicit Bit Masking ───────────────────────────────
//
// When portability is required (cross-platform protocol), always use
// explicit masks and shifts — guaranteed layout.

#define UART_SR_TX_EMPTY_MSK   0x01U
#define UART_SR_RX_FULL_MSK    0x02U
#define UART_SR_ERROR_CODE_MSK 0x0CU
#define UART_SR_ERROR_CODE_POS 2U

static inline uint8_t uart_sr_get_error_code(uint8_t sr) {
    return (uint8_t)((sr & UART_SR_ERROR_CODE_MSK) >> UART_SR_ERROR_CODE_POS);
}

static inline uint8_t uart_sr_set_error_code(uint8_t sr, uint8_t code) {
    return (uint8_t)((sr & ~UART_SR_ERROR_CODE_MSK) |
                     ((code << UART_SR_ERROR_CODE_POS) & UART_SR_ERROR_CODE_MSK));
}

void explicit_mask_demo(void) {
    uint8_t sr = 0x00;
    sr |= UART_SR_TX_EMPTY_MSK;             // set TX_EMPTY
    sr |= UART_SR_RX_FULL_MSK;              // set RX_FULL
    sr  = uart_sr_set_error_code(sr, 2);    // set framing error

    printf("\n=== Explicit Mask (portable, preferred for protocols) ===\n");
    printf("sr = 0x%02X (expect 0x0B)\n", sr);
    printf("error_code = %u (expect 2)\n", uart_sr_get_error_code(sr));
}

// ─── 4. Union for Protocol Frame Parsing ─────────────────────────────────────

// CAN-style frame ID union: 11-bit standard ID
typedef union {
    struct {
        uint16_t id       : 11;   // bits [10:0]
        uint16_t rtr      : 1;    // bit 11 — remote transmission request
        uint16_t reserved : 4;    // bits [15:12]
    } fields;
    uint16_t raw;
} CanId_t;

void can_id_demo(void) {
    CanId_t frame;
    frame.raw = 0x0000;
    frame.fields.id  = 0x1A3;  // 11-bit ID = 419
    frame.fields.rtr = 0;

    printf("\n=== CAN ID Union ===\n");
    printf("raw = 0x%04X\n", frame.raw);
    printf("id = 0x%03X (%u)  rtr = %u\n",
           frame.fields.id, frame.fields.id, frame.fields.rtr);
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    union_type_punning_demo();
    bitfield_demo();
    explicit_mask_demo();
    can_id_demo();

    printf("\n=== Design Guidance ===\n");
    printf("Use bit-fields:     MCU register maps (compiler-specific, single-target)\n");
    printf("Use explicit masks: protocol parsing, cross-platform, safety-critical\n");
    printf("Use unions:         type-punning (endianness, frame split), NOT aliasing\n");

    return 0;
}
