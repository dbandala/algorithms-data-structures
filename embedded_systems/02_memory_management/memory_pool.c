// Fixed-size memory pool — O(1) allocation and deallocation, no fragmentation
// Ideal for embedded systems where malloc/free are avoided
// Time complexity: O(1) alloc and free
// Space complexity: O(N * block_size) static allocation
//
// Compile: gcc -Wall -Wextra -std=c11 -o out memory_pool.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

// ─── Design ───────────────────────────────────────────────────────────────────
//
// The pool is a statically allocated array of N fixed-size blocks.
// A free-list (singly linked list stored inside the free blocks) tracks
// available slots. No external metadata needed — the blocks themselves
// hold the next pointer when free.
//
// On alloc: pop from free-list head  → O(1)
// On free:  push back to free-list   → O(1)
// No fragmentation: all blocks are the same size.

#define POOL_BLOCK_SIZE  32U    // bytes per block
#define POOL_NUM_BLOCKS  8U     // total blocks

// Ensure a block is large enough to hold a pointer (free-list link)
_Static_assert(POOL_BLOCK_SIZE >= sizeof(void *),
               "Block size must be >= pointer size");

typedef struct {
    uint8_t  storage[POOL_BLOCK_SIZE * POOL_NUM_BLOCKS]; // raw memory
    void    *free_list;   // head of free-list (lives inside free blocks)
    uint32_t free_count;  // for diagnostics
} MemPool_t;

// ─── API ──────────────────────────────────────────────────────────────────────

void pool_init(MemPool_t *pool) {
    pool->free_list  = NULL;
    pool->free_count = POOL_NUM_BLOCKS;

    // Build the free-list by threading a next-pointer through each block
    for (uint32_t i = 0; i < POOL_NUM_BLOCKS; i++) {
        void *block = (void *)(pool->storage + i * POOL_BLOCK_SIZE);
        // Write the current free_list head into the start of this block
        memcpy(block, &pool->free_list, sizeof(void *));
        pool->free_list = block;
    }
}

// Allocate one block — returns NULL if pool is exhausted
void *pool_alloc(MemPool_t *pool) {
    if (pool->free_list == NULL) return NULL;

    void *block = pool->free_list;
    // Read the next pointer stored at the start of this block
    memcpy(&pool->free_list, block, sizeof(void *));
    pool->free_count--;

    // Zero out the block before handing it to the caller (optional but safe)
    memset(block, 0, POOL_BLOCK_SIZE);
    return block;
}

// Free a block — put it back on the free-list
void pool_free(MemPool_t *pool, void *block) {
    if (block == NULL) return;
    // Write the current free_list head into the block, then update head
    memcpy(block, &pool->free_list, sizeof(void *));
    pool->free_list = block;
    pool->free_count++;
}

uint32_t pool_free_count(const MemPool_t *pool) {
    return pool->free_count;
}

// ─── Example: Sensor Reading Buffers ─────────────────────────────────────────

typedef struct {
    uint16_t sensor_id;
    int32_t  temperature_mdeg;  // millidegrees Celsius
    uint32_t timestamp_ms;
} SensorReading;

_Static_assert(sizeof(SensorReading) <= POOL_BLOCK_SIZE,
               "SensorReading must fit in one pool block");

// ─── Main ─────────────────────────────────────────────────────────────────────

static MemPool_t g_sensor_pool;

int main(void) {
    pool_init(&g_sensor_pool);

    printf("=== Memory Pool Tests ===\n");
    printf("blocks: %u  block_size: %u bytes  pool_size: %zu bytes\n",
           POOL_NUM_BLOCKS, POOL_BLOCK_SIZE,
           sizeof(g_sensor_pool.storage));
    printf("free after init: %u (expect %u)\n\n",
           pool_free_count(&g_sensor_pool), POOL_NUM_BLOCKS);

    // Allocate 3 sensor readings
    SensorReading *r0 = (SensorReading *)pool_alloc(&g_sensor_pool);
    SensorReading *r1 = (SensorReading *)pool_alloc(&g_sensor_pool);
    SensorReading *r2 = (SensorReading *)pool_alloc(&g_sensor_pool);

    printf("After 3 allocs: free=%u (expect %u)\n\n",
           pool_free_count(&g_sensor_pool), POOL_NUM_BLOCKS - 3);

    // Populate
    r0->sensor_id = 1; r0->temperature_mdeg = 25000; r0->timestamp_ms = 100;
    r1->sensor_id = 2; r1->temperature_mdeg = -5300; r1->timestamp_ms = 200;
    r2->sensor_id = 3; r2->temperature_mdeg = 37250; r2->timestamp_ms = 300;

    printf("r0: id=%u  temp=%.3f°C  t=%ums\n",
           r0->sensor_id, r0->temperature_mdeg / 1000.0, r0->timestamp_ms);
    printf("r1: id=%u  temp=%.3f°C  t=%ums\n",
           r1->sensor_id, r1->temperature_mdeg / 1000.0, r1->timestamp_ms);
    printf("r2: id=%u  temp=%.3f°C  t=%ums\n",
           r2->sensor_id, r2->temperature_mdeg / 1000.0, r2->timestamp_ms);

    // Free r1, re-alloc a new block — should get r1's slot back
    pool_free(&g_sensor_pool, r1);
    printf("\nAfter free(r1): free=%u (expect %u)\n",
           pool_free_count(&g_sensor_pool), POOL_NUM_BLOCKS - 2);

    SensorReading *r3 = (SensorReading *)pool_alloc(&g_sensor_pool);
    printf("r3 alloc'd at %p, r1 was at %p  (same? %s)\n",
           (void *)r3, (void *)r1, r3 == r1 ? "YES — reused slot" : "NO");

    // Exhaust the pool
    void *blocks[POOL_NUM_BLOCKS];
    memset(blocks, 0, sizeof(blocks));
    uint32_t allocated = 0;
    void *b;
    while ((b = pool_alloc(&g_sensor_pool)) != NULL) {
        blocks[allocated++] = b;
    }
    printf("\nExhausted pool after %u more allocs\n", allocated);
    printf("free=%u (expect 0)\n", pool_free_count(&g_sensor_pool));

    // NULL on exhaustion
    void *null_ptr = pool_alloc(&g_sensor_pool);
    printf("alloc on empty pool: %s (expect NULL)\n",
           null_ptr == NULL ? "NULL" : "NOT NULL — BUG!");

    // Return all
    pool_free(&g_sensor_pool, r0);
    pool_free(&g_sensor_pool, r3);
    pool_free(&g_sensor_pool, r2);
    for (uint32_t i = 0; i < allocated; i++) pool_free(&g_sensor_pool, blocks[i]);
    printf("\nAfter returning all: free=%u (expect %u)\n",
           pool_free_count(&g_sensor_pool), POOL_NUM_BLOCKS);

    return 0;
}
