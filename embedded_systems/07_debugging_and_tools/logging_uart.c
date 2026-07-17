// Lightweight ring-buffer UART logger with log levels
// Non-blocking: log writes to a ring buffer; UART TX drains it (simulated here)
// Time complexity: O(N) per log message (N = message length)
// Space complexity: O(LOG_BUF_SIZE) static
//
// Compile: gcc -Wall -Wextra -std=c11 -o out logging_uart.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdbool.h>
#include <string.h>

// ─── Log Levels ───────────────────────────────────────────────────────────────

typedef enum {
    LOG_DEBUG = 0,
    LOG_INFO  = 1,
    LOG_WARN  = 2,
    LOG_ERROR = 3,
    LOG_NONE  = 4,   // disable all logging
} LogLevel;

static const char * const LOG_LEVEL_STR[] = { "DBG", "INF", "WRN", "ERR" };

// ─── Ring Buffer for Log Output ───────────────────────────────────────────────

#define LOG_BUF_SIZE  256U   // must be power of 2
#define LOG_BUF_MASK  (LOG_BUF_SIZE - 1U)

static char     g_log_buf[LOG_BUF_SIZE];
static uint32_t g_log_head = 0;    // write index (logger writes here)
static uint32_t g_log_tail = 0;    // read index  (UART TX ISR reads here)

static bool log_buf_full(void)  { return ((g_log_head - g_log_tail) & LOG_BUF_MASK) == LOG_BUF_MASK; }
static bool log_buf_empty(void) { return g_log_head == g_log_tail; }

static void log_buf_push(char c) {
    if (log_buf_full()) return;  // drop character if buffer full — never block in embedded
    g_log_buf[g_log_head & LOG_BUF_MASK] = c;
    g_log_head++;
}

static bool log_buf_pop(char *c) {
    if (log_buf_empty()) return false;
    *c = g_log_buf[g_log_tail & LOG_BUF_MASK];
    g_log_tail++;
    return true;
}

// ─── Log Configuration ────────────────────────────────────────────────────────

static LogLevel g_min_level = LOG_DEBUG;   // filter: suppress below this level

void log_set_level(LogLevel level) {
    g_min_level = level;
}

// ─── Simulated Tick Counter ───────────────────────────────────────────────────

static uint32_t g_tick_ms = 0;

void log_set_tick(uint32_t ms) { g_tick_ms = ms; }

// ─── Log Write Function ───────────────────────────────────────────────────────

void log_write(LogLevel level, const char *tag, const char *fmt, ...) {
    if (level < g_min_level) return;

    // Build: "[  123 INF TAG] message\n"
    char line[128];
    int  hdr_len = snprintf(line, sizeof(line), "[%5u %s %-6s] ",
                            g_tick_ms,
                            LOG_LEVEL_STR[level],
                            tag);
    if (hdr_len < 0) return;

    va_list args;
    va_start(args, fmt);
    int msg_len = vsnprintf(line + hdr_len,
                            sizeof(line) - (size_t)hdr_len,
                            fmt, args);
    va_end(args);
    if (msg_len < 0) return;

    // Append newline
    size_t total = (size_t)(hdr_len + msg_len);
    if (total < sizeof(line) - 1) {
        line[total]     = '\n';
        line[total + 1] = '\0';
        total++;
    }

    // Push to ring buffer (non-blocking)
    for (size_t i = 0; i < total; i++) {
        log_buf_push(line[i]);
    }
}

// Convenience macros (common pattern in embedded logging libraries)
#define LOG_D(tag, fmt, ...)  log_write(LOG_DEBUG, tag, fmt, ##__VA_ARGS__)
#define LOG_I(tag, fmt, ...)  log_write(LOG_INFO,  tag, fmt, ##__VA_ARGS__)
#define LOG_W(tag, fmt, ...)  log_write(LOG_WARN,  tag, fmt, ##__VA_ARGS__)
#define LOG_E(tag, fmt, ...)  log_write(LOG_ERROR, tag, fmt, ##__VA_ARGS__)

// ─── Simulated UART TX Drain ─────────────────────────────────────────────────
// In real firmware: called from UART TX empty interrupt to send next byte.

void uart_tx_drain(void) {
    char c;
    while (log_buf_pop(&c)) {
        putchar(c);   // simulate UART TX
    }
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== Embedded UART Logger Demo ===\n\n");

    // All levels
    log_set_tick(0);
    LOG_D("INIT",   "Boot sequence started");
    LOG_I("INIT",   "CPU frequency: %u MHz", 72);
    LOG_I("INIT",   "RTOS heap available: %u bytes", 8192);
    LOG_W("SENSOR", "Temperature sensor read took %u ms (threshold %u ms)", 18, 10);
    LOG_E("CAN",    "Bus-off error detected — reinitializing");
    uart_tx_drain();

    // Advance tick and log with filtering
    log_set_tick(1250);
    log_set_level(LOG_WARN);   // suppress DEBUG and INFO
    printf("--- Filtering: only WARN and ERROR ---\n");
    LOG_D("TASK",   "Task A running (suppressed)");
    LOG_I("TASK",   "Task A completed (suppressed)");
    LOG_W("POWER",  "Battery voltage low: %.2fV", 3.1f);
    LOG_E("FLASH",  "Write failed at address 0x%08X", 0x08020000U);
    uart_tx_drain();

    // Overflow test
    log_set_level(LOG_DEBUG);
    log_set_tick(5000);
    printf("\n--- Buffer overflow: very long message is truncated ---\n");
    LOG_E("TEST", "This is a very long error message that may exceed the log line buffer "
                  "limit of 128 characters and will be silently truncated at the boundary.");
    uart_tx_drain();

    return 0;
}
