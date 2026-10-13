# RTOS Producer-Consumer

A complete producer-consumer implementation using POSIX threads as a stand-in
for FreeRTOS tasks, with side-by-side FreeRTOS API equivalents commented throughout.

---

## What This Demonstrates

- Two-task architecture: producer fills a queue, consumer drains it
- Message queue for safe inter-task communication (no shared variables)
- Binary semaphore for task signaling
- Bounded queue: producer blocks when queue is full (back-pressure)
- FreeRTOS API equivalents commented next to every POSIX call

---

## Architecture

```
  [Producer Task]                    [Consumer Task]
  ADC / Sensor read                  Process data
  xQueueSend → ████████████████████ → xQueueReceive
                  Message Queue
               (depth = 8, blocks on full/empty)
```

---

## FreeRTOS Equivalents

| POSIX | FreeRTOS |
|-------|----------|
| `pthread_create` | `xTaskCreate` |
| `sem_wait` / `sem_post` | `xSemaphoreTake` / `xSemaphoreGive` |
| Queue (custom) | `xQueueCreate` / `xQueueSend` / `xQueueReceive` |
| `usleep` | `vTaskDelay(pdMS_TO_TICKS(ms))` |

---

## Build and Run

```bash
gcc -Wall -Wextra -std=c11 -pthread -o producer_consumer producer_consumer.c && ./producer_consumer
```
