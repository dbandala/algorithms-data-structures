// Assertions for embedded systems — runtime and compile-time
// Covers: custom assert_failed handler, _Static_assert, ASSERT macro, graceful error handling
// Time complexity: O(1)
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out assertions_embedded.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

// ─── Why Custom Assertions in Embedded ───────────────────────────────────────
//
// Standard assert() calls abort() → may not be suitable (no OS, no clean shutdown).
// In embedded:
//   - assert_failed() should log the error, optionally blink an error LED,
//     and either reset the MCU (via watchdog or NVIC_SystemReset) or spin forever
//     so a debugger can catch it.
//   - In production: log + reset. In debug: spin at the error location.
//   - Build debug builds with ASSERT enabled; release may disable them to save space.

// ─── assert_failed Handler ────────────────────────────────────────────────────

// In a real MCU implementation:
//   - Write file/line to a backup RAM region for post-reset diagnosis
//   - Trigger watchdog reset (let it expire without kicking)
//   - OR call NVIC_SystemReset() for immediate reset
//   - In debug builds: loop forever so GDB can halt and read the backtrace

static void assert_failed(const char *file, int line, const char *expr) {
    fprintf(stderr, "\n*** ASSERTION FAILED ***\n");
    fprintf(stderr, "  File:  %s\n", file);
    fprintf(stderr, "  Line:  %d\n", line);
    fprintf(stderr, "  Expr:  %s\n", expr);
    fprintf(stderr, "  Action: (production) log + reset | (debug) spin forever\n\n");
    // Simulation: call abort() — in real MCU: NVIC_SystemReset() or WDT
    abort();
}

// ─── ASSERT Macro ─────────────────────────────────────────────────────────────
//
// The do-while(0) wrapper ensures the macro behaves like a single statement,
// safe to use inside if/else without braces.

#ifdef NDEBUG
  #define ASSERT(expr)  ((void)0)      // stripped out in release builds
#else
  #define ASSERT(expr) \
      do { \
          if (!(expr)) assert_failed(__FILE__, __LINE__, #expr); \
      } while (0)
#endif

// ─── Compile-Time Assertions ─────────────────────────────────────────────────
//
// _Static_assert checks at compile time — zero runtime cost.
// Use for: struct sizes, enum counts, buffer size checks.

typedef struct {
    uint8_t  type;
    uint8_t  flags;
    uint16_t length;
    uint32_t crc;
} ProtocolHeader;

_Static_assert(sizeof(ProtocolHeader) == 8,
               "ProtocolHeader must be 8 bytes — check padding");

// Ensure a lookup table has exactly the right number of entries
#define NUM_ERROR_CODES  5
static const char * const ERROR_NAMES[NUM_ERROR_CODES] = {
    "OK", "TIMEOUT", "CHECKSUM", "OVERFLOW", "NOT_FOUND"
};
_Static_assert(sizeof(ERROR_NAMES) / sizeof(ERROR_NAMES[0]) == NUM_ERROR_CODES,
               "ERROR_NAMES size mismatch — add/remove entries to match NUM_ERROR_CODES");

// ─── Safe Input Validation ────────────────────────────────────────────────────
//
// At system boundaries (external data, user input, hardware reads):
// validate instead of ASSERT — ASSERT is for programmer-invariant violations.

typedef enum {
    SENSOR_OK        = 0,
    SENSOR_RANGE_ERR = 1,
    SENSOR_NULL_ERR  = 2,
} SensorStatus;

// Returns SENSOR_OK if valid, else error code (no assert — input may be invalid)
SensorStatus validate_temperature(float temp_c) {
    if (temp_c < -55.0f || temp_c > 150.0f) return SENSOR_RANGE_ERR;
    return SENSOR_OK;
}

// Caller is responsible for non-null buf (programmer invariant → ASSERT)
void copy_to_buffer(uint8_t *buf, size_t buf_len,
                    const uint8_t *src, size_t src_len) {
    ASSERT(buf != NULL);         // programmer must not call with NULL
    ASSERT(src != NULL);
    ASSERT(buf_len >= src_len);  // programmer must ensure buffer is large enough
    memcpy(buf, src, src_len);
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== Assertions for Embedded Systems ===\n\n");

    // Compile-time assertions passed (no compiler error at this point)
    printf("_Static_assert checks passed at compile time\n");
    printf("sizeof(ProtocolHeader) = %zu (expect 8)\n\n", sizeof(ProtocolHeader));

    // Runtime assertion — passes
    int x = 5;
    ASSERT(x > 0);
    printf("ASSERT(x > 0) — passed\n");

    // Input validation (NOT an assert)
    SensorStatus s = validate_temperature(25.0f);
    printf("validate_temperature(25.0) = %d (expect 0=OK)\n", s);
    s = validate_temperature(200.0f);
    printf("validate_temperature(200.0) = %d (expect 1=RANGE_ERR)\n", s);

    // copy_to_buffer — normal usage
    uint8_t src[4] = {1, 2, 3, 4};
    uint8_t dst[8];
    copy_to_buffer(dst, 8, src, 4);
    printf("copy_to_buffer: dst[0]=%u dst[3]=%u (expect 1 4)\n\n", dst[0], dst[3]);

    printf("Error names:\n");
    for (int i = 0; i < NUM_ERROR_CODES; i++) {
        printf("  [%d] %s\n", i, ERROR_NAMES[i]);
    }

    printf("\n=== Triggering a failing ASSERT (will call assert_failed) ===\n");
    printf("Calling ASSERT(0 == 1)...\n");
    ASSERT(0 == 1);   // This will trigger — abort() follows

    // This line is never reached
    printf("Should not reach here\n");
    return 0;
}
