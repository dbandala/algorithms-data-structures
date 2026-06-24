// Memory layout of a C program — visualizing segment placement
// Covers: .text, .data, .bss, stack, heap, and where different variables live
// Time complexity: N/A (demonstration)
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out memory_layout.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

int main(void);   // forward declaration for printing main's address

// ─── Variables In Each Segment ────────────────────────────────────────────────

// .text (code) — functions live here; also string literals and const globals

// .rodata (read-only data, part of .text or its own section)
const uint32_t ROM_TABLE[4] = {0x11, 0x22, 0x33, 0x44};  // .rodata
const char     BANNER[]     = "Embedded Systems";          // .rodata

// .data — initialized non-const globals and statics (copied from Flash to RAM at boot)
uint32_t g_counter       = 100;   // .data — has a non-zero initial value
static uint32_t s_state  = 0xFF;  // .data — file-scope static, non-zero

// .bss — zero-initialized globals and statics (NOT stored in Flash, just zeroed at boot)
uint32_t g_buffer[64];            // .bss — implicitly zeroed
static uint8_t s_flag;            // .bss — implicitly zeroed

// ─── Stack vs Heap ────────────────────────────────────────────────────────────
//
// Stack: automatic storage — local variables; grows downward on most architectures;
//        lifetime is the enclosing scope/function call.
//
// Heap:  dynamic storage — malloc/free; grows upward; fragmentation risk; avoid in
//        deeply embedded code.

void show_addresses(void) {
    // Stack variables
    uint32_t stack_var_a = 0xAAAA;
    uint32_t stack_var_b = 0xBBBB;

    // Heap allocation (intentionally avoided in embedded, shown for comparison)
    uint32_t *heap_ptr = (uint32_t *)malloc(sizeof(uint32_t));
    if (heap_ptr) {
        *heap_ptr = 0xCCCC;
    }

    printf("=== Address Space Overview ===\n\n");

    // Code (.text)
    printf(".text  (code)     : %p  show_addresses()\n",  (void *)show_addresses);
    printf(".text  (code)     : %p  main()\n",            (void *)main);

    // Read-only data (.rodata)
    printf(".rodata           : %p  ROM_TABLE\n",         (void *)ROM_TABLE);
    printf(".rodata           : %p  BANNER\n",            (void *)BANNER);

    // Initialized data (.data)
    printf(".data             : %p  g_counter=%u\n",      (void *)&g_counter, g_counter);
    printf(".data             : %p  s_state=0x%X\n",      (void *)&s_state, s_state);

    // Zero-initialized data (.bss)
    printf(".bss              : %p  g_buffer[0]=%u\n",    (void *)&g_buffer[0], g_buffer[0]);
    printf(".bss              : %p  s_flag=%u\n",         (void *)&s_flag, s_flag);

    // Stack (local variables)
    printf("stack             : %p  stack_var_a\n",       (void *)&stack_var_a);
    printf("stack             : %p  stack_var_b\n",       (void *)&stack_var_b);

    // Heap
    if (heap_ptr) {
        printf("heap              : %p  *heap_ptr=0x%X\n", (void *)heap_ptr, *heap_ptr);
        free(heap_ptr);
    }

    printf("\nNOTE: on a real MCU, .text/.rodata are in Flash (low addresses),\n");
    printf("      .data/.bss are in SRAM, and stack is at the top of SRAM.\n");
}

// ─── Demonstrating Static Local Variables ─────────────────────────────────────
//
// A static local is NOT on the stack — it lives in .data or .bss and persists
// across function calls. Critical for embedded: counters, state, one-time init.

uint32_t call_count(void) {
    static uint32_t count = 0;  // .data or .bss depending on initial value
    return ++count;
}

// ─── Stack Growth Direction ───────────────────────────────────────────────────

void check_stack_direction(void) {
    uint8_t outer = 0;
    uint8_t inner = 0;  // may be same frame on some compilers — call a nested fn

    (void)inner;
    printf("\n=== Stack Growth ===\n");
    printf("outer local &=%p\n", (void *)&outer);
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    show_addresses();

    printf("\n=== Static Local Variable (persists across calls) ===\n");
    printf("call_count() = %u (expect 1)\n", call_count());
    printf("call_count() = %u (expect 2)\n", call_count());
    printf("call_count() = %u (expect 3)\n", call_count());

    check_stack_direction();

    printf("\n=== Segment Characteristics Summary ===\n");
    printf("Segment    | Location   | Lifetime     | Init\n");
    printf("-----------|------------|--------------|------------------\n");
    printf(".text      | Flash/ROM  | Forever      | Read-only code\n");
    printf(".rodata    | Flash/ROM  | Forever      | Const data\n");
    printf(".data      | RAM        | Program run  | Copied from Flash\n");
    printf(".bss       | RAM        | Program run  | Zeroed at startup\n");
    printf("stack      | RAM (top)  | Function     | Not initialized\n");
    printf("heap       | RAM        | malloc/free  | Not initialized\n");

    return 0;
}
