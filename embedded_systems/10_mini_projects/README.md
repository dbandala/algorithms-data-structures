# 10 — Mini Projects

End-to-end projects that integrate concepts from all previous modules.
Each project is self-contained with its own README, compiles on a host machine,
and demonstrates a pattern commonly used in production embedded firmware.

---

## Projects

| Project | Key Concepts |
|---------|-------------|
| [`led_blinker_state_machine/`](led_blinker_state_machine/README.md) | FSM, timer callbacks, GPIO abstraction |
| [`uart_command_parser/`](uart_command_parser/README.md) | Circular buffer, UART ISR, command dispatch |
| [`rtos_producer_consumer/`](rtos_producer_consumer/README.md) | FreeRTOS tasks, queue, semaphore, priority |

---

## How to Build and Run

All projects compile on macOS/Linux with:

```bash
gcc -Wall -Wextra -std=c11 -o out <project>/<file>.c && ./out
```

No embedded toolchain is required. Hardware-specific code is clearly commented.

---

## What to Demonstrate in an Interview

When walking through a mini project in an interview, structure your explanation:

1. **Requirements** — what does the system need to do?
2. **Architecture** — how are the components divided? (layers, modules, tasks)
3. **Key design decisions** — why FSM? why circular buffer? why a queue vs shared variable?
4. **Safety and reliability** — error handling, watchdog, bounds checking
5. **What you would add for production** — OTA update, power management, logging
