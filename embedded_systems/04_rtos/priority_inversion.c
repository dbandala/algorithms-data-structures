// Priority inversion — scenario demonstration and priority inheritance solution
// Time complexity: O(1) per lock/unlock
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -pthread -o out priority_inversion.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <string.h>

// ─── The Problem: Priority Inversion ─────────────────────────────────────────
//
// Three tasks: H (high priority), M (medium priority), L (low priority)
//
// Timeline WITHOUT priority inheritance:
//   t=0: L starts, acquires shared mutex
//   t=1: H wakes, needs mutex → BLOCKED on L
//   t=2: M wakes (higher than L) → PREEMPTS L
//   t=3: M runs to completion — L (and thus H) cannot run
//   t=4: M finishes → L resumes, finishes, releases mutex
//   t=5: H finally runs
//
// Result: H effectively has the priority of L because M can block the chain.
// In real-time systems this can violate hard deadlines.
//
// Solution: Priority Inheritance
//   When H blocks on a mutex held by L, L temporarily inherits H's priority.
//   M can no longer preempt L — L runs, releases mutex, H unblocks.
//
// FreeRTOS: xSemaphoreCreateMutex() implements priority inheritance.
//           xSemaphoreCreateBinary() does NOT — don't use it for mutual exclusion.

// ─── Simulation (without true priorities — demonstrates the access pattern) ──

static pthread_mutex_t g_shared_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t g_print_mutex  = PTHREAD_MUTEX_INITIALIZER;

static void safe_print(const char *msg) {
    pthread_mutex_lock(&g_print_mutex);
    printf("%s", msg);
    fflush(stdout);
    pthread_mutex_unlock(&g_print_mutex);
}

// L: low-priority task — holds mutex for a while
static void *task_low(void *arg) {
    (void)arg;
    safe_print("[L] Low-priority task acquiring mutex...\n");
    pthread_mutex_lock(&g_shared_mutex);
    safe_print("[L] Low-priority task holding mutex (doing work)\n");
    usleep(200000);   // holds mutex for 200 ms
    safe_print("[L] Low-priority task releasing mutex\n");
    pthread_mutex_unlock(&g_shared_mutex);
    safe_print("[L] Low-priority task finished\n");
    return NULL;
}

// H: high-priority task — needs the mutex that L holds
static void *task_high(void *arg) {
    (void)arg;
    usleep(50000);    // wakes 50 ms after L acquires mutex
    safe_print("[H] High-priority task needs mutex — waiting...\n");
    pthread_mutex_lock(&g_shared_mutex);
    safe_print("[H] High-priority task acquired mutex — running critical section\n");
    usleep(50000);
    pthread_mutex_unlock(&g_shared_mutex);
    safe_print("[H] High-priority task finished\n");
    return NULL;
}

// M: medium-priority task — no need for mutex, but preempts L when it can run
static void *task_medium(void *arg) {
    (void)arg;
    usleep(80000);    // wakes while L holds mutex and H is waiting
    safe_print("[M] Medium-priority task running (does NOT need mutex)\n");
    usleep(150000);   // runs for 150 ms — in a real RTOS, this delays L (and H)
    safe_print("[M] Medium-priority task finished\n");
    return NULL;
}

// ─── Priority Inheritance Explanation ────────────────────────────────────────

void explain_priority_inheritance(void) {
    printf("\n=== Priority Inheritance (FreeRTOS) ===\n\n");
    printf("FreeRTOS mutex (xSemaphoreCreateMutex) implements priority inheritance:\n\n");
    printf("  t=0: L acquires mutex\n");
    printf("  t=1: H blocks on mutex → L inherits H's priority\n");
    printf("  t=2: M tries to preempt L → FAILS (L now has H's priority)\n");
    printf("  t=3: L finishes, releases mutex → H's priority restored to L\n");
    printf("  t=4: H runs immediately (highest priority, no longer blocked)\n");
    printf("  t=5: M runs after H finishes\n\n");
    printf("FreeRTOS API:\n");
    printf("  SemaphoreHandle_t mtx = xSemaphoreCreateMutex();\n");
    printf("  xSemaphoreTake(mtx, portMAX_DELAY);  // L acquires\n");
    printf("  // H calls xSemaphoreTake → L's priority temporarily raised to H's\n");
    printf("  xSemaphoreGive(mtx);                 // L releases; priority restored\n\n");
    printf("Key: xSemaphoreCreateBinary() does NOT implement priority inheritance.\n");
    printf("     Always use xSemaphoreCreateMutex() for mutual exclusion.\n");
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== Priority Inversion Demo ===\n");
    printf("Three tasks: H (high), M (medium), L (low)\n");
    printf("L holds mutex, H needs mutex, M preempts L\n\n");

    pthread_t t_l, t_h, t_m;
    pthread_create(&t_l, NULL, task_low,    NULL);
    pthread_create(&t_h, NULL, task_high,   NULL);
    pthread_create(&t_m, NULL, task_medium, NULL);

    pthread_join(t_l, NULL);
    pthread_join(t_h, NULL);
    pthread_join(t_m, NULL);

    explain_priority_inheritance();

    pthread_mutex_destroy(&g_shared_mutex);
    pthread_mutex_destroy(&g_print_mutex);
    return 0;
}
