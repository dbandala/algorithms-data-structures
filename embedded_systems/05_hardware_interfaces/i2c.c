// I2C (Inter-Integrated Circuit) — software bit-bang implementation
// Covers: START/STOP conditions, byte write/read, ACK/NACK, addressing
// Time complexity: O(N) for N bytes
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out i2c.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// ─── I2C Protocol Review ──────────────────────────────────────────────────────
//
// Two open-drain wires pulled high externally:
//   SDA (Serial Data)   — data line
//   SCL (Serial Clock)  — clock line (master-driven normally)
//
// Transaction template:
//   START → [7-bit address][R/W] → ACK → [DATA]... → ACK/NACK → STOP
//
// START:  SDA falls while SCL is HIGH
// STOP:   SDA rises  while SCL is HIGH
// DATA:   SDA changes only while SCL is LOW; sampled when SCL is HIGH
// ACK:    SDA = 0 after byte reception (pulled low by receiver)
// NACK:   SDA = 1 after byte reception (SDA not pulled)
//
// Clock stretching: slave holds SCL LOW to pause master.
// Not simulated here for simplicity.

// ─── Simulated Signals ────────────────────────────────────────────────────────

static bool g_sda = true;   // HIGH = released (open-drain)
static bool g_scl = true;   // HIGH = released

// Simulated slave device
#define SLAVE_ADDR  0x48U    // example: TMP102 temperature sensor
static uint8_t g_slave_reg  = 0x00;  // register pointer
static uint8_t g_slave_data[2] = {0x19, 0x00};  // register 0: 0x19 (25°C)

// Slave drives SDA to 0 (ACK) or leaves it at 1 (NACK)
static bool g_slave_ack = false;

// ─── GPIO Operations ──────────────────────────────────────────────────────────
// In real firmware: these write to GPIO registers.

static void sda_high(void) { g_sda = true; }
static void sda_low(void)  { g_sda = false; }
static void scl_high(void) { g_scl = true; }
static void scl_low(void)  { g_scl = false; }
static bool sda_read(void) { return g_sda; }

// ─── I2C Primitives ───────────────────────────────────────────────────────────

static void i2c_start(void) {
    sda_high(); scl_high();
    sda_low();  // SDA falls while SCL high → START
    scl_low();
}

static void i2c_stop(void) {
    sda_low(); scl_high();
    sda_high(); // SDA rises while SCL high → STOP
}

// Send one byte; returns true if ACK received
static bool i2c_write_byte(uint8_t byte) {
    for (int bit = 7; bit >= 0; bit--) {
        if ((byte >> bit) & 1U) sda_high();
        else                    sda_low();
        scl_high();   // slave samples SDA here
        scl_low();
    }
    // ACK/NACK: release SDA, slave drives it
    sda_high();

    // Simulate slave ACK logic:
    // If byte is the slave address (write), ACK; if register byte, ACK; if unknown, NACK
    if (byte == ((SLAVE_ADDR << 1) | 0) ||   // address + write
        byte == ((SLAVE_ADDR << 1) | 1) ||   // address + read
        byte == 0x00) {                       // register 0 pointer
        g_slave_ack = true;
        g_sda = false;   // slave pulls SDA low = ACK
    } else {
        g_slave_ack = false;
        g_sda = true;    // NACK
    }

    scl_high();   // master pulses SCL for ACK bit
    bool ack = !sda_read();   // ACK = SDA LOW
    scl_low();
    sda_high();   // release SDA
    g_sda = true; // release simulation

    return ack;
}

// Read one byte; send ACK if ack=true (more bytes coming), NACK if ack=false (last byte)
static uint8_t i2c_read_byte(bool ack) {
    uint8_t byte = 0;
    sda_high();   // release SDA — slave drives it
    for (int bit = 7; bit >= 0; bit--) {
        scl_high();
        // Simulate slave driving data based on register pointer
        bool slave_bit = (g_slave_data[g_slave_reg] >> bit) & 1U;
        g_sda = slave_bit;
        byte |= (uint8_t)((uint8_t)slave_bit << bit);
        scl_low();
    }
    g_sda = true;  // release slave simulation

    // Master sends ACK or NACK
    if (ack) { sda_low();  }   // ACK — more bytes
    else     { sda_high(); }   // NACK — last byte
    scl_high();
    scl_low();
    sda_high();

    return byte;
}

// ─── Higher-Level I2C Transactions ────────────────────────────────────────────

// Write N bytes to a register
bool i2c_write_reg(uint8_t dev_addr, uint8_t reg_addr,
                   const uint8_t *data, uint8_t len) {
    i2c_start();
    if (!i2c_write_byte((uint8_t)((dev_addr << 1) | 0))) {
        i2c_stop();
        return false;  // NACK on address — device not present
    }
    g_slave_reg = reg_addr;
    if (!i2c_write_byte(reg_addr)) {
        i2c_stop();
        return false;  // NACK on register pointer
    }
    for (uint8_t i = 0; i < len; i++) {
        i2c_write_byte(data[i]);
    }
    i2c_stop();
    return true;
}

// Read N bytes starting from a register (write reg pointer, then repeated START + read)
bool i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *buf, uint8_t len) {
    // Write register pointer
    i2c_start();
    if (!i2c_write_byte((uint8_t)((dev_addr << 1) | 0))) { i2c_stop(); return false; }
    g_slave_reg = reg_addr;
    if (!i2c_write_byte(reg_addr)) { i2c_stop(); return false; }

    // Repeated START + address with read bit
    i2c_start();
    if (!i2c_write_byte((uint8_t)((dev_addr << 1) | 1))) { i2c_stop(); return false; }

    for (uint8_t i = 0; i < len; i++) {
        buf[i] = i2c_read_byte(i < len - 1);  // ACK all but last
    }
    i2c_stop();
    return true;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== I2C Software Bit-Bang ===\n\n");
    printf("Slave address: 0x%02X\n", SLAVE_ADDR);
    printf("Simulated register 0x00 = 0x%02X (TMP102 raw: 25°C)\n\n",
           g_slave_data[0]);

    // Write register pointer then read 1 byte
    uint8_t rx[2] = {0, 0};
    bool ok = i2c_read_reg(SLAVE_ADDR, 0x00, rx, 1);
    printf("i2c_read_reg(0x%02X, reg=0x00, 1 byte): ok=%d  data=0x%02X (expect 0x19)\n",
           SLAVE_ADDR, ok, rx[0]);

    // Try wrong address (should NACK)
    ok = i2c_read_reg(0x10, 0x00, rx, 1);
    printf("i2c_read_reg(wrong addr 0x10): ok=%d (expect 0 = NACK)\n", ok);

    printf("\n=== I2C Protocol Rules ===\n");
    printf("START:  SDA falls while SCL HIGH\n");
    printf("STOP:   SDA rises  while SCL HIGH\n");
    printf("DATA:   changes on SCL LOW, sampled on SCL HIGH\n");
    printf("ACK:    SDA driven LOW by receiver after each byte\n");
    printf("NACK:   SDA remains HIGH — stop, error, or last byte\n");
    printf("Pull-ups required: SDA and SCL must have external pull-up resistors\n");

    return 0;
}
