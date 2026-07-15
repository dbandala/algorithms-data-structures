// Watchdog timer — init, kick, window watchdog concept
// Simulates IWDG (independent) and WWDG (window) watchdog patterns
// Time complexity: O(1)
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out watchdog_timer.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

// ─── Watchdog Concepts ────────────────────────────────────────────────────────
//
// Independent Watchdog (IWDG):
//   - Runs on its own low-speed oscillator (LSI ~32 kHz on STM32)
//   - Not affected by the main clock stopping
//   - Must be refreshed BEFORE it expires → detects hangs
//   - Once started, cannot be stopped by software in most MCUs
//
// Window Watchdog (WWDG):
//   - Must be refreshed WITHIN a time window: not too early, not too late
//   - Too early (refresh before window opens) → reset
//   - Too late (refresh after window closes) → reset
//   - Detects both hangs (too late) AND runaway code (too early)

// ─── Simulated Watchdog State ─────────────────────────────────────────────────

typedef struct {
    uint32_t timeout_ms;     // period before reset if not kicked
    uint32_t counter_ms;     // counts down to 0
    bool     triggered;      // true if watchdog fired
} IWDG_Sim;

typedef struct {
    uint32_t timeout_ms;     // period before reset (close = 0)
    uint32_t window_ms;      // kicks accepted only AFTER (timeout - window) has passed
    uint32_t counter_ms;
    bool     triggered;
    bool     too_early;
} WWDG_Sim;

void iwdg_init(IWDG_Sim *wdt, uint32_t timeout_ms) {
    wdt->timeout_ms = timeout_ms;
    wdt->counter_ms = timeout_ms;
    wdt->triggered  = false;
}

// Call iwdg_tick periodically (simulates the LSI timer advancing the watchdog)
void iwdg_tick(IWDG_Sim *wdt, uint32_t elapsed_ms) {
    if (wdt->triggered) return;
    if (elapsed_ms >= wdt->counter_ms) {
        wdt->counter_ms = 0;
        wdt->triggered  = true;
    } else {
        wdt->counter_ms -= elapsed_ms;
    }
}

void iwdg_kick(IWDG_Sim *wdt) {
    wdt->counter_ms = wdt->timeout_ms;  // reload
}

void wwdg_init(WWDG_Sim *wdt, uint32_t timeout_ms, uint32_t window_ms) {
    wdt->timeout_ms = timeout_ms;
    wdt->window_ms  = window_ms;
    wdt->counter_ms = timeout_ms;
    wdt->triggered  = false;
    wdt->too_early  = false;
}

void wwdg_tick(WWDG_Sim *wdt, uint32_t elapsed_ms) {
    if (wdt->triggered) return;
    if (elapsed_ms >= wdt->counter_ms) {
        wdt->counter_ms = 0;
        wdt->triggered  = true;  // too late
    } else {
        wdt->counter_ms -= elapsed_ms;
    }
}

void wwdg_kick(WWDG_Sim *wdt) {
    // Kick is valid only inside the window: when counter_ms <= window_ms
    if (wdt->counter_ms > wdt->window_ms) {
        // Kick BEFORE the window opened → reset
        wdt->too_early = true;
        wdt->triggered = true;
    } else {
        wdt->counter_ms = wdt->timeout_ms;  // reload
    }
}

// ─── Test Scenarios ───────────────────────────────────────────────────────────

void test_iwdg_normal(void) {
    printf("=== IWDG: Normal Operation (kick before timeout) ===\n");
    IWDG_Sim wdt;
    iwdg_init(&wdt, 100);   // 100 ms timeout

    // Kick every 80 ms — should never trigger
    for (int i = 0; i < 5; i++) {
        iwdg_tick(&wdt, 80);
        if (!wdt.triggered) {
            printf("  t=%dms: kicked  counter=%ums\n", (i + 1) * 80, wdt.counter_ms);
            iwdg_kick(&wdt);
        }
    }
    printf("  Watchdog triggered: %s (expect NO)\n\n", wdt.triggered ? "YES" : "NO");
}

void test_iwdg_hang(void) {
    printf("=== IWDG: Hang Simulation (forgot to kick) ===\n");
    IWDG_Sim wdt;
    iwdg_init(&wdt, 100);

    // Simulate a hang — never kick
    iwdg_tick(&wdt, 110);   // 110 ms > 100 ms timeout → fires
    printf("  After 110ms without kick: triggered=%s (expect YES)\n",
           wdt.triggered ? "YES" : "NO");
    printf("  MCU would have reset!\n\n");
}

void test_wwdg_normal(void) {
    printf("=== WWDG: Normal Operation (kick within window) ===\n");
    WWDG_Sim wdt;
    wwdg_init(&wdt, 100, 50);  // 100 ms timeout, 50 ms window (open at 50 ms)

    // Advance to 60 ms (window is open: counter=40ms < window=50ms)
    wwdg_tick(&wdt, 60);
    printf("  t=60ms: counter=%ums  window_opens_below=%ums  in_window=%s\n",
           wdt.counter_ms, wdt.window_ms,
           wdt.counter_ms <= wdt.window_ms ? "YES" : "NO");
    wwdg_kick(&wdt);
    printf("  kick: triggered=%s (expect NO)\n\n", wdt.triggered ? "YES" : "NO");
}

void test_wwdg_too_early(void) {
    printf("=== WWDG: Too-Early Kick (runaway code) ===\n");
    WWDG_Sim wdt;
    wwdg_init(&wdt, 100, 50);

    // Kick at 20 ms — window not yet open (counter=80 > window=50)
    wwdg_tick(&wdt, 20);
    printf("  t=20ms: counter=%ums — window not yet open\n", wdt.counter_ms);
    wwdg_kick(&wdt);   // too early!
    printf("  kick too early: triggered=%s  too_early=%s (expect YES/YES)\n\n",
           wdt.triggered ? "YES" : "NO",
           wdt.too_early ? "YES" : "NO");
}

// ─── Best Practices ───────────────────────────────────────────────────────────

void print_wdt_rules(void) {
    printf("=== Watchdog Best Practices ===\n");
    printf("1. Kick from a SINGLE point in the main loop\n");
    printf("2. Never kick from an ISR or a worker function\n");
    printf("3. Verify the main loop ran at least once before kicking\n");
    printf("4. Set timeout appropriate to your worst-case loop time\n");
    printf("5. In safety-critical code: use WWDG to detect runaway fast loops too\n");
    printf("6. Log a watchdog-reset event at startup (check reset cause register)\n");
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    test_iwdg_normal();
    test_iwdg_hang();
    test_wwdg_normal();
    test_wwdg_too_early();
    print_wdt_rules();
    return 0;
}
