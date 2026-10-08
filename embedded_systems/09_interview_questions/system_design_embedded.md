# Embedded System Design Interview Q&A

System design questions assess your ability to think through an entire embedded
system — hardware/software partitioning, reliability, communication, and trade-offs.

---

## How to Approach System Design Questions

1. **Clarify requirements** — ask about power, form factor, connectivity, reliability, BOM cost
2. **Choose architecture** — MCU family, RTOS vs bare-metal, communication protocols
3. **Define interfaces** — what talks to what; draw a block diagram
4. **Address reliability** — watchdog, error handling, safe states, fail-safe
5. **Address updates** — how does firmware get updated in the field?
6. **Discuss trade-offs** — you chose X over Y because...

---

## Design Problem 1: Temperature Data Logger

**Prompt:** Design a battery-powered temperature data logger with a microcontroller,
temperature sensor, flash memory, and UART output.

**Requirements:** Log temperature every 10 seconds, 6-month battery life, USB readout.

**Sample Answer:**

**Hardware Block:**
```
Battery → LDO regulator → MCU (low-power Cortex-M0+)
                              ├── I2C → TMP117 temperature sensor
                              ├── SPI → FRAM or NAND flash (wear-leveling)
                              └── USB/UART → USB-CDC or FTDI
```

**MCU Selection:** STM32L0 or nRF52 — µA sleep current, integrated USB or SWD.

**Software Architecture:**
- Main loop: `__WFI()` (sleep most of the time)
- RTC interrupt every 10 s → wake, read I2C sensor (~2 ms), append to flash, sleep
- USB/UART interrupt → stream stored data on request

**Flash Storage:**
- Write 6 bytes per record: `[4-byte timestamp | 2-byte raw temperature]`
- 6 months × 86400 s/day / 10 s × 6 bytes ≈ 9.4 MB → 16 MB SPI flash
- Circular log with wrap-around; track head/tail in non-volatile header block

**Power Budget:**
- Active (read + write): ~1 mA × 5 ms = 5 µA·s per sample
- Sleep: 1 µA × 10 s = 10 µA·s per cycle
- Total average: ~2 µA — achievable 6-month lifetime with 1000 mAh LiPo

**Reliability:**
- Watchdog (IWDG) with 30 s timeout; kicked after each successful log cycle
- Power-on test: verify I2C sensor responds; set error flag if not
- CRC on each flash record; skip corrupted records on readout

---

## Design Problem 2: Motor Controller with Fault Detection

**Prompt:** Design a brushless DC motor controller with fault detection and safe-state logic.

**Sample Answer:**

**Hardware Block:**
```
MCU ──PWM──► Gate driver ──► MOSFET bridge ──► BLDC motor
 │                                                   │
 ├── ADC ← Current shunt (overcurrent detect)        │
 ├── ADC ← Phase voltage sense (back-EMF)            │
 ├── ADC ← Bus voltage monitor                       │
 └── Digital: hall sensors / encoder                 ◄──┘
```

**State Machine:**
```
IDLE → STARTING (ramp up) → RUNNING
RUNNING → FAULT (on trip) → SAFE_STATE (gate signals disabled)
SAFE_STATE → IDLE (after reset/clear)
```

**Fault Conditions:**
- Overcurrent: ADC > threshold → immediate gate disable via hardware comparator (< 1 µs)
- Overvoltage/undervoltage: ADC on bus rail checked each PWM cycle
- Overtemperature: NTC thermistor ADC; derate then shutdown
- Hall sensor fault: timeout on expected commutation events
- Stall: no back-EMF / encoder movement under load for > N ms

**Safe State:** All gate drive signals driven LOW (or gate driver enable pulled LOW by hardware comparator) → motor coasts to stop. Hardware comparator bypass ensures < 1 µs response for overcurrent — faster than software interrupt path.

**PWM / FOC:**
- Center-aligned PWM on 3-channel timer; deadtime insertion for shoot-through protection
- Speed loop: outer PI controller (1 kHz); current loop: inner PI (10–20 kHz)
- FOC (Field Oriented Control) for torque-efficient operation: Park/Clarke transforms

**Firmware Update:**
- Secondary bootloader in protected Flash sector
- CAN or UART DFU (Device Firmware Upgrade); write to inactive Flash bank; CRC verify; swap

---

## Design Problem 3: IoT Sensor Node

**Prompt:** Design a wireless sensor node that reads an air quality sensor and
sends data to a cloud backend every 5 minutes.

**Sample Answer:**

**Stack:**
```
AQ Sensor (I2C/SPI) → MCU → LoRaWAN / BLE / Wi-Fi → Gateway → Cloud
```

**Protocol Choice:**
- LoRaWAN for > 1 km range, low bandwidth, deep sleep between sends → best for battery
- BLE for < 10 m, frequent updates, existing phone connectivity
- Wi-Fi for high data rate, existing infrastructure, high power

**Security:**
- LoRaWAN: AES-128 session keys (AppSKey, NwkSKey), OTAA for provisioning
- TLS for MQTT/HTTP if Wi-Fi — mutual authentication (device certificate)
- No hardcoded keys in firmware — use secure element (ATECC608) or OTP fuses

**OTA Update:**
- LoRaWAN: FUOTA (Fragmented Update) standard (LoRaWAN 1.0.4)
- Wi-Fi: HTTPS download to inactive partition; SHA-256 verify; atomic swap; rollback on failed boot

**Power:**
- Sense + transmit: 10 ms at 10 mA = 0.1 mAh per cycle
- Sleep 5 minutes: 1 µA = 0.008 mAh
- Average: ~0.12 µA → 2–3 year AA battery life with LoRaWAN

---

## Design Problem 4: Bootloader for Firmware Update

**Prompt:** Describe how you would implement a safe OTA firmware update bootloader.

**Sample Answer:**

**Flash Layout:**
```
[Bootloader | Metadata | App Bank A | App Bank B | NV Config]
  0x08000000   0x08004000  0x08008000   0x08040000  0x0807C000
```

**Update Flow:**
1. Main app receives new firmware over UART/CAN/BLE
2. Main app writes firmware to **inactive** bank (A if currently running B, and vice versa)
3. Main app computes CRC/SHA-256 of written data; verifies against transmitted hash
4. Main app sets "update pending" flag in metadata with boot counter = 3 (rollback guard)
5. Main app resets MCU
6. Bootloader reads metadata, sees update pending
7. Bootloader remaps vector table to new bank; decrements boot counter
8. New firmware boots; if successful, writes "boot confirmed" flag to metadata
9. If MCU resets 3 times without confirmation → bootloader reverts to old bank

**Safety:**
- Bootloader in write-protected Flash sector (RDP Level 1 or option bytes on STM32)
- New firmware validated before swap (never boot an invalid image)
- Boot counter prevents boot loop from corrupting the system permanently

**Key APIs (STM32 as example):**
```c
HAL_FLASH_Unlock();
FLASH_Erase_Sector();      // erase target bank
HAL_FLASH_Program();       // program 32/64-bit words
HAL_FLASH_Lock();
NVIC_SetVectorTable();     // remap vector table to new bank
```

---

## Common Follow-Up Questions

- **What is DMA? When would you use it?**
  > DMA moves data between memory and peripherals without CPU involvement. Use for:
  > ADC sample buffers, SPI/UART bulk transfers at high rates, audio streaming,
  > display framebuffer updates. CPU continues working (or sleeps) while transfer runs.

- **Explain memory-mapped peripherals vs port-mapped I/O.**
  > Memory-mapped: peripherals share the address space with RAM (all modern ARM MCUs).
  > Port-mapped (x86): separate I/O instructions (IN/OUT). Memory-mapped is simpler —
  > any load/store instruction can access peripherals; pointers work normally.

- **What is a race condition in embedded firmware? How do you prevent it?**
  > A race condition occurs when the behavior depends on the timing of two or more
  > concurrent accesses to shared state. Prevention: identify all shared variables,
  > protect accesses with critical sections (disable IRQ or mutex), use message
  > passing (queues) to transfer ownership instead of shared memory.

- **What is defensive programming? Give three concrete examples.**
  > 1. Bounds-check array indices before access (assert or saturate)
  > 2. Validate sensor readings before processing (range check)
  > 3. Check return values of all driver functions (I2C ACK/NACK, SPI status)
  > 4. Use ASSERT macros for programmer invariants (null checks, state machine transitions)
  > 5. Watchdog timer to catch hangs

- **How do you unit test embedded firmware?**
  > Test business logic on the host: mock hardware (HAL) with stub implementations.
  > Use test frameworks (Unity, CMock) with CI/CD. Hardware-in-the-loop (HIL) testing
  > with a real board for integration tests. TDD for critical state machines.
