typedef unsigned long long rll_u64;

extern rll_u64 rll_saved_ms(rll_u64 baseline_ms, rll_u64 current_ms);
extern rll_u64 rll_gain_permille(rll_u64 baseline_ms, rll_u64 current_ms);
extern rll_u64 rll_throughput_milli_per_second(rll_u64 completed_count, rll_u64 duration_ms);
extern rll_u64 rll_energy_millijoule(rll_u64 measured_average_power_mw, rll_u64 duration_ms);

#define RLL_INVALID_U64 (~(rll_u64)0)

int main(void)
{
    if (rll_saved_ms(301403ULL, 34583ULL) != 266820ULL) {
        return 1;
    }
    if (rll_gain_permille(301403ULL, 34583ULL) != 885ULL) {
        return 2;
    }
    if (rll_throughput_milli_per_second(1727ULL, 285030ULL) != 6059ULL) {
        return 3;
    }
    if (rll_energy_millijoule(100000ULL, 34583ULL) != 3458300ULL) {
        return 4;
    }
    if (rll_gain_permille(0ULL, 1ULL) != RLL_INVALID_U64) {
        return 5;
    }
    if (rll_throughput_milli_per_second(1ULL, 0ULL) != RLL_INVALID_U64) {
        return 6;
    }
    return 0;
}
