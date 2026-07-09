// SPI (Serial Peripheral Interface) — all 4 CPOL/CPHA modes, software bit-bang
// Covers: CPOL/CPHA matrix, full-duplex exchange, CS management
// Time complexity: O(N) for N-byte transfer
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out spi.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// ─── CPOL / CPHA Modes ────────────────────────────────────────────────────────
//
// CPOL = Clock Polarity: idle state of SCLK
//   CPOL=0: SCLK idle LOW
//   CPOL=1: SCLK idle HIGH
//
// CPHA = Clock Phase: which edge samples data
//   CPHA=0: data captured on the FIRST edge (idle→active)
//   CPHA=1: data captured on the SECOND edge (active→idle)
//
// Mode | CPOL | CPHA | Idle CLK | Sample on
//  0   |  0   |  0   | Low      | Rising edge
//  1   |  0   |  1   | Low      | Falling edge
//  2   |  1   |  0   | High     | Falling edge
//  3   |  1   |  1   | High     | Rising edge
//
// Most sensors/ICs use Mode 0 or Mode 3. Check the datasheet!

typedef enum {
    SPI_MODE_0 = 0,   // CPOL=0, CPHA=0
    SPI_MODE_1 = 1,   // CPOL=0, CPHA=1
    SPI_MODE_2 = 2,   // CPOL=1, CPHA=0
    SPI_MODE_3 = 3,   // CPOL=1, CPHA=1
} SpiMode;

// ─── Simulated GPIO Signals ───────────────────────────────────────────────────
//
// In real firmware: each "gpio_write" call sets/clears a hardware register bit.

static bool g_sclk = false;
static bool g_mosi = false;
static bool g_cs   = true;   // CS active-low; idle = HIGH
static bool g_miso = false;  // driven by slave

// Simulated slave response: shifts out 0xA3 for demonstration
static uint8_t g_slave_tx = 0xA3;
static int     g_slave_bit_idx = 0;

// Called by the master's bit-bang to read MISO from the slave
static bool slave_drive_miso(bool master_clk_high, SpiMode mode) {
    // Slave shifts on the same edge the master samples
    bool cpol = (mode == SPI_MODE_2 || mode == SPI_MODE_3);
    bool sample_on_rising = (mode == SPI_MODE_0 || mode == SPI_MODE_3);
    bool rising = (master_clk_high && !cpol) || (!master_clk_high && cpol);

    if (rising == sample_on_rising) {
        // Output the next bit (MSB first)
        int bit_pos = 7 - (g_slave_bit_idx % 8);
        g_slave_bit_idx++;
        return (g_slave_tx >> bit_pos) & 1U;
    }
    return g_miso; // hold current
}

// ─── Software SPI Bit-Bang ────────────────────────────────────────────────────

// Transfer one byte, return received byte from slave
uint8_t spi_transfer_byte(uint8_t tx_byte, SpiMode mode) {
    bool cpol = (mode == SPI_MODE_2 || mode == SPI_MODE_3);
    bool cpha = (mode == SPI_MODE_1 || mode == SPI_MODE_3);

    g_sclk = cpol;   // idle state
    uint8_t rx_byte = 0;

    for (int bit = 7; bit >= 0; bit--) {
        bool tx_bit = (tx_byte >> bit) & 1U;

        if (!cpha) {
            // CPHA=0: setup data BEFORE the first clock edge, sample ON first edge
            g_mosi = tx_bit;
            // Toggle clock (idle → active)
            g_sclk = !cpol;
            // Sample MISO on the first (active) edge
            g_miso = slave_drive_miso(g_sclk, mode);
            rx_byte |= (uint8_t)(g_miso << bit);
            // Toggle clock back (active → idle)
            g_sclk = cpol;
        } else {
            // CPHA=1: first edge is setup edge, second edge is sample edge
            g_sclk = !cpol;   // first edge
            g_mosi = tx_bit;  // setup data
            g_sclk = cpol;    // second edge
            g_miso = slave_drive_miso(g_sclk, mode);
            rx_byte |= (uint8_t)(g_miso << bit);
        }
    }
    g_sclk = cpol;   // return to idle
    return rx_byte;
}

// Transfer a buffer, full-duplex
void spi_transfer(const uint8_t *tx, uint8_t *rx, size_t len, SpiMode mode) {
    g_cs = false;             // assert CS (active low)
    g_slave_bit_idx = 0;      // reset slave bit counter

    for (size_t i = 0; i < len; i++) {
        rx[i] = spi_transfer_byte(tx[i], mode);
    }

    g_cs = true;              // deassert CS
}

// ─── Tests ────────────────────────────────────────────────────────────────────

static const char *mode_name(SpiMode m) {
    switch (m) {
        case SPI_MODE_0: return "Mode 0 (CPOL=0,CPHA=0)";
        case SPI_MODE_1: return "Mode 1 (CPOL=0,CPHA=1)";
        case SPI_MODE_2: return "Mode 2 (CPOL=1,CPHA=0)";
        case SPI_MODE_3: return "Mode 3 (CPOL=1,CPHA=1)";
        default: return "Unknown";
    }
}

int main(void) {
    printf("=== SPI Bit-Bang — All 4 Modes ===\n\n");

    // Test each mode — slave always sends 0xA3 back
    SpiMode modes[] = {SPI_MODE_0, SPI_MODE_1, SPI_MODE_2, SPI_MODE_3};
    uint8_t tx_buf[1] = {0x55};
    uint8_t rx_buf[1];

    for (int i = 0; i < 4; i++) {
        rx_buf[0] = 0;
        g_slave_tx = 0xA3;
        spi_transfer(tx_buf, rx_buf, 1, modes[i]);
        printf("%s: sent 0x%02X, received 0x%02X (expect 0xA3)\n",
               mode_name(modes[i]), tx_buf[0], rx_buf[0]);
    }

    printf("\n=== Multi-byte Transfer (Mode 0) ===\n");
    uint8_t tx3[3] = {0x01, 0x02, 0x03};
    uint8_t rx3[3] = {0, 0, 0};
    // Slave sends 0xA3 as first byte, then repeats pattern
    g_slave_tx = 0xA3;
    spi_transfer(tx3, rx3, 3, SPI_MODE_0);
    printf("Sent:     0x%02X 0x%02X 0x%02X\n", tx3[0], tx3[1], tx3[2]);
    printf("Received: 0x%02X 0x%02X 0x%02X\n", rx3[0], rx3[1], rx3[2]);

    printf("\n=== CPOL/CPHA Summary ===\n");
    printf("Mode 0: CLK idle LOW,  sample on RISING  edge — most common\n");
    printf("Mode 1: CLK idle LOW,  sample on FALLING edge\n");
    printf("Mode 2: CLK idle HIGH, sample on FALLING edge\n");
    printf("Mode 3: CLK idle HIGH, sample on RISING  edge\n");
    printf("Always check the slave datasheet for supported modes!\n");

    return 0;
}
