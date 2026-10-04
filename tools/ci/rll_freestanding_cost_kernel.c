/* RLL freestanding cost kernel v1.
 *
 * Contract:
 * - C11 freestanding translation unit;
 * - no headers, libc, heap, I/O, syscalls, floating point, or globals with runtime init;
 * - integer-only arithmetic;
 * - energy is computed only when measured average power is supplied by the caller.
 */

typedef unsigned long long rll_u64;

#define RLL_INVALID_U64 (~(rll_u64)0)
#define RLL_MAX_DURATION_MS ((rll_u64)604800000) /* 7 days */
#define RLL_MAX_COUNT ((rll_u64)1000000000)
#define RLL_MAX_POWER_MW ((rll_u64)1000000000) /* 1 MW */

rll_u64 rll_saved_ms(rll_u64 baseline_ms, rll_u64 current_ms)
{
    if (baseline_ms > RLL_MAX_DURATION_MS || current_ms > RLL_MAX_DURATION_MS) {
        return RLL_INVALID_U64;
    }
    if (current_ms >= baseline_ms) {
        return 0;
    }
    return baseline_ms - current_ms;
}

rll_u64 rll_gain_permille(rll_u64 baseline_ms, rll_u64 current_ms)
{
    rll_u64 saved;

    if (baseline_ms == 0 || baseline_ms > RLL_MAX_DURATION_MS || current_ms > RLL_MAX_DURATION_MS) {
        return RLL_INVALID_U64;
    }

    saved = rll_saved_ms(baseline_ms, current_ms);
    if (saved == RLL_INVALID_U64) {
        return RLL_INVALID_U64;
    }

    return (saved * 1000ULL) / baseline_ms;
}

rll_u64 rll_throughput_milli_per_second(rll_u64 completed_count, rll_u64 duration_ms)
{
    if (completed_count > RLL_MAX_COUNT || duration_ms == 0 || duration_ms > RLL_MAX_DURATION_MS) {
        return RLL_INVALID_U64;
    }

    return (completed_count * 1000000ULL) / duration_ms;
}

rll_u64 rll_energy_millijoule(rll_u64 measured_average_power_mw, rll_u64 duration_ms)
{
    if (measured_average_power_mw > RLL_MAX_POWER_MW || duration_ms > RLL_MAX_DURATION_MS) {
        return RLL_INVALID_U64;
    }

    return (measured_average_power_mw * duration_ms) / 1000ULL;
}
