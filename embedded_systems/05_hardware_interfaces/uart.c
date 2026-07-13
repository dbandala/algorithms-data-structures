// UART — framing, baud rate calculation, software bit-bang UART TX
// Covers: frame format, baud error calculation, bit-banging
// Time complexity: O(N) for N-byte transfer
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out uart.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

// ─── UART Frame Format ────────────────────────────────────────────────────────
//
// Asynchronous — no clock line. Both ends must be configured identically.
//
// Line idle:  HIGH (mark state = 1)
// Start bit:  1 bit LOW (space = 0) — signals start of frame to receiver
// Data bits:  5–9 bits LSB first (typically 8)
// Parity bit: optional — even, odd, or none
// Stop bits:  1 or 2 bits HIGH (mark) — gives receiver time to process
//
// Total frame for 8N1 (8 data, no parity, 1 stop): 10 bits per byte
// At 115200 baud: 10 / 115200 ≈ 86.8 µs per byte

typedef enum { PARITY_NONE, PARITY_EVEN, PARITY_ODD } UartParity;

// ─── Baud Rate Error Calculation ─────────────────────────────────────────────
//
// Hardware UART generates baud rate by dividing the peripheral clock:
//   actual_baud = F_clk / divisor   (divisor must be an integer)
// Error must be < ~3% for reliable reception.

typedef struct {
    uint32_t f_clk;          // peripheral clock Hz
    uint32_t target_baud;    // desired baud rate
    uint32_t divisor;        // rounded integer divisor
    uint32_t actual_baud;    // resulting baud rate
    double   error_pct;      // percentage error
} BaudCalc;

BaudCalc calc_baud(uint32_t f_clk, uint32_t target_baud) {
    BaudCalc r;
    r.f_clk       = f_clk;
    r.target_baud = target_baud;
    r.divisor     = (f_clk + target_baud / 2) / target_baud;  // round to nearest
    r.actual_baud = f_clk / r.divisor;
    r.error_pct   = fabs((double)r.actual_baud - (double)target_baud)
                    / (double)target_baud * 100.0;
    return r;
}

void print_baud_calc(BaudCalc *b) {
    printf("  F_clk=%uHz, target=%ubaud → divisor=%u → actual=%ubaud, error=%.3f%%\n",
           b->f_clk, b->target_baud, b->divisor, b->actual_baud, b->error_pct);
    printf("  Status: %s\n", b->error_pct < 3.0 ? "OK (< 3%)" : "WARNING: > 3% — unreliable!");
}

// ─── Parity Calculation ───────────────────────────────────────────────────────

static bool calc_parity_bit(uint8_t data, UartParity type) {
    uint8_t count = 0;
    for (int i = 0; i < 8; i++) count += (data >> i) & 1U;
    if (type == PARITY_EVEN) return (count % 2) != 0;  // 1 to make total even
    if (type == PARITY_ODD)  return (count % 2) == 0;  // 1 to make total odd
    return false;
}

// ─── Software UART TX (Bit-Bang) ──────────────────────────────────────────────
//
// In real hardware: each "delay" is a hardware timer interrupt or busy-wait of
// exactly one bit period (= 1/baud seconds).

#define BAUD_RATE      115200U
#define BIT_PERIOD_US  (1000000U / BAUD_RATE)  // ≈ 8 µs at 115200

static bool g_tx_pin = true;   // idle HIGH

// Simulate one bit-period delay (real: hardware timer or DWT counter)
static void delay_bit(void) {
    // No actual delay in this simulation
    (void)BIT_PERIOD_US;
}

void uart_tx_byte(uint8_t byte, UartParity parity) {
    printf("  TX 0x%02X ('%c')  bits: ",
           byte, (byte >= 0x20 && byte < 0x7F) ? byte : '.');

    // Start bit (LOW)
    g_tx_pin = false;
    printf("S");
    delay_bit();

    // Data bits (LSB first)
    for (int i = 0; i < 8; i++) {
        g_tx_pin = (byte >> i) & 1U;
        printf("%u", (byte >> i) & 1U);
        delay_bit();
    }

    // Parity bit (optional)
    if (parity != PARITY_NONE) {
        g_tx_pin = calc_parity_bit(byte, parity);
        printf("P%u", g_tx_pin);
        delay_bit();
    }

    // Stop bit (HIGH)
    g_tx_pin = true;
    printf("T\n");
    delay_bit();
}

void uart_tx_string(const char *s, UartParity parity) {
    while (*s) uart_tx_byte((uint8_t)*s++, parity);
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== UART Baud Rate Calculations ===\n\n");

    // Common MCU + baud rate combinations
    BaudCalc b;
    b = calc_baud(16000000, 9600);    print_baud_calc(&b);
    b = calc_baud(16000000, 115200);  print_baud_calc(&b);
    b = calc_baud(48000000, 115200);  print_baud_calc(&b);
    b = calc_baud(8000000,  115200);  print_baud_calc(&b);  // tricky
    b = calc_baud(72000000, 1000000); print_baud_calc(&b);  // 1 Mbaud

    printf("\n=== Software UART TX (8N1) ===\n");
    printf("Format: S = start bit, bits 0-7 LSB first, T = stop bit\n\n");
    uart_tx_string("Hi", PARITY_NONE);

    printf("\n=== Software UART TX (8E1 — even parity) ===\n");
    uart_tx_byte(0x41, PARITY_EVEN);   // 'A' = 0x41 = 0b01000001 → 2 ones → even → parity=0
    uart_tx_byte(0x43, PARITY_EVEN);   // 'C' = 0x43 = 0b01000011 → 3 ones → odd  → parity=1

    printf("\n=== Frame Summary ===\n");
    printf("8N1: 1 start + 8 data + 1 stop = 10 bits/byte\n");
    printf("8E1: 1 start + 8 data + 1 parity + 1 stop = 11 bits/byte\n");
    printf("Bit period at 115200 baud: ~%u µs\n", BIT_PERIOD_US);
    printf("Max throughput 8N1/115200: %.0f bytes/s\n",
           115200.0 / 10.0);

    return 0;
}
