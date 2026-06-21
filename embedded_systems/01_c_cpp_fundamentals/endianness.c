// Endianness — detection, conversion, and protocol considerations
// Time complexity: O(1) per conversion
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -o out endianness.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <string.h>

// ─── Endianness Detection ─────────────────────────────────────────────────────
//
// Little-endian: LSB at the lowest address  (x86, ARM Cortex-M default)
// Big-endian:    MSB at the lowest address  (network byte order, some DSPs)

typedef enum { LITTLE_ENDIAN_SYS, BIG_ENDIAN_SYS } Endianness;

// Safe detection using a union (avoids strict-aliasing UB compared to pointer cast)
Endianness get_endianness(void) {
    union {
        uint32_t word;
        uint8_t  bytes[4];
    } probe;

    probe.word = 0x01020304U;
    // On little-endian: bytes[0] == 0x04 (least significant byte first)
    // On big-endian:    bytes[0] == 0x01 (most significant byte first)
    return (probe.bytes[0] == 0x04) ? LITTLE_ENDIAN_SYS : BIG_ENDIAN_SYS;
}

// ─── Byte-Swap Functions ──────────────────────────────────────────────────────

uint16_t bswap16(uint16_t x) {
    return (uint16_t)((x >> 8) | (x << 8));
}

uint32_t bswap32(uint32_t x) {
    return ((x & 0x000000FFU) << 24) |
           ((x & 0x0000FF00U) << 8)  |
           ((x & 0x00FF0000U) >> 8)  |
           ((x & 0xFF000000U) >> 24);
}

uint64_t bswap64(uint64_t x) {
    return ((uint64_t)bswap32((uint32_t)(x & 0xFFFFFFFFU)) << 32) |
           (uint64_t)bswap32((uint32_t)(x >> 32));
}

// ─── Network (Big-Endian) to Host Conversion ─────────────────────────────────
// htons / ntohs equivalents — portable, no reliance on POSIX headers

uint16_t host_to_be16(uint16_t x) {
    if (get_endianness() == BIG_ENDIAN_SYS) return x;
    return bswap16(x);
}

uint16_t be16_to_host(uint16_t x) {
    return host_to_be16(x);  // symmetric
}

uint32_t host_to_be32(uint32_t x) {
    if (get_endianness() == BIG_ENDIAN_SYS) return x;
    return bswap32(x);
}

uint32_t be32_to_host(uint32_t x) {
    return host_to_be32(x);
}

// ─── Struct Serialization Without Relying on Struct Layout ───────────────────
//
// NEVER cast a struct directly to bytes for protocol parsing.
// Endianness + padding make the layout non-portable.
// Use explicit byte packing/unpacking instead.

typedef struct {
    uint16_t id;
    uint32_t value;
} SensorFrame;

// Serialize to big-endian byte array (e.g., for CAN or UART packet)
void serialize_sensor_frame(const SensorFrame *frame, uint8_t buf[6]) {
    uint16_t id_be    = host_to_be16(frame->id);
    uint32_t value_be = host_to_be32(frame->value);

    memcpy(buf + 0, &id_be,    2);
    memcpy(buf + 2, &value_be, 4);
}

// Deserialize from big-endian byte array
void deserialize_sensor_frame(const uint8_t buf[6], SensorFrame *frame) {
    uint16_t id_be;
    uint32_t value_be;

    memcpy(&id_be,    buf + 0, 2);
    memcpy(&value_be, buf + 2, 4);

    frame->id    = be16_to_host(id_be);
    frame->value = be32_to_host(value_be);
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    Endianness sys = get_endianness();
    printf("System endianness: %s\n\n",
           sys == LITTLE_ENDIAN_SYS ? "LITTLE-ENDIAN" : "BIG-ENDIAN");

    // Byte-swap tests
    printf("bswap16(0x1234)     = 0x%04X  (expect 0x3412)\n", bswap16(0x1234));
    printf("bswap32(0x12345678) = 0x%08X  (expect 0x78563412)\n", bswap32(0x12345678));
    printf("bswap64(0x0102030405060708) = 0x%016llX  (expect 0x0807060504030201)\n",
           (unsigned long long)bswap64(0x0102030405060708ULL));

    // Network byte order conversion
    uint32_t host_val = 0xDEADBEEF;
    uint32_t net_val  = host_to_be32(host_val);
    uint32_t back     = be32_to_host(net_val);
    printf("\nhost_to_be32(0x%08X) = 0x%08X\n", host_val, net_val);
    printf("be32_to_host(0x%08X) = 0x%08X (roundtrip matches: %s)\n",
           net_val, back, back == host_val ? "YES" : "NO");

    // Struct serialization (protocol-safe)
    SensorFrame tx = { .id = 0x0042, .value = 0x00ABCDEF };
    uint8_t buf[6];
    serialize_sensor_frame(&tx, buf);

    printf("\nSerialized bytes: ");
    for (int i = 0; i < 6; i++) printf("0x%02X ", buf[i]);
    printf("\n");
    // On any endianness: 0x00 0x42 0x00 0xAB 0xCD 0xEF

    SensorFrame rx = {0};
    deserialize_sensor_frame(buf, &rx);
    printf("Deserialized: id=0x%04X value=0x%08X  (expect id=0x0042 val=0x00ABCDEF)\n",
           rx.id, rx.value);

    return 0;
}
