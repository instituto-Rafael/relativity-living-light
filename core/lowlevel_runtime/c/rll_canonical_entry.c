#include "rll_canonical_freestanding.h"

#if defined(__GNUC__) || defined(__clang__)
#define RLLC_NORETURN __attribute__((noreturn))
#else
#define RLLC_NORETURN
#endif

rllc_i64 rllc_raw_write_stdout(const void *buf, rllc_u64 len) {
    if ((buf == (const void *)0) && (len != 0ull)) {
        return -22ll;
    }

#if defined(__linux__) && defined(__x86_64__)
    rllc_i64 ret;
    __asm__ volatile(
        "syscall"
        : "=a"(ret)
        : "a"(1ull), "D"(1ull), "S"(buf), "d"(len)
        : "rcx", "r11", "memory"
    );
    return ret;
#elif defined(__linux__) && defined(__aarch64__)
    register rllc_u64 x0 __asm__("x0") = 1ull;
    register rllc_u64 x1 __asm__("x1") = (rllc_u64)buf;
    register rllc_u64 x2 __asm__("x2") = len;
    register rllc_u64 x8 __asm__("x8") = 64ull;
    __asm__ volatile(
        "svc 0"
        : "+r"(x0)
        : "r"(x1), "r"(x2), "r"(x8)
        : "memory"
    );
    return (rllc_i64)x0;
#elif defined(__linux__) && defined(__arm__)
    register rllc_u32 r0 __asm__("r0") = 1u;
    register rllc_u32 r1 __asm__("r1") = (rllc_u32)(rllc_u64)buf;
    register rllc_u32 r2 __asm__("r2") = (rllc_u32)len;
    register rllc_u32 r7 __asm__("r7") = 4u;
    __asm__ volatile(
        "svc 0"
        : "+r"(r0)
        : "r"(r1), "r"(r2), "r"(r7)
        : "memory"
    );
    return (rllc_i64)(rllc_i32)r0;
#elif defined(__linux__) && defined(__riscv) && (__riscv_xlen == 64)
    register rllc_u64 a0 __asm__("a0") = 1ull;
    register rllc_u64 a1 __asm__("a1") = (rllc_u64)buf;
    register rllc_u64 a2 __asm__("a2") = len;
    register rllc_u64 a7 __asm__("a7") = 64ull;
    __asm__ volatile(
        "ecall"
        : "+r"(a0)
        : "r"(a1), "r"(a2), "r"(a7)
        : "memory"
    );
    return (rllc_i64)a0;
#else
    (void)buf;
    (void)len;
    return -38ll;
#endif
}

RLLC_NORETURN void rllc_raw_exit(rllc_i32 status) {
#if defined(__linux__) && defined(__x86_64__)
    __asm__ volatile(
        "syscall"
        :
        : "a"(60ull), "D"((rllc_u64)(rllc_u32)status)
        : "rcx", "r11", "memory"
    );
#elif defined(__linux__) && defined(__aarch64__)
    register rllc_u64 x0 __asm__("x0") = (rllc_u64)(rllc_u32)status;
    register rllc_u64 x8 __asm__("x8") = 93ull;
    __asm__ volatile("svc 0" : : "r"(x0), "r"(x8) : "memory");
#elif defined(__linux__) && defined(__arm__)
    register rllc_u32 r0 __asm__("r0") = (rllc_u32)status;
    register rllc_u32 r7 __asm__("r7") = 1u;
    __asm__ volatile("svc 0" : : "r"(r0), "r"(r7) : "memory");
#elif defined(__linux__) && defined(__riscv) && (__riscv_xlen == 64)
    register rllc_u64 a0 __asm__("a0") = (rllc_u64)(rllc_u32)status;
    register rllc_u64 a7 __asm__("a7") = 93ull;
    __asm__ volatile("ecall" : : "r"(a0), "r"(a7) : "memory");
#else
    (void)status;
#endif

    for (;;) {
#if defined(__GNUC__) || defined(__clang__)
        __asm__ volatile("" : : : "memory");
#endif
    }
}

RLLC_NORETURN void _start(void) {
    static rllc_phase20_params_q16 params;
    static rllc_receipt_v1 receipt;
    static char line[512];
    rllc_u32 length;
    rllc_i64 written;

    rllc_phase20_default_params(&params);
    rllc_evaluate_canonical_hz(
        rllc_hz_canonical_data,
        RLLC_CANONICAL_ROW_COUNT,
        &params,
        &receipt
    );

    length = rllc_format_receipt_line(&receipt, line, (rllc_u32)sizeof(line));
    written = rllc_raw_write_stdout(line, (rllc_u64)length);

    if ((written < 0ll) || ((rllc_u64)written != (rllc_u64)length)) {
        rllc_raw_exit(3);
    }
    if ((receipt.valid_count != RLLC_CANONICAL_ROW_COUNT) ||
        (receipt.numeric_flags != 0u)) {
        rllc_raw_exit(2);
    }
    rllc_raw_exit(0);
}
