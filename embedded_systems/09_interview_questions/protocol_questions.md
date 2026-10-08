# Protocol Interview Q&A — UART, SPI, I2C, CAN

Detailed question-and-answer reference for hardware protocol questions
that appear in senior embedded engineer interviews.

---

## UART

**Q: What information must both UART peers agree on before communication starts?**
> Baud rate, number of data bits (usually 8), parity (none/even/odd), number of stop
> bits (1 or 2). This is summarized as a format string like "115200 8N1".
> Any mismatch causes framing errors or garbled data.

**Q: How do you calculate the baud rate error for a given MCU clock?**
> `divisor = round(F_clk / baud_rate)` ; `actual_baud = F_clk / divisor` ;
> `error = |actual - target| / target × 100%`. Acceptable error is < ~3%.
> Example: F_clk = 8 MHz, target = 115200 baud → divisor ≈ 69.4 → round to 69
> → actual = 115,942 → error ≈ 0.64% ✓

**Q: What is a framing error?**
> The UART receiver expected a stop bit (HIGH) but received a space (LOW).
> Indicates baud rate mismatch, line noise, or a connected device with different settings.

**Q: What is a parity error?**
> The received parity bit does not match the expected value computed from the data bits.
> Indicates a single-bit (or odd number of bit) flip during transmission.
> Note: parity cannot detect 2-bit errors.

**Q: How does hardware flow control (RTS/CTS) work?**
> RTS (Request to Send): sender pulls it LOW to signal "I want to send."
> CTS (Clear to Send): receiver pulls it LOW to signal "I'm ready to receive."
> The sender must not transmit unless CTS is asserted. Prevents buffer overruns
> without software handshaking.

**Q: Why might you choose DMA for UART reception instead of interrupt-per-byte?**
> At 115200 baud with 8N1, a byte arrives every ~87 µs — an ISR every 87 µs.
> At 1 Mbaud, that's every 10 µs — extremely high CPU interrupt overhead.
> DMA fills the buffer autonomously, generates a single interrupt when full
> (or half-full), freeing the CPU for other work.

---

## SPI

**Q: How many wires does SPI require? What is each for?**
> 4 wires: SCLK (clock), MOSI (Master Out Slave In), MISO (Master In Slave Out),
> CS (Chip Select, active low). Multiple slaves share SCLK/MOSI/MISO; each has a
> separate CS line.

**Q: Explain CPOL and CPHA and why they matter.**
> CPOL (clock polarity): idle state of SCLK — 0=idle LOW, 1=idle HIGH.
> CPHA (clock phase): which edge samples data — 0=first edge, 1=second edge.
> Both master and slave must use the same mode or data will be misread.
> Mode 0 (0,0) and Mode 3 (1,1) are by far the most common in practice.

**Q: How do you talk to multiple SPI slaves?**
> Each slave has its own CS line. The master deasserts all CS lines when idle,
> then asserts only the target slave's CS before a transfer. Slaves with CS
> deasserted ignore SCLK/MOSI and tri-state MISO.

**Q: What is daisy-chaining in SPI?**
> Multiple slaves connected in a ring: master's MOSI → Slave1's SI → Slave1's SO →
> Slave2's SI → ... → master's MISO. All CS lines tied together.
> One long transfer shifts data through all slaves simultaneously (used in LED drivers).

**Q: Why is SPI faster than I2C?**
> SPI is full-duplex and has no address phase or ACK overhead. Maximum clock is
> limited only by trace capacitance and the slave's max speed. I2C tops out at
> 3.4 MHz (HS mode); SPI regularly runs at 40–80 MHz.

---

## I2C

**Q: How does I2C address a device?**
> The master sends a 7-bit address (or 10-bit in extended mode) followed by a
> direction bit (0=write, 1=read). All slaves on the bus see this; only the matching
> slave ACKs by pulling SDA low.

**Q: What are valid START and STOP conditions?**
> START: SDA transitions HIGH→LOW while SCL is HIGH.
> STOP: SDA transitions LOW→HIGH while SCL is HIGH.
> Both are generated only by the master (or by a multi-master that has won arbitration).

**Q: What does a NACK mean and when does it occur?**
> The receiver does NOT pull SDA low during the ACK bit. This means:
> 1. No device responded to the address (wrong address or device not present).
> 2. Device busy or not ready (common for EEPROMs during write cycle).
> 3. Data byte not accepted (e.g., invalid register pointer).
> 4. Master signals the last byte of a read — signals slave to stop sending.

**Q: What is clock stretching?**
> A slave holds SCL LOW after the master releases it, pausing the transaction.
> Used when the slave needs more time to prepare data (e.g., an ADC conversion).
> Not all I2C masters support clock stretching — check the spec.

**Q: What is I2C bus arbitration (multi-master)?**
> Two masters can try to drive SDA simultaneously. Because SDA is open-drain,
> a LOW from any master dominates. Each master monitors SDA while transmitting;
> if it writes HIGH but reads LOW, another master drove it — the losing master
> backs off and retries. This is non-destructive (winning master continues normally).

**Q: What are typical I2C address conflicts?**
> Many sensors use fixed addresses. Common conflicts: 0x48 (TMP102/ADS1015/PCF8574),
> 0x3C (SSD1306 OLED). Solutions: use ADDR pin variants (e.g., 0x48–0x4B via A0/A1),
> use I2C multiplexer (TCA9548A), or use separate I2C buses.

---

## CAN Bus

**Q: What is the CAN bus physical layer?**
> Differential pair: CAN_H and CAN_L. Dominant bit (logical 0): CAN_H = 3.5V,
> CAN_L = 1.5V, differential = 2V. Recessive bit (logical 1): both at 2.5V
> (passive state). Termination: 120Ω at each end of the bus (matched to cable impedance).

**Q: Explain CAN arbitration.**
> Multi-master: any node can transmit when the bus is idle. If two nodes transmit
> simultaneously, arbitration is bit-by-bit:
> - A node transmitting a recessive (1) bit monitors the bus.
> - If it reads dominant (0), another node won — the loser backs off immediately.
> - Lower numeric frame ID → more leading zeros → more dominant bits → wins arbitration.
> This is non-destructive; the winning frame is not corrupted.

**Q: What is the CAN standard frame structure?**
> `SOF(1) | ID(11) | RTR(1) | IDE(1) | r0(1) | DLC(4) | Data(0–8 bytes) | CRC(15) | ACK(2) | EOF(7)`
> - SOF: Start of Frame (dominant bit)
> - ID: 11-bit message identifier (also determines priority)
> - RTR: Remote Transmission Request (1 = requesting data from another node)
> - DLC: Data Length Code (0–8 bytes)
> - CRC: 15-bit polynomial checksum
> - ACK: any receiving node pulls dominant to acknowledge

**Q: What is bit stuffing in CAN?**
> After 5 consecutive bits of the same polarity, the transmitter inserts one
> complementary "stuff bit." The receiver strips it. Purpose: ensure enough
> signal transitions for bit synchronization and error detection.

**Q: What are the CAN error frames / error states?**
> Error Active: normal — can send active error frames (6 dominant bits).
> Error Passive: send passive error frames (6 recessive bits) — bus disruption reduced.
> Bus Off: too many errors (TEC > 255) — node disconnects, requires intervention.
> Transitions are controlled by Transmit Error Counter (TEC) and Receive Error Counter (REC).

**Q: What is the maximum data rate and cable length for CAN?**
> At 1 Mbit/s: max ~40 m (signal propagation limits). At 250 kbit/s: ~250 m.
> At 125 kbit/s: ~500 m. The bus speed × length product is limited by propagation delay.
> For longer distances: use CAN FD at lower speeds, or ISO 11898-3 (low-speed fault tolerant).

---

## Mixed Protocol Q&A

**Q: When would you choose I2C over SPI?**
> I2C: fewer wires (2 vs 4+), multi-master, built-in addressing, acceptable for slow
> sensors (< 400 kHz reads). SPI: needed for higher speed, no ACK overhead,
> streaming data (display, DAC). I2C when pin count is critical; SPI when speed matters.

**Q: How do you debug a protocol issue on an embedded system?**
> 1. Logic analyzer: capture raw bits, trigger on START/CS, decode protocol.
> 2. Scope: check signal integrity (levels, edges, noise, reflections).
> 3. Compare timing to datasheet requirements (setup/hold times, CS timing).
> 4. Print captured bytes via UART logging.
> 5. Check pull-up/pull-down resistor values and supply voltage.
