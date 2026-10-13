# UART Command Parser

A real-world firmware pattern: receive ASCII commands over UART into a circular
buffer (ISR-safe), then parse and dispatch them in the main loop.

---

## What This Demonstrates

- Circular buffer for UART RX (ISR writes, main reads — lock-free 1P/1C)
- Line-based protocol: commands terminated by `\r\n` or `\n`
- Command dispatcher using a lookup table (function pointer per command)
- Input validation at the system boundary
- Non-blocking design: main loop never busy-waits on UART

---

## Supported Commands

| Command | Description |
|---------|-------------|
| `LED ON` | Turn the LED on |
| `LED OFF` | Turn the LED off |
| `STATUS` | Print system status |
| `RESET` | Simulate system reset |
| `HELP` | List commands |

---

## Build and Run

```bash
gcc -Wall -Wextra -std=c11 -o uart_parser uart_parser.c && ./uart_parser
```
