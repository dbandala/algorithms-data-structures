// Memory-mapped I/O simulation and volatile pointer patterns
// In real hardware: peripheral registers live at fixed addresses from the datasheet.
// Here we simulate them so the code compiles and runs on a host machine.
// Time complexity: O(1) per access
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out memory_mapped_io.c && ./out

#include <stdio.h>
#include <stdint.h>

// ─── Simulated Peripheral Register Bank ──────────────────────────────────────
//
// On a real MCU (e.g., STM32):
//   #define GPIOA_BASE  0x40020000UL
//   #define GPIOA_MODER (*((volatile uint32_t *)(GPIOA_BASE + 0x00)))
//   #define GPIOA_ODR   (*((volatile uint32_t *)(GPIOA_BASE + 0x14)))
//   #define GPIOA_IDR   (*((volatile uint32_t *)(GPIOA_BASE + 0x10)))

// Simulated backing memory for the GPIO peripheral
static uint32_t _sim_MODER = 0x00000000;  // mode register (output/input/alt)
static uint32_t _sim_ODR   = 0x00000000;  // output data register
static uint32_t _sim_IDR   = 0x00000020;  // input data register (bit 5 = 1 from HW)

// Volatile pointers — mimic real MMIO pointer declarations
volatile uint32_t * const GPIO_MODER = (volatile uint32_t *)&_sim_MODER;
volatile uint32_t * const GPIO_ODR   = (volatile uint32_t *)&_sim_ODR;
volatile const uint32_t * const GPIO_IDR = (volatile const uint32_t *)&_sim_IDR;

// ─── GPIO Driver Using MMIO ────────────────────────────────────────────────────

#define GPIO_MODE_INPUT  0x0U
#define GPIO_MODE_OUTPUT 0x1U
#define MODE_BITS        2U       // 2 bits per pin in MODER

// Configure a pin's mode (2-bit field per pin in MODER)
static void gpio_set_mode(volatile uint32_t *moder, uint8_t pin, uint8_t mode) {
    uint32_t shift = (uint32_t)pin * MODE_BITS;
    uint32_t mask  = 0x3U << shift;
    *moder = (*moder & ~mask) | ((uint32_t)mode << shift);
}

// Write a pin HIGH or LOW via ODR
static void gpio_write_pin(volatile uint32_t *odr, uint8_t pin, uint8_t level) {
    if (level) {
        *odr |= (1U << pin);
    } else {
        *odr &= ~(1U << pin);
    }
}

// Read a pin from IDR
static uint8_t gpio_read_pin(volatile const uint32_t *idr, uint8_t pin) {
    return (uint8_t)((*idr >> pin) & 1U);
}

// ─── Register Struct Overlay Pattern ─────────────────────────────────────────
//
// Instead of separate macros per register, group them into a struct
// and cast the base address to a pointer. CMSIS headers use this approach.

typedef struct {
    volatile uint32_t MODER;   // offset 0x00
    volatile uint32_t OTYPER;  // offset 0x04
    volatile uint32_t OSPEEDR; // offset 0x08
    volatile uint32_t PUPDR;   // offset 0x0C
    volatile const uint32_t IDR; // offset 0x10 — read-only
    volatile uint32_t ODR;     // offset 0x14
} GPIO_TypeDef;

// In real code: #define GPIOA ((GPIO_TypeDef *)0x40020000UL)
// Here: point to our simulated backing memory
static uint32_t _sim_gpio_bank[6] = {0, 0, 0, 0, 0x00000020, 0};

static GPIO_TypeDef *const GPIOA = (GPIO_TypeDef *)_sim_gpio_bank;

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== MMIO: Individual Pointer Style ===\n");

    // Configure pin 3 as output
    gpio_set_mode(GPIO_MODER, 3, GPIO_MODE_OUTPUT);
    printf("MODER after pin 3 = OUTPUT: 0x%08X (expect 0x00000040)\n", *GPIO_MODER);

    // Set pin 3 high
    gpio_write_pin(GPIO_ODR, 3, 1);
    printf("ODR after pin 3 HIGH: 0x%08X (expect 0x00000008)\n", *GPIO_ODR);

    // Read pin 5 (simulated as HIGH in IDR)
    uint8_t pin5 = gpio_read_pin(GPIO_IDR, 5);
    printf("IDR pin 5 = %u (expect 1)\n", pin5);

    // Set pin 3 low
    gpio_write_pin(GPIO_ODR, 3, 0);
    printf("ODR after pin 3 LOW:  0x%08X (expect 0x00000000)\n", *GPIO_ODR);

    printf("\n=== MMIO: Struct Overlay Style (CMSIS approach) ===\n");

    // Configure pin 5 as output via struct
    uint32_t shift = 5U * MODE_BITS;
    GPIOA->MODER = (GPIOA->MODER & ~(0x3U << shift)) | ((uint32_t)GPIO_MODE_OUTPUT << shift);
    printf("GPIOA->MODER = 0x%08X\n", GPIOA->MODER);

    // Read pin from IDR via struct
    uint8_t pin5_struct = (uint8_t)((GPIOA->IDR >> 5) & 1U);
    printf("GPIOA->IDR pin 5 = %u (expect 1)\n", pin5_struct);

    printf("\nKey rule: EVERY peripheral register access MUST use a volatile pointer.\n");
    printf("Without volatile, the compiler may cache the value and never re-read it.\n");

    return 0;
}
