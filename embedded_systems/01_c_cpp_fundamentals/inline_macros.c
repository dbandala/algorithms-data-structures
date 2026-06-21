// Struct alignment, padding, and offsetof — embedded memory efficiency
// Time complexity: O(1)
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out memory_alignment.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <stddef.h>  // offsetof

// ─── 1. Padding Waste: Worst vs Best Layout ──────────────────────────────────

// Wasteful: alternating small/large fields forces padding
struct Wasteful {
    uint8_t  a;    // 1 byte  + 3 padding
    uint32_t b;    // 4 bytes
    uint8_t  c;    // 1 byte  + 3 padding
    uint32_t d;    // 4 bytes
};  // total: 16 bytes (8 wasted)

// Efficient: fields sorted largest → smallest
struct Efficient {
    uint32_t b;    // 4 bytes
    uint32_t d;    // 4 bytes
    uint8_t  a;    // 1 byte
    uint8_t  c;    // 1 byte  + 2 padding (struct must be multiple of 4)
};  // total: 12 bytes (2 wasted) vs 16 — saves 4 bytes per instance

// ─── 2. offsetof — Find byte offset of a struct member ───────────────────────

struct Packet {
    uint8_t  sync;       // offset 0
    uint16_t id;         // offset 2 (1 byte padding after sync)
    uint32_t payload;    // offset 4
    uint8_t  checksum;   // offset 8
};  // total: 12 bytes (1 byte padding after checksum)

// ─── 3. Packed Struct ────────────────────────────────────────────────────────
// __attribute__((packed)) removes all padding — use only when:
// - Mapping a fixed external binary format (protocol, file)
// - You accept the risk of unaligned access (can cause bus fault on ARM if
//   unaligned access trapping is enabled)

struct __attribute__((packed)) PackedPacket {
    uint8_t  sync;       // offset 0
    uint16_t id;         // offset 1 (no padding)
    uint32_t payload;    // offset 3 (no padding — UNALIGNED on 32-bit arch!)
    uint8_t  checksum;   // offset 7
};  // total: 8 bytes — no padding

// ─── 4. Alignment Rule Summary ───────────────────────────────────────────────
//
// Natural alignment: a type of size N should be at an address divisible by N.
// Struct trailing padding: compiler adds bytes at the end so that an array of
// the struct keeps each element naturally aligned.

// ─── 5. DMA Buffer Alignment ─────────────────────────────────────────────────
// DMA engines often require buffers at specific alignments (e.g., 4-byte or
// 32-byte for cache-line coherency).

static uint8_t dma_buf[128] __attribute__((aligned(32)));

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== Struct Sizes ===\n");
    printf("sizeof(Wasteful)       = %zu (expect 16)\n", sizeof(struct Wasteful));
    printf("sizeof(Efficient)      = %zu (expect 12)\n", sizeof(struct Efficient));
    printf("sizeof(Packet)         = %zu\n",             sizeof(struct Packet));
    printf("sizeof(PackedPacket)   = %zu (expect 8)\n",  sizeof(struct PackedPacket));

    printf("\n=== offsetof — Packet ===\n");
    printf("offsetof(sync)     = %zu (expect 0)\n",  offsetof(struct Packet, sync));
    printf("offsetof(id)       = %zu (expect 2)\n",  offsetof(struct Packet, id));
    printf("offsetof(payload)  = %zu (expect 4)\n",  offsetof(struct Packet, payload));
    printf("offsetof(checksum) = %zu (expect 8)\n",  offsetof(struct Packet, checksum));

    printf("\n=== offsetof — PackedPacket (no padding) ===\n");
    printf("offsetof(sync)     = %zu (expect 0)\n",  offsetof(struct PackedPacket, sync));
    printf("offsetof(id)       = %zu (expect 1)\n",  offsetof(struct PackedPacket, id));
    printf("offsetof(payload)  = %zu (expect 3)\n",  offsetof(struct PackedPacket, payload));
    printf("offsetof(checksum) = %zu (expect 7)\n",  offsetof(struct PackedPacket, checksum));

    printf("\n=== DMA Buffer Alignment ===\n");
    printf("dma_buf address: %p\n", (void *)dma_buf);
    printf("address %% 32 == %lu (expect 0 — 32-byte aligned)\n",
           (unsigned long)((uintptr_t)dma_buf % 32));

    printf("\n=== Alignment Rules Summary ===\n");
    printf("uint8_t  — aligned to 1 byte\n");
    printf("uint16_t — aligned to 2 bytes\n");
    printf("uint32_t — aligned to 4 bytes\n");
    printf("uint64_t — aligned to 8 bytes\n");
    printf("Struct   — aligned to the largest member's alignment requirement\n");

    return 0;
}
