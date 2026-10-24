/* RAFAELIA / RLL formal integer geometric diagnostic, 2026-10-24.
 * New bounded freestanding u32 implementation, independent of the Python oracle.
 * No heap, syscalls, libc, floating point, physics adapter or external runtime.
 * NOT a fixed-time algorithm: bounded fixed-width loops and bitwise arithmetic.
 * SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM; claim_allowed=false.
 */
#include "rll_quantized_orbit_u32.h"

_Static_assert(sizeof(rll_q_u32) == 4, "requires 32-bit unsigned int");
_Static_assert(sizeof(rll_q_u64) == 8, "requires 64-bit unsigned long long");

static rll_q_u64 rll_q_isqrt64(rll_q_u64 number) {
    rll_q_u64 result = 0ULL;
    rll_q_u64 bit = 1ULL << 62;
    while (bit > number) bit >>= 2;
    while (bit != 0ULL) {
        const rll_q_u64 candidate = result + bit;
        if (number >= candidate) {
            number -= candidate;
            result = (result >> 1) + bit;
        } else {
            result >>= 1;
        }
        bit >>= 2;
    }
    return result;
}

static rll_q_u32 rll_q_binary_gcd(rll_q_u32 a, rll_q_u32 b) {
    rll_q_u32 shifts = 0u;
    if (a == 0u) return b;
    if (b == 0u) return a;
    while (((a | b) & 1u) == 0u) {
        a >>= 1; b >>= 1; ++shifts;
    }
    while ((a & 1u) == 0u) a >>= 1;
    do {
        while ((b & 1u) == 0u) b >>= 1;
        if (a > b) { const rll_q_u32 tmp = a; a = b; b = tmp; }
        b -= a;
    } while (b != 0u);
    return a << shifts;
}

/* Software binary divide: avoid EABI runtime division libcall on ARM32. */
static rll_q_u32 rll_q_div_u32(rll_q_u32 dividend, rll_q_u32 divisor) {
    rll_q_u32 quotient = 0u;
    rll_q_u64 remainder = 0ULL;
    rll_q_u32 bit = 32u;
    while (bit != 0u) {
        --bit;
        remainder = (remainder << 1) | ((dividend >> bit) & 1u);
        if (remainder >= (rll_q_u64)divisor) {
            remainder -= (rll_q_u64)divisor;
            quotient |= (rll_q_u32)1u << bit;
        }
    }
    return quotient;
}

rll_q_orbit_result rll_q_orbit_u32(rll_q_u32 base, rll_q_u32 exponent) {
    rll_q_orbit_result out = {0};
    out.status = RLL_Q_INVALID_INPUT;
    out.base = base;
    out.exponent = exponent;
    /* Unknown is typed, never converted to a geometry zero. */
    if (base == 0u) return out;
    if (exponent > 63u) { out.status = RLL_Q_UNREPRESENTABLE; return out; }

    const rll_q_u32 half = exponent >> 1;
    rll_q_u64 num = (rll_q_u64)base;
    rll_q_u32 i = 0u;
    while (i < half) {
        if (num > 6148914691236517205ULL) {
            out.status = RLL_Q_UNREPRESENTABLE; return out;
        }
        num *= 3ULL;
        ++i;
    }

    rll_q_u64 step64;
    if ((exponent & 1u) != 0u) {
        /* Guard 3*num*num against overflow before exact integer sqrt. */
        if (num > 2479700524ULL) {
            out.status = RLL_Q_UNREPRESENTABLE; return out;
        }
        step64 = rll_q_isqrt64(3ULL * num * num) >> (2u * half + 1u);
        out.boundary_integer = 0u; /* irrational for nonzero integer base */
    } else {
        step64 = num >> (2u * half); /* division by 4^half, exactly */
        if ((2u * half) < 32u)
            out.boundary_integer = (base & ((1u << (2u * half)) - 1u)) == 0u;
        else
            out.boundary_integer = 0u;
    }
    if (step64 > (rll_q_u64)base) {
        out.status = RLL_Q_UNREPRESENTABLE; return out;
    }
    out.exact_step = (rll_q_u32)step64;
    out.cycles = rll_q_binary_gcd(base, out.exact_step);
    out.vertices_per_cycle = rll_q_div_u32(base, out.cycles);
    out.permutation_sign = ((base - out.cycles) & 1u) != 0u ? -1 : 1;
    out.status = RLL_Q_OK;
    return out;
}
