// volatile, const volatile, and restrict — embedded systems usage
// Demonstrates why each qualifier matters at hardware level
// Time complexity: N/A
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out volatile_const_restrict.c && ./out

#include <stdio.h>
#include <stdint.h>

// ─── Simulated Hardware Registers ─────────────────────────────────────────────
//
// In real MCU code, these would be:
//   #define UART_DR  (*((volatile uint32_t *)0x40004004))
//
// Here we simulate them with regular variables so the code runs on a host.

static uint32_t _sim_gpio_idr = 0x00000020;  // simulated input data register
static uint32_t _sim_uart_dr  = 0x00000041;  // simulated data register ('A' = 0x41)
static uint32_t _sim_gpio_odr = 0x00000000;  // simulated output data register

// READ-ONLY hardware register — can change externally but must not be written
// const: this code cannot write to it
// volatile: compiler must re-read from the address on every access
volatile const uint32_t * const GPIO_IDR =
    (volatile const uint32_t *)&_sim_gpio_idr;

// READ-WRITE hardware register (output)
volatile uint32_t * const GPIO_ODR =
    (volatile uint32_t *)&_sim_gpio_odr;

// READ-WRITE data register
volatile uint32_t * const UART_DR =
    (volatile uint32_t *)&_sim_uart_dr;

// ─── 1. volatile: Why Polling Without It Is Broken ────────────────────────────
//
// Without volatile, an optimizing compiler may generate:
//   r = *UART_DR;   // read once into register
//   while (r == 0)  // loop forever comparing the register — never re-reads memory
//
// With volatile, EVERY iteration re-reads from the hardware address.

uint8_t read_uart_byte(void) {
    // Wait until data is ready (bit 0 of a status register would normally be checked;
    // here we just read directly to demonstrate the volatile access pattern)
    uint32_t byte = *UART_DR;  // volatile: compiler MUST read from this address
    return (uint8_t)(byte & 0xFF);
}

// ─── 2. const volatile: Read-Only Hardware Register ───────────────────────────
//
// GPIO_IDR is read-only (cannot write to a pin input register).
// const: prevents accidental writes from firmware.
// volatile: hardware changes the value — must always re-read.

uint8_t read_pin(uint8_t pin_num) {
    return (uint8_t)((*GPIO_IDR >> pin_num) & 1U);
}

// ─── 3. ISR → Main Communication With volatile ────────────────────────────────
//
// A variable modified in an ISR and read in main MUST be volatile.
// Without volatile, the compiler may hoist the read out of the loop.

volatile uint8_t  g_rx_byte    = 0;
volatile uint8_t  g_data_ready = 0;

// Simulate an ISR being called externally
void UART_IRQHandler_sim(void) {
    g_rx_byte    = (uint8_t)(*UART_DR & 0xFF);
    g_data_ready = 1;
}

void isr_volatile_demo(void) {
    g_data_ready = 0;
    UART_IRQHandler_sim();  // simulate ISR fire

    // Without volatile: compiler may never re-read g_data_ready → infinite loop
    // With volatile:    correctly exits when ISR sets the flag
    while (!g_data_ready) { /* wait */ }
    printf("Received byte from ISR: 0x%02X ('%c')\n", g_rx_byte, g_rx_byte);
}

// ─── 4. restrict: Non-Aliasing Pointer Hint ───────────────────────────────────
//
// `restrict` tells the compiler: "no other pointer in this scope aliases this memory".
// Allows the compiler to keep values in registers instead of re-loading after stores.
// Important for DSP/DMA memcpy implementations.

void add_arrays(const int * restrict a,
                const int * restrict b,
                int       * restrict result,
                int len) {
    for (int i = 0; i < len; i++) {
        result[i] = a[i] + b[i];   // compiler can vectorize because a/b/result don't alias
    }
}

// ─── 5. Common Mistake: Missing volatile in a Timeout Loop ───────────────────

// Correct version
uint32_t wait_for_flag_correct(const volatile uint32_t *status_reg, uint32_t flag,
                               uint32_t max_tries) {
    uint32_t tries = 0;
    while (!(*status_reg & flag) && tries < max_tries) {
        tries++;
    }
    return tries;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== volatile / const volatile / restrict demo ===\n\n");

    // 1. Read from volatile const register
    printf("GPIO_IDR pin 5 state: %u (expect 1 — bit 5 of 0x20)\n",
           read_pin(5));

    // 2. Write to volatile output register
    *GPIO_ODR |= (1U << 3);   // Set pin 3
    printf("GPIO_ODR after set pin 3: 0x%08X (expect 0x00000008)\n", *GPIO_ODR);

    // 3. UART read
    uint8_t b = read_uart_byte();
    printf("UART byte: 0x%02X ('%c') (expect 0x41 = 'A')\n", b, b);

    // 4. ISR communication
    printf("\n--- ISR volatile communication ---\n");
    isr_volatile_demo();

    // 5. restrict
    printf("\n--- restrict: add_arrays ---\n");
    int src_a[4] = {1, 2, 3, 4};
    int src_b[4] = {10, 20, 30, 40};
    int res[4];
    add_arrays(src_a, src_b, res, 4);
    printf("result: %d %d %d %d (expect 11 22 33 44)\n",
           res[0], res[1], res[2], res[3]);

    // 6. Timeout loop
    _sim_gpio_idr = 0x00000001;  // set bit 0 of simulated register
    uint32_t tries = wait_for_flag_correct(GPIO_IDR, 0x1, 1000);
    printf("\nwait_for_flag found bit 0 in %u try (expect 1)\n", tries + 1);

    return 0;
}
