// UART Command Parser — Mini Project
// Demonstrates: circular RX buffer (ISR-safe), line parser, command dispatch table
// Time complexity: O(N) for N-char line parse; O(K) dispatch table lookup (K=commands)
// Space complexity: O(RX_BUF_SIZE) + O(K) for command table
//
// Compile: gcc -Wall -Wextra -std=c11 -o uart_parser uart_parser.c && ./uart_parser

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

// ─── Circular RX Buffer (ISR ↔ Main, lock-free 1P/1C) ────────────────────────

#define RX_BUF_SIZE  128U
#define RX_BUF_MASK  (RX_BUF_SIZE - 1U)

static volatile uint8_t  g_rx_buf[RX_BUF_SIZE];
static volatile uint32_t g_rx_head = 0;   // written by UART ISR
static volatile uint32_t g_rx_tail = 0;   // read by main loop

static bool rx_empty(void)  { return g_rx_head == g_rx_tail; }
static bool rx_full(void)   {
    return ((g_rx_head - g_rx_tail) & RX_BUF_MASK) == RX_BUF_MASK;
}

// Called from UART RX ISR
static void rx_push(uint8_t byte) {
    if (rx_full()) return;  // drop on overflow — never block in ISR
    g_rx_buf[g_rx_head & RX_BUF_MASK] = byte;
    g_rx_head++;
}

// Called from main loop
static bool rx_pop(uint8_t *out) {
    if (rx_empty()) return false;
    *out = g_rx_buf[g_rx_tail & RX_BUF_MASK];
    g_rx_tail++;
    return true;
}

// ─── Line Assembler ───────────────────────────────────────────────────────────
// Drain the RX buffer byte-by-byte; accumulate into a line buffer.
// Returns true + populates 'line' when a complete line (\n or \r\n) is ready.

#define MAX_LINE  64

static char  g_line_buf[MAX_LINE];
static int   g_line_pos = 0;

static bool assemble_line(char *line_out, size_t max_len) {
    uint8_t byte;
    while (rx_pop(&byte)) {
        if (byte == '\r') continue;   // ignore CR, wait for LF
        if (byte == '\n') {
            // Complete line
            g_line_buf[g_line_pos] = '\0';
            size_t copy_len = (size_t)g_line_pos < max_len - 1
                              ? (size_t)g_line_pos : max_len - 1;
            strncpy(line_out, g_line_buf, copy_len);
            line_out[copy_len] = '\0';
            g_line_pos = 0;
            return true;
        }
        // Normal character — add to buffer if space available
        if (g_line_pos < MAX_LINE - 1) {
            g_line_buf[g_line_pos++] = (char)byte;
        }
        // else: line too long — silently drop until newline
    }
    return false;
}

// ─── Command Handlers ─────────────────────────────────────────────────────────

static bool g_led_on = false;

static void cmd_led_on(const char *args)   {
    (void)args;
    g_led_on = true;
    printf("  LED turned ON\n");
}

static void cmd_led_off(const char *args)  {
    (void)args;
    g_led_on = false;
    printf("  LED turned OFF\n");
}

static void cmd_status(const char *args)   {
    (void)args;
    printf("  System status: LED=%s  RX buf usage=%u/%u\n",
           g_led_on ? "ON" : "OFF",
           (unsigned)((g_rx_head - g_rx_tail) & RX_BUF_MASK),
           RX_BUF_SIZE - 1U);
}

static void cmd_reset(const char *args) {
    (void)args;
    printf("  Simulating system reset...\n");
    // Real: NVIC_SystemReset() or trigger watchdog
}

static void cmd_help(const char *args);  // forward declaration

// ─── Command Dispatch Table ───────────────────────────────────────────────────

typedef void (*CmdHandler)(const char *args);

typedef struct {
    const char *name;
    CmdHandler  handler;
    const char *description;
} CmdEntry;

static const CmdEntry CMD_TABLE[] = {
    { "LED ON",  cmd_led_on,  "Turn LED on"        },
    { "LED OFF", cmd_led_off, "Turn LED off"       },
    { "STATUS",  cmd_status,  "Show system status" },
    { "RESET",   cmd_reset,   "Reset the MCU"      },
    { "HELP",    cmd_help,    "List all commands"  },
};

#define NUM_CMDS  (sizeof(CMD_TABLE) / sizeof(CMD_TABLE[0]))

static void cmd_help(const char *args) {
    (void)args;
    printf("  Available commands:\n");
    for (size_t i = 0; i < NUM_CMDS; i++) {
        printf("    %-10s — %s\n", CMD_TABLE[i].name, CMD_TABLE[i].description);
    }
}

// ─── Command Dispatcher ───────────────────────────────────────────────────────

static void to_upper(char *s) {
    while (*s) { *s = (char)toupper((unsigned char)*s); s++; }
}

static void dispatch_command(const char *raw_line) {
    // Make a mutable uppercase copy for matching
    char line[MAX_LINE];
    strncpy(line, raw_line, MAX_LINE - 1);
    line[MAX_LINE - 1] = '\0';
    to_upper(line);

    // Strip leading/trailing whitespace
    size_t start = 0;
    while (line[start] == ' ') start++;
    size_t end = strlen(line);
    while (end > start && line[end - 1] == ' ') end--;
    line[end] = '\0';
    const char *trimmed = line + start;

    printf("> %s\n", trimmed);

    for (size_t i = 0; i < NUM_CMDS; i++) {
        size_t len = strlen(CMD_TABLE[i].name);
        if (strncmp(trimmed, CMD_TABLE[i].name, len) == 0 &&
            (trimmed[len] == '\0' || trimmed[len] == ' ')) {
            const char *args = (trimmed[len] == ' ') ? trimmed + len + 1 : "";
            CMD_TABLE[i].handler(args);
            return;
        }
    }
    printf("  ERROR: unknown command '%s'\n", trimmed);
}

// ─── Simulate UART Input ──────────────────────────────────────────────────────

static void simulate_uart_rx(const char *text) {
    while (*text) rx_push((uint8_t)*text++);
    rx_push('\n');   // simulate newline
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== UART Command Parser Demo ===\n\n");

    // Simulate a sequence of UART commands arriving (ISR would push these)
    const char *commands[] = {
        "HELP",
        "LED ON",
        "STATUS",
        "LED OFF",
        "STATUS",
        "unknown_cmd",
        "RESET",
    };
    int n = (int)(sizeof(commands) / sizeof(commands[0]));

    char line[MAX_LINE];

    // Main loop: push command bytes then drain and dispatch
    for (int i = 0; i < n; i++) {
        simulate_uart_rx(commands[i]);  // simulate ISR filling RX buffer

        // Main loop processing
        if (assemble_line(line, MAX_LINE)) {
            dispatch_command(line);
        }
        printf("\n");
    }

    return 0;
}
