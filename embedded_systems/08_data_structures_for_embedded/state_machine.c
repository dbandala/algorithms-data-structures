// Finite State Machine with function-pointer dispatch table
// Example: Traffic light controller (green→yellow→red→green)
// Time complexity: O(1) per event
// Space complexity: O(states × events) for dispatch table
//
// Compile: gcc -Wall -Wextra -std=c11 -o out state_machine.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// ─── FSM Design Pattern: Function-Pointer Table ───────────────────────────────
//
// For small FSMs (≤ 3 states): a switch statement is fine.
// For larger FSMs: a 2D table maps (state, event) → (action, next_state).
// Benefits: adding a new state = one new row; no deep nested switch.

// ─── States and Events ────────────────────────────────────────────────────────

typedef enum {
    STATE_GREEN  = 0,
    STATE_YELLOW = 1,
    STATE_RED    = 2,
    NUM_STATES
} TrafficState;

typedef enum {
    EVENT_TIMER   = 0,   // periodic timer tick
    EVENT_BUTTON  = 1,   // pedestrian push button
    NUM_EVENTS
} TrafficEvent;

// ─── State Entry/Exit/Action Functions ───────────────────────────────────────

static void on_green_entry(void)  { printf("  [GREEN ] Light ON  — vehicles go\n"); }
static void on_yellow_entry(void) { printf("  [YELLOW] Light ON  — prepare to stop\n"); }
static void on_red_entry(void)    { printf("  [RED   ] Light ON  — vehicles stop\n"); }

// Actions triggered ON a transition (not just entry)
static void action_none(void)        { /* no action */ }
static void action_pedestrian(void)  { printf("  [ACTION] Pedestrian crossing enabled\n"); }

// ─── Transition Table ─────────────────────────────────────────────────────────

typedef void (*ActionFn)(void);
typedef void (*EntryFn)(void);

typedef struct {
    TrafficState next_state;
    ActionFn     action;      // called on this transition
} Transition;

// table[current_state][event] → {next_state, action}
static const Transition TABLE[NUM_STATES][NUM_EVENTS] = {
    //              EVENT_TIMER                              EVENT_BUTTON
    [STATE_GREEN]  = { {STATE_YELLOW, action_none},         {STATE_RED,    action_pedestrian} },
    [STATE_YELLOW] = { {STATE_RED,    action_none},         {STATE_YELLOW, action_none}       },
    [STATE_RED]    = { {STATE_GREEN,  action_none},         {STATE_RED,    action_none}        },
};

static const EntryFn ENTRY_FN[NUM_STATES] = {
    [STATE_GREEN]  = on_green_entry,
    [STATE_YELLOW] = on_yellow_entry,
    [STATE_RED]    = on_red_entry,
};

static const char * const STATE_NAME[NUM_STATES] = { "GREEN", "YELLOW", "RED" };

// ─── FSM Core ─────────────────────────────────────────────────────────────────

typedef struct {
    TrafficState current;
} TrafficFSM;

void fsm_init(TrafficFSM *fsm) {
    fsm->current = STATE_GREEN;
    ENTRY_FN[STATE_GREEN]();
}

void fsm_dispatch(TrafficFSM *fsm, TrafficEvent event) {
    const Transition *t = &TABLE[fsm->current][event];
    printf("  Transition: %s --[%s]--> %s\n",
           STATE_NAME[fsm->current],
           event == EVENT_TIMER ? "TIMER" : "BUTTON",
           STATE_NAME[t->next_state]);

    t->action();                           // run transition action

    if (t->next_state != fsm->current) {
        fsm->current = t->next_state;
        ENTRY_FN[fsm->current]();          // run entry action of new state
    }
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== Traffic Light FSM ===\n\n");
    TrafficFSM light;
    fsm_init(&light);

    printf("\n--- Normal timer cycle (GREEN→YELLOW→RED→GREEN) ---\n");
    fsm_dispatch(&light, EVENT_TIMER);   // GREEN → YELLOW
    fsm_dispatch(&light, EVENT_TIMER);   // YELLOW → RED
    fsm_dispatch(&light, EVENT_TIMER);   // RED → GREEN

    printf("\n--- Pedestrian button press from GREEN ---\n");
    fsm_dispatch(&light, EVENT_BUTTON);  // GREEN → RED (skip yellow)

    printf("\n--- Button press while YELLOW (ignored — stay YELLOW) ---\n");
    fsm_dispatch(&light, EVENT_TIMER);   // RED → GREEN
    fsm_dispatch(&light, EVENT_TIMER);   // GREEN → YELLOW
    fsm_dispatch(&light, EVENT_BUTTON);  // YELLOW: button has no effect

    printf("\n=== FSM Design Notes ===\n");
    printf("Function-pointer table scales cleanly to any number of states/events.\n");
    printf("Adding a new state: add a row to the table + entry/exit functions.\n");
    printf("Adding a new event: add a column to the table.\n");
    printf("No deeply nested switch statements required.\n");

    return 0;
}
