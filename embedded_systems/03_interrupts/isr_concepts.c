// ISR concepts — structure, volatile flag communication, and interrupt flag clearing
// Simulates the ISR ↔ main code data-sharing pattern used in real firmware
// Time complexity: O(1)
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out isr_concepts.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// ─── Shared State Between ISR and Main ───────────────────────────────────────
//
// RULES:
// 1. Any variable modified by an ISR and read by main MUST be volatile.
//    Without volatile, an optimizing compiler may cache the value in a register
//    and never re-read from memory.
// 2. For multi-byte values on an 8-bit MCU, use a critical section (disable IRQ)
//    around the read in main to prevent a torn read.
// 3. Keep ISR logic minimal — set a flag or copy one register value, then return.

volatile uint8_t  g_uart_rx_byte  = 0;   // last received byte
volatile bool     g_uart_rx_ready = false; // flag: new byte available
volatile uint32_t g_tick_count    = 0;   // incremented by SysTick-style ISR

// ─── Simulated ISRs ───────────────────────────────────────────────────────────
//
// In real firmware these would be:
//   void USART1_IRQHandler(void) { ... }
//   void SysTick_Handler(void)   { ... }
//
// Marked with __attribute__((interrupt)) or __attribute__((naked)) on some targets.
// Here we call them manually to demonstrate the communication pattern.

// UART receive ISR: called when a new byte arrives in the hardware data register
void UART_RX_IRQHandler_sim(uint8_t hw_data_register) {
    // STEP 1: Read the hardware register (on real hardware this also clears the IRQ flag)
    g_uart_rx_byte = hw_data_register;

    // STEP 2: Set the flag — main loop polls this
    g_uart_rx_ready = true;

    // Do NOT do any heavy processing here (no printf, no malloc, no blocking).
}

// SysTick ISR: fires every 1 ms (simulated)
void SysTick_Handler_sim(void) {
    g_tick_count++;
    // Clear the SysTick pending bit — on ARM: automatically cleared by hardware
}

// ─── Main Loop Pattern ────────────────────────────────────────────────────────
//
// Main code waits for flags set by ISRs, processes them, then clears the flags.

static void process_byte(uint8_t byte) {
    printf("  Processed byte: 0x%02X ('%c')\n", byte, (byte >= 0x20) ? byte : '?');
}

void main_loop_sim(void) {
    // Simulate 5 UART bytes arriving (each triggers the ISR)
    uint8_t incoming[5] = {'H', 'e', 'l', 'l', 'o'};
    printf("=== ISR ↔ Main Communication Pattern ===\n\n");

    for (int i = 0; i < 5; i++) {
        // --- Hardware fires ISR ---
        UART_RX_IRQHandler_sim(incoming[i]);

        // --- Main loop checks the flag ---
        if (g_uart_rx_ready) {
            // Atomically read and clear (on real hardware: disable IRQ for 32-bit read)
            uint8_t byte = g_uart_rx_byte;   // copy locally
            g_uart_rx_ready = false;          // clear flag AFTER copying

            process_byte(byte);
        }
    }
}

// ─── SysTick / Tick Counter Pattern ──────────────────────────────────────────

uint32_t get_tick(void) {
    return g_tick_count;  // volatile: always re-reads from memory
}

// Blocking delay using tick counter (simulated)
void delay_ticks_sim(uint32_t ticks_to_wait, uint32_t ticks_per_call) {
    uint32_t start = get_tick();
    // Simulate the tick passing
    for (uint32_t i = 0; i < ticks_to_wait; i++) {
        SysTick_Handler_sim();
        (void)ticks_per_call;
    }
    uint32_t elapsed = get_tick() - start;
    printf("\n=== SysTick Pattern ===\n");
    printf("Waited %u ticks (requested %u)\n", elapsed, ticks_to_wait);
}

// ─── ISR Design Checklist ─────────────────────────────────────────────────────

void print_isr_rules(void) {
    printf("\n=== ISR Design Rules ===\n");
    printf("1. Clear the hardware interrupt flag before returning\n");
    printf("2. All shared variables MUST be volatile\n");
    printf("3. Keep ISR short — set a flag, copy one register, then return\n");
    printf("4. No blocking calls: no sleep(), no mutex wait, no printf\n");
    printf("5. No FreeRTOS API calls unless they end in FromISR\n");
    printf("6. Protect multi-byte shared state with a critical section in main\n");
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    main_loop_sim();
    delay_ticks_sim(10, 1);
    print_isr_rules();
    return 0;
}
