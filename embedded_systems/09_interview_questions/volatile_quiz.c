// volatile quiz — spot-the-bug problems with explanations
// These are the types of code snippets shown in senior embedded interviews.
// Time complexity: N/A
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -O2 -o out volatile_quiz.c && ./out
// NOTE: -O2 is intentional — some bugs only manifest with optimization enabled.

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// ─── Quiz 1: ISR flag polling bug ────────────────────────────────────────────
//
// Question: Is this code correct? What happens at -O2?
//
//   uint8_t g_flag = 0;
//   void ISR(void) { g_flag = 1; }
//   void main_loop(void) { while (!g_flag) { } }
//
// Answer: BUG — g_flag must be volatile.
//   At -O2, the compiler sees g_flag never changes in main_loop and
//   transforms it to: if (!g_flag) { while(1){} } — infinite loop.
//
// Fix:
volatile uint8_t g_flag_correct = 0;
// void ISR_correct(void) { g_flag_correct = 1; }

// ─── Quiz 2: Multi-byte shared variable torn read ─────────────────────────────
//
// Question: On an 8-bit MCU, is this read of g_timestamp safe?
//
//   volatile uint32_t g_timestamp = 0;   // updated in ISR
//   void main(void) { uint32_t t = g_timestamp; process(t); }
//
// Answer: BUG on 8-bit MCU.
//   Reading a 32-bit value takes 4 separate 8-bit reads. An ISR can fire
//   between any two reads, partially updating g_timestamp → torn read.
//
// Fix: disable interrupts around the read.
volatile uint32_t g_timestamp = 0;

uint32_t read_timestamp_safe(void) {
    // __disable_irq(); // ARM: CPSID I
    uint32_t t = g_timestamp;
    // __enable_irq();
    return t;
}

// ─── Quiz 3: Incorrect use of volatile for synchronization ───────────────────
//
// Question: Does volatile guarantee ordering / atomicity between two threads?
//
//   volatile int ready = 0;
//   volatile int data  = 0;
//   void producer(void) { data = 42; ready = 1; }
//   void consumer(void) { while (!ready) {} use(data); }
//
// Answer: NOT safe on multicore or OoO processors.
//   volatile prevents compiler reordering but does NOT prevent CPU memory
//   reordering (store-store, load-load). The CPU may write ready=1 before
//   data=42 is visible to the other core.
//
// Fix: use C11 atomics (stdatomic.h) or explicit memory barriers.
//   _Atomic int ready = 0;   _Atomic int data = 0;

// ─── Quiz 4: const volatile pointer to hardware register ─────────────────────
//
// Question: Which declaration is correct for a read-only hardware status register?
//
//   (a) const    volatile uint32_t *p = (uint32_t *)0x40001000;
//   (b) volatile const    uint32_t *p = (uint32_t *)0x40001000;
//   (c) volatile uint32_t * const   p = (uint32_t *)0x40001000;
//
// Answer: (a) and (b) are equivalent and both correct for the target data.
//   The pointer itself can be reseated.
//   (c) makes the POINTER const (can't change where it points) but not the data —
//       does not prevent writing to the register.
//   For a truly read-only register, use:
//   const volatile uint32_t * const p = (const volatile uint32_t *)ADDR;

// ─── Quiz 5: volatile does NOT make ++ atomic ─────────────────────────────────
//
// Question: Is this safe if ISR and main both call increment_counter()?
//
//   volatile uint32_t g_counter = 0;
//   void increment_counter(void) { g_counter++; }
//
// Answer: BUG — volatile ++ is NOT atomic.
//   g_counter++ compiles to: LOAD, ADD, STORE.
//   If an ISR fires between LOAD and STORE, the ISR's increment is lost.
//
// Fix: use a critical section, or C11 _Atomic, or __sync_fetch_and_add.

volatile uint32_t g_counter = 0;

// Safe increment: must be called within a critical section in real code
static void increment_safe(void) {
    // __disable_irq();
    g_counter++;
    // __enable_irq();
}

// ─── Quiz 6: volatile function pointer array ─────────────────────────────────
//
// Question: ISR handler table must have volatile pointers?
//
// Answer: NO. The function pointers in a vector table are set once at startup
//   and never change. They do not need to be volatile.
//   If the vector table is in Flash, it can't be changed anyway.
//   Only memory-mapped register values and variables shared with ISRs need volatile.

// ─── Demonstrate correct vs incorrect ────────────────────────────────────────

int main(void) {
    printf("=== volatile Quiz Answers ===\n\n");

    printf("Quiz 1: ISR flag\n");
    printf("  BUG: uint8_t g_flag missing volatile\n");
    printf("  FIX: volatile uint8_t g_flag\n\n");

    printf("Quiz 2: Multi-byte torn read\n");
    printf("  BUG: 32-bit read on 8-bit MCU not atomic\n");
    printf("  FIX: disable IRQ around the read-copy-enable sequence\n\n");

    printf("Quiz 3: volatile for synchronization\n");
    printf("  BUG: volatile does NOT prevent CPU reordering (only compiler)\n");
    printf("  FIX: use C11 _Atomic or explicit memory barriers\n\n");

    printf("Quiz 4: const volatile pointer\n");
    printf("  CORRECT: const volatile uint32_t *p  — pointer to read-only, volatile data\n");
    printf("  WRONG:   volatile uint32_t * const p — const pointer, but data writable!\n\n");

    printf("Quiz 5: volatile ++ atomicity\n");
    printf("  BUG: volatile ++ = LOAD + ADD + STORE — not atomic\n");
    printf("  FIX: disable IRQ around the increment, or use _Atomic / GCC builtins\n\n");

    printf("Quiz 6: ISR vector table volatile\n");
    printf("  volatile NOT needed for function pointers in a vector table\n");
    printf("  volatile IS needed for: registers, ISR-updated variables, shared memory\n");

    // Demonstrate safe usage
    g_flag_correct = 0;
    (void)read_timestamp_safe();
    increment_safe();
    increment_safe();
    printf("\ng_counter after 2 safe increments: %u (expect 2)\n", g_counter);

    return 0;
}
