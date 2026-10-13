// RTOS Producer-Consumer — Mini Project
// Demonstrates: bounded queue, two tasks, semaphore for signaling, back-pressure
// Uses POSIX threads (host-runnable); FreeRTOS API equivalents in comments
// Time complexity: O(1) per enqueue/dequeue
// Space complexity: O(QUEUE_DEPTH) items
//
// Compile: gcc -Wall -Wextra -std=c11 -pthread -o producer_consumer producer_consumer.c && ./producer_consumer

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>

// ─── Message Type ──────────────────────────────────────────────────────────────

typedef struct {
    uint32_t sequence;       // sequence number for ordering validation
    int32_t  adc_raw;        // simulated ADC reading
    uint32_t timestamp_ms;   // capture timestamp
} SensorSample;

// ─── Bounded Message Queue ────────────────────────────────────────────────────
//
// FreeRTOS equivalent:
//   QueueHandle_t g_queue = xQueueCreate(QUEUE_DEPTH, sizeof(SensorSample));

#define QUEUE_DEPTH  8

typedef struct {
    SensorSample    items[QUEUE_DEPTH];
    uint32_t        head;
    uint32_t        tail;
    uint32_t        count;
    pthread_mutex_t lock;
    sem_t           sem_items;   // signals consumer: how many items available
    sem_t           sem_space;   // signals producer: how many spaces available
} Queue_t;

static Queue_t g_queue;

static void queue_init(Queue_t *q) {
    q->head = q->tail = q->count = 0;
    pthread_mutex_init(&q->lock, NULL);
    sem_init(&q->sem_items, 0, 0);           // initially 0 items
    sem_init(&q->sem_space, 0, QUEUE_DEPTH); // initially all space free
}

static void queue_destroy(Queue_t *q) {
    pthread_mutex_destroy(&q->lock);
    sem_destroy(&q->sem_items);
    sem_destroy(&q->sem_space);
}

// Blocking send — waits for space if queue full (back-pressure)
// FreeRTOS: xQueueSend(g_queue, &sample, portMAX_DELAY);
static void queue_send(Queue_t *q, const SensorSample *item) {
    sem_wait(&q->sem_space);                      // wait for space
    pthread_mutex_lock(&q->lock);
    q->items[q->head % QUEUE_DEPTH] = *item;
    q->head++;
    q->count++;
    pthread_mutex_unlock(&q->lock);
    sem_post(&q->sem_items);                      // notify consumer
}

// Blocking receive — waits until item available
// FreeRTOS: SensorSample rx; xQueueReceive(g_queue, &rx, portMAX_DELAY);
static void queue_receive(Queue_t *q, SensorSample *out) {
    sem_wait(&q->sem_items);                      // wait for item
    pthread_mutex_lock(&q->lock);
    *out = q->items[q->tail % QUEUE_DEPTH];
    q->tail++;
    q->count--;
    pthread_mutex_unlock(&q->lock);
    sem_post(&q->sem_space);                      // notify producer
}

// ─── Shared Statistics ─────────────────────────────────────────────────────────

static pthread_mutex_t g_stats_lock = PTHREAD_MUTEX_INITIALIZER;
static uint32_t g_produced = 0;
static uint32_t g_consumed = 0;

// ─── Producer Task ────────────────────────────────────────────────────────────
//
// FreeRTOS task signature:
//   void producer_task(void *pvParameters) {
//     for (;;) {
//       SensorSample s = adc_read();
//       xQueueSend(g_queue, &s, portMAX_DELAY);
//       vTaskDelay(pdMS_TO_TICKS(50));
//     }
//   }

#define NUM_SAMPLES  20

static void *producer_task(void *arg) {
    (void)arg;
    for (uint32_t i = 1; i <= NUM_SAMPLES; i++) {
        // Simulate ADC read (random 12-bit value 0–4095)
        SensorSample s = {
            .sequence     = i,
            .adc_raw      = (int32_t)(rand() % 4096),
            .timestamp_ms = (uint32_t)(i * 50),
        };

        printf("[Producer] Sending sample %u: adc=%d  t=%ums\n",
               s.sequence, s.adc_raw, s.timestamp_ms);

        queue_send(&g_queue, &s);  // blocks if queue is full

        pthread_mutex_lock(&g_stats_lock);
        g_produced++;
        pthread_mutex_unlock(&g_stats_lock);

        usleep(50000);  // 50 ms between samples — vTaskDelay(pdMS_TO_TICKS(50))
    }

    // Sentinel: signal consumer to stop
    SensorSample sentinel = { .sequence = 0xFFFFFFFF, .adc_raw = 0, .timestamp_ms = 0 };
    queue_send(&g_queue, &sentinel);

    printf("[Producer] All %d samples sent\n", NUM_SAMPLES);
    return NULL;
}

// ─── Consumer Task ────────────────────────────────────────────────────────────
//
// FreeRTOS task signature:
//   void consumer_task(void *pvParameters) {
//     SensorSample rx;
//     for (;;) {
//       if (xQueueReceive(g_queue, &rx, portMAX_DELAY) == pdTRUE) {
//         process(&rx);
//       }
//     }
//   }

static float  g_sum     = 0.0f;
static int32_t g_min    = INT32_MAX;
static int32_t g_max    = INT32_MIN;

static void *consumer_task(void *arg) {
    (void)arg;
    SensorSample rx;
    while (1) {
        queue_receive(&g_queue, &rx);

        if (rx.sequence == 0xFFFFFFFF) {
            printf("[Consumer] Sentinel received — stopping\n");
            break;
        }

        // Process: running average, min, max
        g_sum += (float)rx.adc_raw;
        if (rx.adc_raw < g_min) g_min = rx.adc_raw;
        if (rx.adc_raw > g_max) g_max = rx.adc_raw;

        printf("[Consumer] Received sample %u: adc=%d  (running avg=%.1f)\n",
               rx.sequence, rx.adc_raw, g_sum / (float)rx.sequence);

        pthread_mutex_lock(&g_stats_lock);
        g_consumed++;
        pthread_mutex_unlock(&g_stats_lock);

        usleep(120000);  // 120 ms to process — slower than producer (queue absorbs burst)
    }

    return NULL;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    srand(42);  // deterministic for reproducibility
    printf("=== RTOS Producer-Consumer ===\n");
    printf("Producer: 50ms/sample  |  Consumer: 120ms/sample  |  Queue depth: %d\n\n",
           QUEUE_DEPTH);

    queue_init(&g_queue);

    // FreeRTOS equivalent:
    //   xTaskCreate(producer_task, "Producer", 512, NULL, 2, NULL);
    //   xTaskCreate(consumer_task, "Consumer", 512, NULL, 1, NULL);
    //   vTaskStartScheduler();

    pthread_t t_prod, t_cons;
    pthread_create(&t_prod, NULL, producer_task, NULL);
    pthread_create(&t_cons, NULL, consumer_task, NULL);

    pthread_join(t_prod, NULL);
    pthread_join(t_cons, NULL);

    printf("\n=== Results ===\n");
    printf("Produced: %u  Consumed: %u\n", g_produced, g_consumed);
    if (g_consumed > 0) {
        printf("ADC min=%d  max=%d  avg=%.1f\n",
               g_min, g_max, g_sum / (float)g_consumed);
    }

    queue_destroy(&g_queue);
    pthread_mutex_destroy(&g_stats_lock);
    return 0;
}
