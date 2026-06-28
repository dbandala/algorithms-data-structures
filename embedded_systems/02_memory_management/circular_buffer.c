// Circular (ring) buffer — lock-free single-producer / single-consumer implementation
// Used in: UART RX/TX, ADC streaming, audio buffers, inter-task communication
// Time complexity: O(1) push and pop
// Space complexity: O(N) for the buffer
//
// Compile: gcc -Wall -Wextra -std=c11 -o out circular_buffer.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// ─── Design Notes ─────────────────────────────────────────────────────────────
//
// Power-of-2 size: wrap using bitwise AND instead of modulo — faster and no division.
// Lock-free invariant (single producer / single consumer):
//   - Producer writes 'head' only.
//   - Consumer writes 'tail' only.
//   - Both read the other's index.
//   On architectures where size_t reads/writes are atomic (most 32-bit MCUs),
//   this is safe without a mutex for the 1P/1C case.

#define RING_BUF_SIZE  16U    // MUST be a power of 2
#define RING_BUF_MASK  (RING_BUF_SIZE - 1U)

typedef struct {
    uint8_t  buf[RING_BUF_SIZE];
    volatile uint32_t head;   // write index (producer)
    volatile uint32_t tail;   // read  index (consumer)
} RingBuf_t;

// ─── API ──────────────────────────────────────────────────────────────────────

void ring_buf_init(RingBuf_t *rb) {
    rb->head = 0;
    rb->tail = 0;
    memset(rb->buf, 0, sizeof(rb->buf));
}

// Returns number of bytes currently in the buffer
uint32_t ring_buf_count(const RingBuf_t *rb) {
    return (rb->head - rb->tail) & RING_BUF_MASK;
}

// Returns available space
uint32_t ring_buf_free(const RingBuf_t *rb) {
    return (RING_BUF_SIZE - 1U) - ring_buf_count(rb);
    // SIZE-1: leave one slot empty to distinguish full from empty without an extra flag
}

bool ring_buf_empty(const RingBuf_t *rb) {
    return rb->head == rb->tail;
}

bool ring_buf_full(const RingBuf_t *rb) {
    return ring_buf_free(rb) == 0U;
}

// Push one byte — call from producer context (e.g., main or ISR filling a TX queue)
// Returns false if buffer is full
bool ring_buf_push(RingBuf_t *rb, uint8_t byte) {
    if (ring_buf_full(rb)) return false;
    rb->buf[rb->head & RING_BUF_MASK] = byte;
    // Memory barrier would go here on SMP or out-of-order CPUs:
    // __atomic_thread_fence(__ATOMIC_RELEASE);
    rb->head++;    // producer advances head
    return true;
}

// Pop one byte — call from consumer context (e.g., processing task or UART TX ISR)
// Returns false if buffer is empty
bool ring_buf_pop(RingBuf_t *rb, uint8_t *out) {
    if (ring_buf_empty(rb)) return false;
    *out = rb->buf[rb->tail & RING_BUF_MASK];
    // __atomic_thread_fence(__ATOMIC_ACQUIRE);
    rb->tail++;    // consumer advances tail
    return true;
}

// ─── Bulk Push (for DMA-filled buffers) ──────────────────────────────────────

uint32_t ring_buf_push_bytes(RingBuf_t *rb, const uint8_t *data, uint32_t len) {
    uint32_t written = 0;
    for (uint32_t i = 0; i < len; i++) {
        if (!ring_buf_push(rb, data[i])) break;
        written++;
    }
    return written;
}

// ─── Tests ────────────────────────────────────────────────────────────────────

int main(void) {
    RingBuf_t rb;
    ring_buf_init(&rb);

    printf("=== Ring Buffer Tests ===\n\n");

    // Empty state
    printf("empty: %d  full: %d  count: %u  free: %u\n",
           ring_buf_empty(&rb), ring_buf_full(&rb),
           ring_buf_count(&rb), ring_buf_free(&rb));
    // expect: empty=1 full=0 count=0 free=15

    // Push bytes
    const char *msg = "Hello";
    uint32_t n = ring_buf_push_bytes(&rb, (const uint8_t *)msg, 5);
    printf("Pushed %u bytes: '%s'\n", n, msg);
    printf("count: %u (expect 5)  free: %u (expect 10)\n",
           ring_buf_count(&rb), ring_buf_free(&rb));

    // Pop and print
    printf("Popped: ");
    uint8_t byte;
    while (ring_buf_pop(&rb, &byte)) {
        printf("%c", (char)byte);
    }
    printf(" (expect 'Hello')\n");
    printf("empty after drain: %d (expect 1)\n", ring_buf_empty(&rb));

    // Fill to full (capacity = SIZE-1 = 15)
    uint8_t fill[15];
    for (uint8_t i = 0; i < 15; i++) fill[i] = i + 1;
    n = ring_buf_push_bytes(&rb, fill, 15);
    printf("\nFilled %u bytes (expect 15)\n", n);
    printf("full: %d (expect 1)  count: %u (expect 15)\n",
           ring_buf_full(&rb), ring_buf_count(&rb));

    // Push one more — should fail
    bool ok = ring_buf_push(&rb, 0xFF);
    printf("push when full returns: %d (expect 0 = false)\n", ok);

    // Drain and verify order
    printf("Drain: ");
    while (ring_buf_pop(&rb, &byte)) {
        printf("%u ", byte);
    }
    printf("\n(expect 1 2 3 ... 15)\n");

    // Wrap-around test: push 10, pop 5, push 10 more (wraps around)
    ring_buf_init(&rb);
    for (uint8_t i = 0; i < 10; i++) ring_buf_push(&rb, i);
    for (int i = 0; i < 5; i++) ring_buf_pop(&rb, &byte);
    for (uint8_t i = 20; i < 30; i++) ring_buf_push(&rb, i);
    printf("\nWrap-around contents: ");
    while (ring_buf_pop(&rb, &byte)) printf("%u ", byte);
    printf("\n(expect 5 6 7 8 9 20 21 22 23 24 25 26 27 28 29)\n");

    return 0;
}
