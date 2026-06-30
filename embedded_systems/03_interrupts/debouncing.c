// Software button debouncing — timer-based and counter-based implementations
// Covers: why debouncing is needed, timer-based (most common), counter-based
// Time complexity: O(1) per sample
// Space complexity: O(1) per button
//
// Compile: gcc -Wall -Wextra -std=c11 -o out debouncing.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// ─── Why Debouncing Is Needed ─────────────────────────────────────────────────
//
// Mechanical switches bounce between open and closed many times over ~5–50 ms
// when pressed or released. Without debouncing, a single button press generates
// many false events.
//
// Hardware fix: RC low-pass filter + Schmitt trigger input.
// Software fix (below): ignore transitions within a timeout period.

// ─── 1. Timer-Based Debounce ──────────────────────────────────────────────────
//
// On a real MCU: attach a GPIO interrupt to the button pin.
// On first edge: start a timer (e.g., 20 ms).
// Disable the GPIO interrupt while the timer runs.
// On timer expiry: check pin state; if it changed from original, accept the event.
// Re-enable the GPIO interrupt.

#define DEBOUNCE_TIMEOUT_MS  20U   // ignore further transitions for 20 ms

typedef enum {
    BTN_STATE_IDLE,       // waiting for press
    BTN_STATE_DEBOUNCING, // timer running, ignoring bounces
} BtnDebounceState_t;

typedef struct {
    BtnDebounceState_t state;
    uint32_t           timer_start_ms;
    bool               stable_level;     // last accepted level
    bool               pressed_event;    // set when a clean press is detected
    bool               released_event;   // set when a clean release is detected
} Button_t;

void button_init(Button_t *btn, bool initial_level) {
    btn->state          = BTN_STATE_IDLE;
    btn->timer_start_ms = 0;
    btn->stable_level   = initial_level;
    btn->pressed_event  = false;
    btn->released_event = false;
}

// Call this from your GPIO ISR (or poll it every 1 ms)
void button_on_edge(Button_t *btn, uint32_t now_ms) {
    if (btn->state == BTN_STATE_IDLE) {
        // First edge detected — start debounce timer
        btn->timer_start_ms = now_ms;
        btn->state          = BTN_STATE_DEBOUNCING;
    }
    // If already debouncing, ignore this bounce
}

// Call this from main loop (or a timer callback) periodically
void button_update(Button_t *btn, bool current_level, uint32_t now_ms) {
    if (btn->state == BTN_STATE_DEBOUNCING) {
        if ((now_ms - btn->timer_start_ms) >= DEBOUNCE_TIMEOUT_MS) {
            // Timer expired — check if level changed
            if (current_level != btn->stable_level) {
                btn->stable_level = current_level;
                if (!current_level) {  // active-low button: LOW = pressed
                    btn->pressed_event = true;
                } else {
                    btn->released_event = true;
                }
            }
            btn->state = BTN_STATE_IDLE;
        }
    }
}

// ─── 2. Counter-Based Debounce ────────────────────────────────────────────────
//
// Sample the pin every 1 ms. Accept a new state only after N consecutive
// samples in the same state (N = debounce count, e.g., 20 → 20 ms debounce).

#define DEBOUNCE_COUNT  20U    // number of consecutive same-state samples required

typedef struct {
    bool     stable;    // current stable (debounced) state
    uint8_t  count;     // consecutive sample count
    bool     pressed_event;
    bool     released_event;
} BtnCounter_t;

void btn_counter_init(BtnCounter_t *btn, bool initial) {
    btn->stable          = initial;
    btn->count           = DEBOUNCE_COUNT;
    btn->pressed_event   = false;
    btn->released_event  = false;
}

// Call every 1 ms with the raw pin sample
void btn_counter_sample(BtnCounter_t *btn, bool raw) {
    if (raw == btn->stable) {
        if (btn->count < DEBOUNCE_COUNT) btn->count++;
    } else {
        btn->count--;
        if (btn->count == 0) {
            // Stable for DEBOUNCE_COUNT samples in new state → accept
            btn->stable = raw;
            btn->count  = DEBOUNCE_COUNT;
            if (!raw) btn->pressed_event  = true;
            else      btn->released_event = true;
        }
    }
}

// ─── Test Harness ─────────────────────────────────────────────────────────────

int main(void) {
    printf("=== Timer-Based Debounce ===\n\n");

    Button_t btn;
    button_init(&btn, true);  // initially HIGH (released, active-low)

    // Simulate: button pressed at t=0, bounces at 2, 5, 8, 12 ms, stable at 15 ms
    // First edge at t=0
    button_on_edge(&btn, 0);
    printf("t=0ms: first edge — debounce timer started\n");

    // Simulate bounces — should be ignored
    button_on_edge(&btn, 2);   // bounce ignored
    button_on_edge(&btn, 5);   // bounce ignored
    button_on_edge(&btn, 8);   // bounce ignored

    // Update called every ms by main loop; check at t=21 (timeout = 20 ms)
    for (uint32_t t = 1; t <= 30; t++) {
        bool pin_level = (t >= 15) ? false : true;  // button settled LOW at t=15
        button_update(&btn, pin_level, t);
        if (btn.pressed_event) {
            printf("t=%ums: PRESS event accepted (stable level=LOW)\n", t);
            btn.pressed_event = false;
        }
        if (btn.released_event) {
            printf("t=%ums: RELEASE event accepted\n", t);
            btn.released_event = false;
        }
    }

    printf("\n=== Counter-Based Debounce ===\n\n");

    BtnCounter_t cbtn;
    btn_counter_init(&cbtn, true);   // initially HIGH

    // Simulate bouncing pin: 8 samples LOW (bounce), 1 HIGH, then 20 consecutive LOW
    bool sim_samples[] = {
        // First few bounces
        false, true, false, true, false, true, false, true,
        // Settled LOW (20 consecutive)
        false, false, false, false, false, false, false, false,
        false, false, false, false, false, false, false, false,
        false, false, false, false
    };
    int n_samples = (int)(sizeof(sim_samples) / sizeof(sim_samples[0]));

    for (int i = 0; i < n_samples; i++) {
        btn_counter_sample(&cbtn, sim_samples[i]);
        if (cbtn.pressed_event) {
            printf("Sample %d: PRESS event accepted after %d stable samples\n",
                   i + 1, DEBOUNCE_COUNT);
            cbtn.pressed_event = false;
        }
    }

    printf("\n=== Debounce Comparison ===\n");
    printf("Timer-based:   best for GPIO interrupt-driven code; low CPU usage\n");
    printf("Counter-based: best for polled code (e.g., called from 1 ms tick ISR)\n");

    return 0;
}
