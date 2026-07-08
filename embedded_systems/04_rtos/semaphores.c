// RTOS semaphores and mutexes — concepts with POSIX simulation + FreeRTOS API reference
// Covers: binary semaphore, counting semaphore, mutex, priority inheritance concept
// Time complexity: O(1) give/take
// Space complexity: O(1) per primitive
//
// Compile: gcc -Wall -Wextra -std=c11 -pthread -o out semaphores.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

// ─── FreeRTOS API Reference (conceptual — not compiled here) ──────────────────
//
// Binary semaphore (for signaling ISR → task):
//   SemaphoreHandle_t sem = xSemaphoreCreateBinary();
//   xSemaphoreGive(sem);            // from task or xSemaphoreGiveFromISR() from ISR
//   xSemaphoreTake(sem, portMAX_DELAY);   // blocks until given
//
// Counting semaphore (N resources):
//   SemaphoreHandle_t csem = xSemaphoreCreateCounting(MAX_COUNT, INITIAL_COUNT);
//   xSemaphoreGive(csem);
//   xSemaphoreTake(csem, timeout_ticks);
//
// Mutex (mutual exclusion, with priority inheritance):
//   SemaphoreHandle_t mtx = xSemaphoreCreateMutex();
//   xSemaphoreTake(mtx, portMAX_DELAY);
//   // ... critical section ...
//   xSemaphoreGive(mtx);
//
// NOTE: never call xSemaphoreTake on a mutex from an ISR — use binary semaphores
// for ISR ↔ task signaling instead.

// ─── 1. Binary Semaphore: ISR → Task Signaling ───────────────────────────────

static sem_t g_isr_signal;   // binary semaphore simulating ISR notification

// Simulated ISR: "fires" after a short delay, signals the worker task
static void *isr_simulator(void *arg) {
    (void)arg;
    usleep(100000);  // simulate ISR firing after 100 ms
    printf("[ISR]  Data ready — posting semaphore\n");
    sem_post(&g_isr_signal);
    return NULL;
}

// Worker task: waits for ISR signal, then processes data
static void *worker_task(void *arg) {
    (void)arg;
    printf("[TASK] Waiting for ISR signal...\n");
    sem_wait(&g_isr_signal);   // blocks until ISR posts
    printf("[TASK] Signal received — processing data\n");
    return NULL;
}

void binary_semaphore_demo(void) {
    printf("=== Binary Semaphore (ISR → Task) ===\n");
    sem_init(&g_isr_signal, 0, 0);  // start at 0 (taken)

    pthread_t t_isr, t_worker;
    pthread_create(&t_worker, NULL, worker_task, NULL);
    pthread_create(&t_isr,    NULL, isr_simulator, NULL);

    pthread_join(t_isr,    NULL);
    pthread_join(t_worker, NULL);
    sem_destroy(&g_isr_signal);
    printf("\n");
}

// ─── 2. Counting Semaphore: Limited Resource Pool ────────────────────────────

#define NUM_DMA_CHANNELS  3   // only 3 DMA channels available

static sem_t g_dma_sem;

typedef struct {
    int  task_id;
    int  sleep_ms;
} TaskArgs;

static void *dma_user_task(void *arg) {
    TaskArgs *ta = (TaskArgs *)arg;
    printf("[Task %d] Requesting DMA channel\n", ta->task_id);
    sem_wait(&g_dma_sem);    // acquire a DMA channel (blocks if all taken)
    printf("[Task %d] Got DMA channel — working...\n", ta->task_id);
    usleep((useconds_t)(ta->sleep_ms * 1000));
    printf("[Task %d] Done — releasing DMA channel\n", ta->task_id);
    sem_post(&g_dma_sem);    // release the channel
    return NULL;
}

void counting_semaphore_demo(void) {
    printf("=== Counting Semaphore (%d DMA channels, 5 tasks) ===\n", NUM_DMA_CHANNELS);
    sem_init(&g_dma_sem, 0, NUM_DMA_CHANNELS);  // 3 available

    pthread_t threads[5];
    TaskArgs  args[5]   = {{1,80},{2,60},{3,120},{4,50},{5,70}};
    for (int i = 0; i < 5; i++) pthread_create(&threads[i], NULL, dma_user_task, &args[i]);
    for (int i = 0; i < 5; i++) pthread_join(threads[i], NULL);

    sem_destroy(&g_dma_sem);
    printf("\n");
}

// ─── 3. Mutex: Protecting a Shared Resource ──────────────────────────────────

static pthread_mutex_t g_uart_mutex = PTHREAD_MUTEX_INITIALIZER;
static char            g_uart_line[128];

static void uart_send(int task_id, const char *msg) {
    pthread_mutex_lock(&g_uart_mutex);
    // --- critical section: only one task sends at a time ---
    snprintf(g_uart_line, sizeof(g_uart_line), "[Task %d] %s", task_id, msg);
    printf("UART TX: %s\n", g_uart_line);
    usleep(10000);  // simulate UART transmission time
    // ---
    pthread_mutex_unlock(&g_uart_mutex);
}

static void *uart_sender(void *arg) {
    int id = *(int *)arg;
    uart_send(id, "Hello from task");
    return NULL;
}

void mutex_demo(void) {
    printf("=== Mutex (shared UART protection) ===\n");
    pthread_t threads[4];
    int ids[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; i++) pthread_create(&threads[i], NULL, uart_sender, &ids[i]);
    for (int i = 0; i < 4; i++) pthread_join(threads[i], NULL);
    pthread_mutex_destroy(&g_uart_mutex);
    printf("\n");
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    binary_semaphore_demo();
    counting_semaphore_demo();
    mutex_demo();

    printf("=== Semaphore vs Mutex Rules ===\n");
    printf("Binary semaphore — signaling: ISR posts, task waits (no owner)\n");
    printf("Counting semaphore — N resources: each take decrements, each give increments\n");
    printf("Mutex — mutual exclusion: SAME task must give that took it; priority inheritance\n");
    printf("Never take a mutex from an ISR — use a binary semaphore instead\n");

    return 0;
}
