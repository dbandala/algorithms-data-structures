// Pointers and memory — interview-focused examples
// Covers: pointer arithmetic, function pointers, void pointers, const pointers,
//         array-pointer duality, double pointers
// Time complexity: N/A (demonstrations)
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out pointers_and_memory.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

// ─── Pointer Arithmetic ────────────────────────────────────────────────────────

void pointer_arithmetic_demo(void) {
    uint32_t arr[4] = {0xAA, 0xBB, 0xCC, 0xDD};
    uint32_t *p = arr;

    printf("=== Pointer Arithmetic ===\n");
    printf("arr[0] via p:    0x%X\n", *p);       // 0xAA
    printf("arr[1] via p+1:  0x%X\n", *(p + 1)); // 0xBB — advances by sizeof(uint32_t)

    // Byte-level walk — cast to uint8_t *
    uint8_t *byteptr = (uint8_t *)arr;
    printf("byte 0 of arr[0]: 0x%X\n", *byteptr);      // depends on endianness
    printf("byte 1 of arr[0]: 0x%X\n", *(byteptr + 1));

    // Difference between pointers (result in elements, not bytes)
    uint32_t *end = arr + 4;
    ptrdiff_t len = end - arr;  // = 4
    printf("distance end-arr: %td elements\n", len);
}

// ─── const Pointer Variations ─────────────────────────────────────────────────
// Interview classic: know all four combinations

void const_pointer_demo(void) {
    int x = 10, y = 20;

    int *p1 = &x;              // non-const ptr to non-const int
    const int *p2 = &x;        // non-const ptr to CONST int   — can't modify *p2
    int * const p3 = &x;       // CONST ptr to non-const int   — can't change p3
    const int * const p4 = &x; // CONST ptr to CONST int       — can't modify either

    *p1 = 11;    // OK
    p1  = &y;    // OK
    // *p2 = 11; // Error: read-only target
    p2  = &y;    // OK: pointer itself is not const
    *p3 = 12;    // OK: target is not const
    // p3  = &y; // Error: pointer is const
    (void)p4;    // silence unused warning

    printf("\n=== const Pointer Variations ===\n");
    printf("p1=%d  p2=%d  p3=%d\n", *p1, *p2, *p3);
}

// ─── Function Pointers ────────────────────────────────────────────────────────
// Used heavily in embedded for: callbacks, state machine dispatch, driver vtables

typedef int (*operation_fn)(int, int);  // type alias for cleaner code

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

// Dispatch table — index maps to operation (common in embedded state machines)
static const operation_fn ops[3] = { add, sub, mul };

void function_pointer_demo(void) {
    printf("\n=== Function Pointers ===\n");
    printf("add(3,2) via table: %d\n", ops[0](3, 2)); // 5
    printf("sub(3,2) via table: %d\n", ops[1](3, 2)); // 1
    printf("mul(3,2) via table: %d\n", ops[2](3, 2)); // 6

    // Direct usage
    operation_fn fp = add;
    printf("fp = add, fp(7,8) = %d\n", fp(7, 8));     // 15
}

// ─── Void Pointer ─────────────────────────────────────────────────────────────
// Generic "any pointer" — must cast before dereference; used in qsort, memcpy, etc.

void void_pointer_demo(void) {
    int    ival = 42;
    float  fval = 3.14f;

    void *vp;

    vp = &ival;
    printf("\n=== Void Pointer ===\n");
    printf("int via void*:   %d\n", *(int *)vp);

    vp = &fval;
    printf("float via void*: %.2f\n", *(float *)vp);
}

// ─── Double Pointers ──────────────────────────────────────────────────────────
// Common use: modifying a pointer inside a function (e.g., linked list insert)

void allocate_buffer(uint8_t **buf_out, size_t *len_out) {
    static uint8_t buf[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    *buf_out = buf;   // set caller's pointer
    *len_out = 8;
}

void double_pointer_demo(void) {
    uint8_t *buf;
    size_t  len;
    allocate_buffer(&buf, &len);

    printf("\n=== Double Pointer ===\n");
    printf("buf[0]=%u  buf[7]=%u  len=%zu\n", buf[0], buf[7], len); // 1 8 8
}

// ─── Array-Pointer Duality ────────────────────────────────────────────────────

void array_pointer_demo(void) {
    int arr[5] = {10, 20, 30, 40, 50};

    // arr decays to a pointer to its first element
    int *p = arr;
    printf("\n=== Array-Pointer Duality ===\n");
    printf("arr[2]  == *(arr+2) == p[2] == *(p+2): %d %d %d %d\n",
           arr[2], *(arr + 2), p[2], *(p + 2)); // all 30

    // sizeof(arr) vs sizeof(p)
    printf("sizeof(arr)=%zu  sizeof(p)=%zu\n",
           sizeof(arr), sizeof(p)); // 20 vs 8 (on 64-bit)
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    pointer_arithmetic_demo();
    const_pointer_demo();
    function_pointer_demo();
    void_pointer_demo();
    double_pointer_demo();
    array_pointer_demo();
    return 0;
}
