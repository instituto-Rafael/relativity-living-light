#include "rll_canonical_real.h"

static int rll_bad(double x) { return !(x == x) || x < 0.0 || x > 1.0e12; }
static double rll_abs_test(double x) { return x < 0.0 ? -x : x; }
static int rll_near(double a, double b, double tolerance) { return rll_abs_test(a - b) <= tolerance; }

int rll_canonical_real_selftest(void) {
    rll_cosmo_params rll = rll_params_fase18e_map();
    rll_cosmo_params lcdm = rll_params_fase18e_lcdm();
    rll_canonical_result a = rll_run_canonical_real(&rll, RLL_MODEL_LOGISTIC);
    rll_canonical_result b = rll_run_canonical_real(&lcdm, RLL_MODEL_LCDM);
    if (rll_canonical_source_count != 4u) return 10;
    if (a.n_hz != 33u || a.n_growth != 16u || a.n_bao != 13u || a.n_cmb != 3u) return 11;
    if (a.status != RLL_RUN_OK || b.status != RLL_RUN_OK) return 12;
    if (a.claim_allowed != 0u || b.claim_allowed != 0u) return 13;
    if (rll_bad(a.chi2_hz) || rll_bad(a.chi2_growth) || rll_bad(a.chi2_bao) || rll_bad(a.chi2_cmb) || rll_bad(a.chi2_total)) return 14;
    if (rll_bad(b.chi2_hz) || rll_bad(b.chi2_growth) || rll_bad(b.chi2_bao) || rll_bad(b.chi2_cmb) || rll_bad(b.chi2_total)) return 15;
    if (!rll_near(a.chi2_hz, 23.96968192673179, 2.0e-4)) return 20;
    if (!rll_near(a.chi2_bao, 21.78806427901191, 2.0e-4)) return 21;
    if (!rll_near(a.chi2_cmb, 0.7616672954080195, 2.0e-4)) return 22;
    if (!rll_near(a.chi2_total, a.chi2_hz + a.chi2_growth + a.chi2_bao + a.chi2_cmb, 1.0e-10)) return 23;
    if (!rll_near(b.chi2_total, b.chi2_hz + b.chi2_growth + b.chi2_bao + b.chi2_cmb, 1.0e-10)) return 24;
    return 0;
}

#if defined(RLL_FREESTANDING_ENTRY)
__attribute__((noreturn)) void _start(void) {
    rll_i64 code = (rll_i64)rll_canonical_real_selftest();
#if defined(__linux__) && defined(__x86_64__)
    __asm__ volatile("syscall" : : "a"(60ull), "D"((rll_u64)code) : "rcx", "r11", "memory");
#elif defined(__linux__) && defined(__aarch64__)
    register rll_u64 x0 __asm__("x0") = (rll_u64)code;
    register rll_u64 x8 __asm__("x8") = 93ull;
    __asm__ volatile("svc 0" : : "r"(x0), "r"(x8) : "memory");
#elif defined(__linux__) && defined(__arm__)
    register rll_u32 r0 __asm__("r0") = (rll_u32)code;
    register rll_u32 r7 __asm__("r7") = 1u;
    __asm__ volatile("svc 0" : : "r"(r0), "r"(r7) : "memory");
#else
    (void)code;
#endif
    for (;;) { __asm__ volatile("" : : : "memory"); }
}
#else
int main(void) { return rll_canonical_real_selftest(); }
#endif
