// LED Blinker State Machine — Mini Project
// Demonstrates: FSM with function-pointer table, timer-driven transitions,
//               hardware abstraction layer (HAL stub for host)
// Time complexity: O(1) per tick
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o led_blinker led_blinker.c && ./led_blinker

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// ─── Hardware Abstraction Layer (HAL) ────────────────────────────────────────
// On a real MCU, these call GPIO register writes.
// On the host: they print the pin state.

static bool g_led_state = false;

static void hal_led_on(void)  { g_led_state = true;  printf("  LED: [ON ]\n"); }
static void hal_led_off(void) { g_led_state = false; printf("  LED: [OFF]\n"); }
static bool hal_led_get(void) { return g_led_state; }

// ─── FSM Definition ───────────────────────────────────────────────────────────

typedef enum {
    LED_OFF   = 0,
    LED_ON    = 1,
    LED_FAULT = 2,   // fast blink error indication
    NUM_LED_STATES
} LedState;

typedef enum {
    EVT_TIMER  = 0,   // periodic tick (e.g., 500 ms for normal blink)
    EVT_FAULT  = 1,   // fault condition detected
    EVT_CLEAR  = 2,   // fault cleared
    NUM_LED_EVENTS
} LedEvent;

typedef void (*LedAction)(void);
typedef void (*LedEntry)(void);

typedef struct {
    LedState  next;
    LedAction action;
} LedTransition;

// Entry actions for each state
static void entry_off(void)   { hal_led_off(); }
static void entry_on(void)    { hal_led_on();  }
static void entry_fault(void) {
    printf("  FAULT entered — fast-blink mode\n");
    hal_led_on();
}

static void action_nop(void)   { /* no action */ }
static void action_toggle(void) {
    if (hal_led_get()) hal_led_off();
    else               hal_led_on();
}

// Transition table [current_state][event] = {next_state, action}
static const LedTransition TABLE[NUM_LED_STATES][NUM_LED_EVENTS] = {
    //                  EVT_TIMER                    EVT_FAULT                    EVT_CLEAR
    [LED_OFF]   = { {LED_ON,    action_nop},   {LED_FAULT, action_nop},    {LED_OFF,  action_nop} },
    [LED_ON]    = { {LED_OFF,   action_nop},   {LED_FAULT, action_nop},    {LED_ON,   action_nop} },
    [LED_FAULT] = { {LED_FAULT, action_toggle},{LED_FAULT, action_nop},    {LED_OFF,  action_nop} },
};

static const LedEntry ENTRY[NUM_LED_STATES] = {
    [LED_OFF]   = entry_off,
    [LED_ON]    = entry_on,
    [LED_FAULT] = entry_fault,
};

static const char * const STATE_NAME[NUM_LED_STATES] = {"OFF", "ON", "FAULT"};
static const char * const EVENT_NAME[NUM_LED_EVENTS] = {"TIMER", "FAULT", "CLEAR"};

// ─── FSM Core ─────────────────────────────────────────────────────────────────

typedef struct {
    LedState current;
    uint32_t tick_count;
} LedFSM;

void led_fsm_init(LedFSM *fsm) {
    fsm->current    = LED_OFF;
    fsm->tick_count = 0;
    ENTRY[LED_OFF]();
}

void led_fsm_dispatch(LedFSM *fsm, LedEvent event) {
    const LedTransition *t = &TABLE[fsm->current][event];
    printf("  [t=%u] %s --%s--> %s\n",
           fsm->tick_count, STATE_NAME[fsm->current],
           EVENT_NAME[event], STATE_NAME[t->next]);
    t->action();
    if (t->next != fsm->current) {
        fsm->current = t->next;
        ENTRY[fsm->current]();
    }
    fsm->tick_count++;
}

// ─── Simulated Main Loop ──────────────────────────────────────────────────────
// In real firmware: a SysTick ISR sets a flag every 500 ms.
// Main loop checks the flag and dispatches EVT_TIMER.

int main(void) {
    printf("=== LED Blinker State Machine ===\n\n");

    LedFSM fsm;
    led_fsm_init(&fsm);

    printf("\n--- Normal blink cycle (6 timer events) ---\n");
    for (int i = 0; i < 6; i++) {
        led_fsm_dispatch(&fsm, EVT_TIMER);
    }

    printf("\n--- Fault triggered from ON state ---\n");
    led_fsm_dispatch(&fsm, EVT_TIMER);      // → ON
    led_fsm_dispatch(&fsm, EVT_FAULT);      // → FAULT

    printf("\n--- Fast blink in FAULT (3 timer events) ---\n");
    for (int i = 0; i < 3; i++) {
        led_fsm_dispatch(&fsm, EVT_TIMER);
    }

    printf("\n--- Fault cleared ---\n");
    led_fsm_dispatch(&fsm, EVT_CLEAR);      // → OFF

    printf("\n--- Resume normal blink ---\n");
    for (int i = 0; i < 4; i++) {
        led_fsm_dispatch(&fsm, EVT_TIMER);
    }

    printf("\n=== Done ===\n");
    return 0;
}
