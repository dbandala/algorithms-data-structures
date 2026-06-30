// Critical sections — protecting shared state between ISR and main code
// Covers: disable/enable IRQ pattern, nested critical section guard,
//         atomic read of multi-byte values
// Time complexity: O(1)
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out critical_sections.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// ─── Simulated IRQ Enable/Disable ────────────────────────────────────────────
//
// On ARM Cortex-M:
//   __disable_irq()  → CPSID I  (sets PRIMASK = 1, masks all IRQs)
//   __enable_irq()   → CPSIE I  (clears PRIMASK)
//   __get_PRIMASK()  → read current PRIMASK (used for save/restore)
//
// For FreeRTOS use taskENTER_CRITICAL() / taskEXIT_CRITICAL() instead —
// they use BASEPRI to only mask interrupts below the FreeRTOS max priority.

static volatile bool _sim_irq_enabled = true;
static volatile int  _sim_irq_nesting = 0;

static void sim_disable_irq(void) { _sim_irq_enabled = false; _sim_irq_nesting++; }
static void sim_enable_irq(void)  {
    if (_sim_irq_nesting > 0) _sim_irq_nesting--;
    if (_sim_irq_nesting == 0) _sim_irq_enabled = true;
}

// ─── Pattern 1: Simple Critical Section ─────────────────────────────────────
//
// Used for a single atomic read-modify-write of a shared variable.

volatile uint32_t g_event_counter = 0;

// ISR (simulated): increments event counter
void Timer_IRQHandler_sim(void) {
    g_event_counter++;   // single word write — atomic on 32-bit MCU
}

// Main: snapshot the counter atomically (critical section)
uint32_t snapshot_counter(void) {
    sim_disable_irq();
    uint32_t snapshot = g_event_counter;  // atomic 32-bit read
    sim_enable_irq();
    return snapshot;
}

// ─── Pattern 2: Save/Restore IRQ State ───────────────────────────────────────
//
// If the critical section may be called from within another critical section,
// save PRIMASK before disabling and restore it afterward.
// This prevents accidentally re-enabling IRQs when the outer section is still active.
//
// On ARM Cortex-M:
//   uint32_t primask = __get_PRIMASK();
//   __disable_irq();
//   ...
//   if (!primask) __enable_irq();   // only re-enable if IRQs were enabled before

typedef struct { bool irq_was_enabled; } CriticalState_t;

static CriticalState_t critical_section_enter(void) {
    CriticalState_t state = { .irq_was_enabled = _sim_irq_enabled };
    sim_disable_irq();
    return state;
}

static void critical_section_exit(CriticalState_t state) {
    if (state.irq_was_enabled) {
        // Restore — only re-enable if IRQs were on before we entered
        _sim_irq_nesting = 0;
        _sim_irq_enabled = true;
    }
}

// ─── Pattern 3: Multi-byte Atomic Read ───────────────────────────────────────
//
// A 64-bit timestamp updated by ISR — must be read atomically on a 32-bit MCU
// (two separate 32-bit reads could be torn if ISR fires between them).

volatile uint64_t g_timestamp_us = 0;

void Timestamp_ISR_sim(void) {
    g_timestamp_us += 100;  // advance by 100 µs each "tick"
}

uint64_t read_timestamp_atomic(void) {
    CriticalState_t cs = critical_section_enter();
    uint64_t ts = g_timestamp_us;   // two 32-bit reads — safe because IRQs disabled
    critical_section_exit(cs);
    return ts;
}

// ─── Pattern 4: FreeRTOS Critical Section Reference ──────────────────────────
//
// In FreeRTOS, taskENTER_CRITICAL() / taskEXIT_CRITICAL() are nestable and
// use BASEPRI (not PRIMASK) — they mask only interrupts with priority BELOW
// configMAX_SYSCALL_INTERRUPT_PRIORITY, allowing high-priority ISRs to still fire.
//
// Usage:
//   taskENTER_CRITICAL();
//   shared_var = new_value;   // protected by critical section
//   taskEXIT_CRITICAL();
//
// For ISR context (ISRs may not use taskENTER_CRITICAL directly):
//   UBaseType_t saved = taskENTER_CRITICAL_FROM_ISR();
//   // ... brief critical work ...
//   taskEXIT_CRITICAL_FROM_ISR(saved);

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== Critical Section Patterns ===\n\n");

    // Pattern 1: simple snapshot
    Timer_IRQHandler_sim();
    Timer_IRQHandler_sim();
    Timer_IRQHandler_sim();
    uint32_t count = snapshot_counter();
    printf("Pattern 1 — counter snapshot: %u (expect 3)\n", count);
    printf("IRQ enabled after exit: %s (expect true)\n",
           _sim_irq_enabled ? "true" : "false");

    // Pattern 2: nested critical sections
    printf("\nPattern 2 — nested critical sections:\n");
    {
        CriticalState_t outer = critical_section_enter();
        printf("  After outer enter: irq_enabled=%s\n",
               _sim_irq_enabled ? "true" : "false");
        {
            CriticalState_t inner = critical_section_enter();
            printf("  After inner enter: irq_enabled=%s\n",
                   _sim_irq_enabled ? "true" : "false");
            critical_section_exit(inner);
        }
        // IRQ should still be off because outer section is still active
        printf("  After inner exit:  irq_enabled=%s (outer still holds)\n",
               _sim_irq_enabled ? "true" : "false");
        critical_section_exit(outer);
    }
    printf("  After outer exit:  irq_enabled=%s (expect true)\n",
           _sim_irq_enabled ? "true" : "false");

    // Pattern 3: atomic 64-bit read
    printf("\nPattern 3 — 64-bit atomic read:\n");
    Timestamp_ISR_sim();
    Timestamp_ISR_sim();
    Timestamp_ISR_sim();
    uint64_t ts = read_timestamp_atomic();
    printf("  timestamp: %llu µs (expect 300)\n", (unsigned long long)ts);

    printf("\n=== Key Rules ===\n");
    printf("1. Keep critical sections as SHORT as possible\n");
    printf("2. Never wait/block inside a critical section\n");
    printf("3. Save IRQ state on entry — restore on exit (avoid double-enable bugs)\n");
    printf("4. On FreeRTOS: use taskENTER/EXIT_CRITICAL — not __disable_irq directly\n");

    return 0;
}
