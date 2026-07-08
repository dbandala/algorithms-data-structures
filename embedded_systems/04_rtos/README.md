# 04 — Real-Time Operating Systems (RTOS)

An RTOS is the heart of most non-trivial embedded applications. This module covers
the core abstractions — tasks, synchronization primitives, and inter-task communication
— using both generic concepts and the FreeRTOS API.

---

## Key Concepts

### Tasks (Threads)
An RTOS task is an independent execution context with its own stack and priority.

FreeRTOS task states:
```
         xTaskCreate()
              │
              ▼
           READY  ◄──────────────────────────────────────┐
              │                                          │
    (highest-priority ready)                     (preempted or yield)
              │                                          │
              ▼                                          │
           RUNNING ─────────────────────────────────────►│
              │
    (event wait / delay)
              │
              ▼
           BLOCKED ──(event occurs / delay expires)──► READY
              │
      (vTaskSuspend)
              │
              ▼
          SUSPENDED ──(vTaskResume)──► READY
```

### Scheduling
- **Preemptive**: higher-priority task ready → immediately runs; lower-priority preempted
- **Cooperative**: task runs until it yields (`taskYIELD()`) or blocks
- **Round-robin**: equal-priority tasks share time slices (one tick each by default in FreeRTOS)

FreeRTOS uses a **tick interrupt** (default 1 ms) to enforce time slicing and unblock delayed tasks.

### Semaphore vs Mutex

| | Semaphore | Mutex |
|--|-----------|-------|
| Use | Signaling / counting | Mutual exclusion |
| Owner | None — any task can signal | The task that takes it must give it |
| Priority inheritance | No | Yes (in FreeRTOS) |
| Interrupt safe | Yes (`xSemaphoreGiveFromISR`) | No |
| ISR signaling to task | ✅ | ❌ |
| Protecting shared data | Possible but wrong | Correct choice |

### Priority Inversion
Occurs when a high-priority task (H) is blocked waiting for a resource held by a
low-priority task (L), and a medium-priority task (M) preempts L.
Result: H effectively runs at L's priority.

**Priority inheritance**: when L holds a mutex that H is waiting for, L temporarily
inherits H's priority until it releases the mutex.

### Deadlock
Four necessary conditions (Coffman):
1. **Mutual exclusion** — resource held by at most one task
2. **Hold and wait** — task holds one resource while waiting for another
3. **No preemption** — resources can't be forcibly taken
4. **Circular wait** — a cycle of tasks, each waiting on the next

Prevention: always acquire multiple mutexes in the same order across all tasks.

### Message Queues
Pass data (not just signals) between tasks. Zero-copy if using pointers.
In FreeRTOS, `xQueueSend` / `xQueueReceive` are the primary IPC mechanism.

### Context Switching
When the scheduler decides to run a different task, it:
1. Saves current task's CPU registers + stack pointer to its TCB (Task Control Block)
2. Loads the new task's registers + stack pointer from its TCB
3. Returns to the new task's last PC address

On ARM Cortex-M, FreeRTOS uses `PendSV` (lowest-priority exception) for context switches
to ensure they happen at the tail end of all real interrupt handling.

---

## Files in This Module

| File | Topic |
|------|-------|
| `task_concepts.c` | Task creation, priorities, states — with POSIX threads simulation |
| `scheduling.c` | Preemptive/cooperative scheduling simulation, time-slice round-robin |
| `semaphores.c` | Binary and counting semaphores — concepts + FreeRTOS API reference |
| `mutexes.c` | Mutex vs semaphore, recursive mutex, FreeRTOS API reference |
| `message_queues.c` | Queue-based producer-consumer — concepts + FreeRTOS API reference |
| `priority_inversion.c` | Priority inversion scenario, priority inheritance solution |
| `deadlock.c` | Deadlock scenario, lock-ordering prevention strategy |
| `timers.c` | One-shot and auto-reload software timers, FreeRTOS timer API |

---

## Common Interview Questions

1. **What is the difference between a semaphore and a mutex?**
   > A mutex is for mutual exclusion and must be given by the same task that took it;
   > it supports priority inheritance. A semaphore is for signaling — any task (or ISR)
   > can give it, and it has no owner concept.

2. **Explain priority inversion. How does FreeRTOS handle it?**
   > A high-priority task blocks on a mutex held by a low-priority task. A medium task
   > can now run indefinitely, starving the high-priority task. FreeRTOS uses **priority
   > inheritance**: the low-priority task temporarily runs at the high task's priority
   > until it releases the mutex.

3. **What is a deadlock? How do you prevent it?**
   > Deadlock occurs when a set of tasks each wait for a resource held by another in
   > the set. Prevention: always acquire multiple mutexes in a **consistent global order**
   > across all tasks.

4. **Why does FreeRTOS use `PendSV` for context switching?**
   > `PendSV` is the lowest-priority ARM Cortex-M exception. By doing the context switch
   > there, all real interrupts (peripheral ISRs) complete first, preventing context switch
   > overhead from adding latency to hardware events.

5. **What is the FreeRTOS tick? What happens if a task misses a tick?**
   > The tick is a periodic interrupt (default 1 ms) that the scheduler uses to advance
   > time, unblock delayed tasks, and (with time-slicing) preempt same-priority tasks.
   > Missing a tick (tick interrupt disabled too long in a critical section) delays
   > unblocking of tasks — causing jitter or missed deadlines.

6. **What is a stack overflow in FreeRTOS? How do you detect it?**
   > A task's stack grows beyond its allocated size, overwriting adjacent memory. Detection:
   > FreeRTOS writes a canary pattern at the stack base and checks it in each context
   > switch (configCHECK_FOR_STACK_OVERFLOW = 2).

7. **When would you choose a message queue over a shared variable + semaphore?**
   > Queue: when you need to pass multiple pending values (buffering), or when data
   > ownership must transfer to the consumer. Semaphore + shared variable: when only
   > the latest value matters (no buffering needed).

8. **What is a counting semaphore? Give a real embedded use case.**
   > A semaphore initialized to N, representing N available instances of a resource
   > (e.g., 4 DMA channels). Each `take` decrements; each `give` increments. Task blocks
   > when count reaches 0.

---

## Further Reading

- FreeRTOS Book (free): https://www.freertos.org/Documentation/RTOS_book.html
- *Real-Time Concepts for Embedded Systems* — Qing Li & Caroline Yao
- *RTOS Design and Implementation Guide* — FreeRTOS Reference Manual
