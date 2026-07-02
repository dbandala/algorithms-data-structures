// RTOS message queues — producer/consumer pattern
// Covers: queue basics, blocking send/receive, timeout, ISR→task via queue
// Uses POSIX for host-runnable simulation + FreeRTOS API reference
// Time complexity: O(1) enqueue/dequeue
// Space complexity: O(N) for queue depth N
//
// Compile: gcc -Wall -Wextra -std=c11 -pthread -o out message_queues.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

// ─── FreeRTOS API Reference ───────────────────────────────────────────────────
//
// Create a queue of 10 items, each sizeof(SensorMsg):
//   QueueHandle_t q = xQueueCreate(10, sizeof(SensorMsg));
//
// Producer (task context):
//   SensorMsg msg = { .id = 1, .value = 42 };
//   xQueueSend(q, &msg, portMAX_DELAY);   // blocks if queue full
//   xQueueSendToFront(q, &msg, 0);        // no wait
//
// Producer (ISR context):
//   BaseType_t higher_prio_woken = pdFALSE;
//   xQueueSendFromISR(q, &msg, &higher_prio_woken);
//   portYIELD_FROM_ISR(higher_prio_woken);
//
// Consumer:
//   SensorMsg rx;
//   if (xQueueReceive(q, &rx, pdMS_TO_TICKS(100)) == pdTRUE) { ... }
//
// Peek (without removing):
//   xQueuePeek(q, &rx, 0);
//
// Items in queue:
//   uxQueueMessagesWaiting(q);

// ─── Simple Fixed-Size Queue (Host-Runnable Simulation) ───────────────────────

#define Q_DEPTH  8

typedef struct {
    uint8_t  sensor_id;
    int32_t  value;
    uint32_t timestamp_ms;
} SensorMsg;

typedef struct {
    SensorMsg       items[Q_DEPTH];
    uint32_t        head;         // next write position
    uint32_t        tail;         // next read position
    uint32_t        count;
    pthread_mutex_t lock;
    sem_t           items_avail;  // signals consumer: items waiting
    sem_t           space_avail;  // signals producer: space available
} MsgQueue_t;

void queue_init(MsgQueue_t *q) {
    q->head  = 0;
    q->tail  = 0;
    q->count = 0;
    pthread_mutex_init(&q->lock, NULL);
    sem_init(&q->items_avail, 0, 0);        // 0 items initially
    sem_init(&q->space_avail, 0, Q_DEPTH);  // all slots free
}

void queue_destroy(MsgQueue_t *q) {
    pthread_mutex_destroy(&q->lock);
    sem_destroy(&q->items_avail);
    sem_destroy(&q->space_avail);
}

// Blocking send — waits if queue is full
void queue_send(MsgQueue_t *q, const SensorMsg *msg) {
    sem_wait(&q->space_avail);       // wait for free slot
    pthread_mutex_lock(&q->lock);
    q->items[q->head % Q_DEPTH] = *msg;
    q->head++;
    q->count++;
    pthread_mutex_unlock(&q->lock);
    sem_post(&q->items_avail);       // notify consumer
}

// Blocking receive — waits if queue is empty
void queue_receive(MsgQueue_t *q, SensorMsg *out) {
    sem_wait(&q->items_avail);       // wait for an item
    pthread_mutex_lock(&q->lock);
    *out = q->items[q->tail % Q_DEPTH];
    q->tail++;
    q->count--;
    pthread_mutex_unlock(&q->lock);
    sem_post(&q->space_avail);       // notify producer
}

// ─── Producer Task (simulates a sensor ISR / data acquisition task) ───────────

static MsgQueue_t g_sensor_queue;

static void *producer_task(void *arg) {
    (void)arg;
    for (uint8_t i = 1; i <= 6; i++) {
        SensorMsg msg = {
            .sensor_id    = i,
            .value        = (int32_t)(i * 100),
            .timestamp_ms = (uint32_t)(i * 50)
        };
        printf("[Producer] Sending: id=%u  val=%d  t=%ums\n",
               msg.sensor_id, msg.value, msg.timestamp_ms);
        queue_send(&g_sensor_queue, &msg);
        usleep(30000);   // simulate 30 ms between samples
    }
    // Sentinel message to signal consumer to stop
    SensorMsg sentinel = { .sensor_id = 0xFF, .value = 0, .timestamp_ms = 0 };
    queue_send(&g_sensor_queue, &sentinel);
    return NULL;
}

// ─── Consumer Task (simulates a data processing / logging task) ──────────────

static void *consumer_task(void *arg) {
    (void)arg;
    SensorMsg msg;
    while (1) {
        queue_receive(&g_sensor_queue, &msg);
        if (msg.sensor_id == 0xFF) {
            printf("[Consumer] Received sentinel — stopping\n");
            break;
        }
        printf("[Consumer] Received: id=%u  val=%d  t=%ums\n",
               msg.sensor_id, msg.value, msg.timestamp_ms);
        usleep(80000);   // simulate slower processing (80 ms) — queue absorbs burst
    }
    return NULL;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== Message Queue: Producer-Consumer ===\n");
    printf("Queue depth: %d  |  Producer: 30ms/msg  |  Consumer: 80ms/msg\n\n",
           Q_DEPTH);

    queue_init(&g_sensor_queue);

    pthread_t t_prod, t_cons;
    pthread_create(&t_prod, NULL, producer_task, NULL);
    pthread_create(&t_cons, NULL, consumer_task, NULL);

    pthread_join(t_prod, NULL);
    pthread_join(t_cons, NULL);

    queue_destroy(&g_sensor_queue);

    printf("\n=== Queue vs Shared Variable ===\n");
    printf("Queue:            buffers multiple values; transfers ownership; ISR-safe\n");
    printf("Shared variable:  only latest value; no buffering; needs critical section\n");
    printf("Use queue when:   producer faster than consumer, or multiple messages matter\n");
    printf("Use shared var:   only latest value needed (e.g., ADC reading)\n");

    return 0;
}
