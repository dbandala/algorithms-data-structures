// ADC — resolution, LSB value, oversampling for extra bits, Nyquist
// Time complexity: O(N) for N-sample oversampling
// Space complexity: O(1)
//
// Compile: gcc -Wall -Wextra -std=c11 -lm -o out adc.c && ./out

#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <stdlib.h>

// ─── ADC Fundamentals ─────────────────────────────────────────────────────────
//
// ADC converts an analog voltage (0 → Vref) to an N-bit integer (0 → 2^N - 1).
//
// Resolution: N bits → 2^N levels
// LSB value:  Vref / 2^N   (the smallest distinguishable voltage step)
// Full-scale: Vref × (2^N - 1) / 2^N  ≈ Vref
//
// Nyquist theorem: to faithfully reconstruct a signal of frequency f_max,
//   sampling rate fs ≥ 2 × f_max
//   → Anti-aliasing filter: low-pass filter at fs/2 BEFORE the ADC input.

typedef struct {
    uint8_t  bits;       // ADC resolution in bits
    float    vref;       // reference voltage
} AdcConfig;

float adc_lsb_voltage(const AdcConfig *cfg) {
    return cfg->vref / (float)(1U << cfg->bits);
}

float adc_to_voltage(const AdcConfig *cfg, uint32_t raw) {
    return (float)raw * adc_lsb_voltage(cfg);
}

uint32_t voltage_to_adc(const AdcConfig *cfg, float voltage) {
    uint32_t full_scale = (1U << cfg->bits) - 1U;
    int32_t raw = (int32_t)(voltage / cfg->vref * (float)(1U << cfg->bits));
    if (raw < 0)                   return 0;
    if ((uint32_t)raw > full_scale) return full_scale;
    return (uint32_t)raw;
}

void print_adc_info(const AdcConfig *cfg) {
    printf("  Resolution:     %u bits → %u levels\n",
           cfg->bits, 1U << cfg->bits);
    printf("  LSB voltage:    %.4f mV (Vref=%.1fV)\n",
           adc_lsb_voltage(cfg) * 1000.0f, cfg->vref);
    printf("  Full-scale:     %.4fV\n",
           adc_to_voltage(cfg, (1U << cfg->bits) - 1U));
}

// ─── Oversampling — Gain Extra Bits ──────────────────────────────────────────
//
// To gain M extra bits of resolution:
//   Take 4^M samples and sum them.
//   Right-shift the sum by M bits (divide by 2^M to get 2^M × sum / 4^M = average scaled up).
//
// This works because noise "dithers" the LSB — the average reveals sub-LSB information.
// Requirement: signal must have enough noise to dither the ADC's LSB.

// Simulate N ADC samples with Gaussian noise (simple LCG + Box-Muller approximation)
static uint32_t g_rand_state = 12345;
static float sim_noise(float sigma) {
    // Simple 12-uniform approximation to Gaussian
    float sum = 0;
    for (int i = 0; i < 12; i++) {
        g_rand_state = g_rand_state * 1664525U + 1013904223U;
        sum += (float)(g_rand_state >> 17) / (float)(1 << 15);
    }
    return (sum - 6.0f) * sigma;
}

uint32_t oversample_and_decimate(const AdcConfig *base_cfg, float true_voltage,
                                  uint8_t extra_bits) {
    uint32_t num_samples = 1U << (2 * extra_bits);  // 4^extra_bits
    float    lsb         = adc_lsb_voltage(base_cfg);
    float    noise_sigma = lsb * 0.6f;  // realistic ADC noise ≈ 0.5–1 LSB

    uint64_t sum = 0;
    for (uint32_t i = 0; i < num_samples; i++) {
        float noisy = true_voltage + sim_noise(noise_sigma);
        sum += voltage_to_adc(base_cfg, noisy);
    }

    // Decimate: shift right by extra_bits to get (base_bits + extra_bits)-bit result
    return (uint32_t)(sum >> extra_bits);
}

float oversampled_to_voltage(const AdcConfig *base_cfg, uint32_t raw, uint8_t extra_bits) {
    uint8_t total_bits = base_cfg->bits + extra_bits;
    return (float)raw / (float)(1U << total_bits) * base_cfg->vref;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main(void) {
    printf("=== ADC Resolution and LSB ===\n\n");

    AdcConfig adc8  = {  8, 3.3f };
    AdcConfig adc12 = { 12, 3.3f };
    AdcConfig adc16 = { 16, 3.3f };

    printf("8-bit ADC (Vref=3.3V):\n");  print_adc_info(&adc8);
    printf("12-bit ADC (Vref=3.3V):\n"); print_adc_info(&adc12);
    printf("16-bit ADC (Vref=3.3V):\n"); print_adc_info(&adc16);

    printf("\n=== Voltage → ADC Raw → Back to Voltage (12-bit) ===\n");
    float test_voltages[] = {0.0f, 1.0f, 1.65f, 3.299f};
    for (int i = 0; i < 4; i++) {
        float v = test_voltages[i];
        uint32_t raw = voltage_to_adc(&adc12, v);
        float back   = adc_to_voltage(&adc12, raw);
        printf("  %.3fV → raw=%-4u → %.4fV  (error=%.4fmV)\n",
               v, raw, back, fabsf(v - back) * 1000.0f);
    }

    printf("\n=== Oversampling — Gaining Extra Bits ===\n");
    printf("Base: 12-bit ADC.  True signal: 1.000V\n\n");
    float true_v = 1.000f;
    for (uint8_t eb = 0; eb <= 4; eb++) {
        uint32_t num = 1U << (2 * eb);
        uint32_t os_raw = oversample_and_decimate(&adc12, true_v, eb);
        float    os_v   = oversampled_to_voltage(&adc12, os_raw, eb);
        float    lsb_mv = adc12.vref / (float)(1U << (adc12.bits + eb)) * 1000.0f;
        printf("  extra_bits=%u  samples=%4u  → %u-bit  LSB=%.4fmV  measured=%.4fV\n",
               eb, num, adc12.bits + eb, lsb_mv, os_v);
    }

    printf("\n=== Nyquist Sampling Rates ===\n");
    float signals_hz[] = {50, 1000, 20000, 100000};
    for (int i = 0; i < 4; i++) {
        printf("  f_signal=%.0f Hz → min fs=%.0f Hz (Nyquist)\n",
               signals_hz[i], 2.0f * signals_hz[i]);
    }

    return 0;
}
