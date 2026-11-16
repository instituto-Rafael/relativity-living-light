/*
 * RLL non-null fixture generator Q16.16 — standalone freestanding producer.
 *
 * No headers, libc, heap, malloc, GC, structs, classes, parser or filesystem.
 * Output is one canonical little-endian binary fixture on stdout.
 *
 * GEN_MODE:
 *   0 exact non-null
 *   1 deterministic stress
 *   2 exact null
 */

typedef unsigned char      u8;
typedef unsigned int       u32;
typedef signed int         i32;
typedef unsigned long long u64;
typedef signed long long   i64;

#define Q16_ONE 65536
#define I32_MAX 2147483647
#define I32_MIN (-2147483647 - 1)
#define N 33u
#define DSTRIDE 2u
#define DZ 0u
#define DS 1u

#ifndef GEN_MODE
#define GEN_MODE 0
#endif

#define INJ_OS 1311
#define INJ_ZT 65536
#define INJ_WT 19661
#define H0_Q16 4417126
#define OM_Q16 20644
#define LN2_Q16 45426
#define EXP_LIMIT_Q16 (10 * Q16_ONE)
#define FIXTURE_BYTES (12u + N * 4u)

static const i32 D[N * DSTRIDE] = {
    4588,1284506, 5898,786432, 7864,1717043, 11141,524288,
    11731,262144, 13042,327680, 13107,1939866, 17695,917504,
    18350,2398618, 23069,917504, 24904,884736, 26214,1114112,
    28836,511181, 31457,4063232, 33423,124518, 37356,222822,
    38863,851968, 39322,399770, 39977,137626, 44564,524288,
    47841,458752, 51184,786432, 57344,1114112, 57672,2621440,
    58982,1507328, 67961,1310720, 85197,1114112, 89326,2202010,
    93716,1179648, 100270,917504, 114688,2621440, 128778,3303014,
    153354,458752
};

#if GEN_MODE == 1
static const i32 NOISE[N] = {
    -2,-1,0,1,2,-2,-1,0,1,2,-2,-1,0,1,2,-2,-1,
    0,1,2,-2,-1,0,1,2,-2,-1,0,1,2,-2,-1,0
};
#endif

static u8 O[FIXTURE_BYTES];

static u32 au32(i32 v)
{
    u32 x = (u32)v;
    u32 m = (u32)(v >> 31);
    return (x ^ m) - m;
}

static u64 udiv6432(u64 n, u32 d)
{
    u64 q = 0ull;
    u64 r = 0ull;
    i32 b = 63;

    if (d == 0u) {
        return ~0ull;
    }

    while (b >= 0) {
        r = (r << 1u) | ((n >> (u32)b) & 1ull);
        if (r >= (u64)d) {
            r -= (u64)d;
            q |= 1ull << (u32)b;
        }
        b--;
    }

    return q;
}

static i32 sat(i64 v)
{
    if (v > (i64)I32_MAX) {
        return I32_MAX;
    }
    if (v < (i64)I32_MIN) {
        return I32_MIN;
    }
    return (i32)v;
}

static i32 qmul(i32 a, i32 b)
{
    return sat(((i64)a * (i64)b) >> 16u);
}

static i32 qdiv(i32 a, i32 b)
{
    u32 s;
    u64 n;
    u32 d;
    u64 q;

    if (b == 0) {
        return (a < 0) ? I32_MIN : I32_MAX;
    }

    s = (u32)((a ^ b) >> 31);
    n = ((u64)au32(a)) << 16u;
    d = au32(b);
    q = udiv6432(n, d);

    if (q > 2147483648ull) {
        return (s != 0u) ? I32_MIN : I32_MAX;
    }

    if (s != 0u) {
        if (q == 2147483648ull) {
            return I32_MIN;
        }
        return -(i32)q;
    }

    return (q > 2147483647ull) ? I32_MAX : (i32)q;
}

static i32 divi(i32 a, i32 b)
{
    u32 s;
    u32 n;
    u32 d;
    u64 q;

    if (b == 0) {
        return (a < 0) ? I32_MIN : I32_MAX;
    }

    s = (u32)((a ^ b) >> 31);
    n = au32(a);
    d = au32(b);
    q = udiv6432((u64)n, d);

    if (s != 0u) {
        if (q == 2147483648ull) {
            return I32_MIN;
        }
        return -(i32)q;
    }

    return (q > 2147483647ull) ? I32_MAX : (i32)q;
}

static u64 isqrt(u64 x)
{
    u64 r = 0ull;
    u64 b = 1ull << 62u;

    while (b > x) {
        b >>= 2u;
    }

    while (b != 0ull) {
        if (x >= r + b) {
            x -= r + b;
            r = (r >> 1u) + b;
        } else {
            r >>= 1u;
        }
        b >>= 2u;
    }

    return r;
}

static i32 qsqrt(i32 x)
{
    u64 r;

    if (x <= 0) {
        return 0;
    }

    r = isqrt(((u64)(u32)x) << 16u);
    return (r > (u64)I32_MAX) ? I32_MAX : (i32)r;
}

static i32 qexp(i32 x)
{
    i32 k;
    i32 r;
    i32 t;
    i32 s;
    i32 n;

    if (x <= -EXP_LIMIT_Q16) {
        return 3;
    }
    if (x >= EXP_LIMIT_Q16) {
        return 1443549184;
    }

    k = divi(x, LN2_Q16);
    r = x - k * LN2_Q16;
    t = Q16_ONE;
    s = Q16_ONE;
    n = 1;

    while (n <= 6) {
        t = qmul(t, r);
        t = divi(t, n);
        s = sat((i64)s + (i64)t);
        n++;
    }

    if (k > 0) {
        if (k >= 15) {
            return I32_MAX;
        }
        return sat(((i64)s) << (u32)k);
    }

    if (k < 0) {
        i32 sh = -k;
        if (sh >= 31) {
            return 0;
        }
        return s >> (u32)sh;
    }

    return s;
}

static i32 model(i32 z, i32 os, i32 zt, i32 wt)
{
    i32 a;
    i32 a2;
    i32 a3;
    i32 f;
    i32 ol;
    i32 sec;
    i32 e2;

    if ((wt <= 0) || (z < 0)) {
        return 0;
    }

    a = sat((i64)Q16_ONE + (i64)z);
    a2 = qmul(a, a);
    a3 = qmul(a2, a);

    f = qdiv(
        Q16_ONE,
        sat((i64)Q16_ONE + (i64)qexp(qdiv(z - zt, wt)))
    );

    ol = Q16_ONE - OM_Q16 - os;
    sec = f + qmul(Q16_ONE - f, a3);
    e2 = qmul(OM_Q16, a3) + ol + qmul(os, sec);

    return qmul(H0_Q16, qsqrt(e2));
}

static void put32(u32 p, u32 v)
{
    O[p + 0u] = (u8)(v & 255u);
    O[p + 1u] = (u8)((v >> 8u) & 255u);
    O[p + 2u] = (u8)((v >> 16u) & 255u);
    O[p + 3u] = (u8)((v >> 24u) & 255u);
}

#if defined(__x86_64__)

static i64 wr(const void *b, u64 n)
{
    register u64 a __asm__("rax") = 1ull;
    register u64 d __asm__("rdi") = 1ull;
    register const void *s __asm__("rsi") = b;
    register u64 c __asm__("rdx") = n;

    __asm__ volatile(
        "syscall"
        : "+a"(a)
        : "D"(d), "S"(s), "d"(c)
        : "rcx", "r11", "memory"
    );

    return (i64)a;
}

static void ex(i32 x)
{
    register u64 a __asm__("rax") = 60ull;
    register u64 d __asm__("rdi") = (u32)x;

    __asm__ volatile(
        "syscall"
        :
        : "a"(a), "D"(d)
        : "rcx", "r11", "memory"
    );

    for (;;) {
    }
}

#elif defined(__arm__)

static i64 wr(const void *b, u64 n)
{
    register u32 r0 __asm__("r0") = 1u;
    register const void *r1 __asm__("r1") = b;
    register u32 r2 __asm__("r2") = (u32)n;
    register u32 r7 __asm__("r7") = 4u;

    __asm__ volatile(
        "svc 0"
        : "+r"(r0)
        : "r"(r1), "r"(r2), "r"(r7)
        : "memory"
    );

    return (i64)(i32)r0;
}

static void ex(i32 x)
{
    register u32 r0 __asm__("r0") = (u32)x;
    register u32 r7 __asm__("r7") = 1u;

    __asm__ volatile(
        "svc 0"
        :
        : "r"(r0), "r"(r7)
        : "memory"
    );

    for (;;) {
    }
}

#else
#error unsupported_architecture
#endif

static u32 write_all(const u8 *p, u32 n)
{
    u32 o = 0u;

    while (o < n) {
        i64 r = wr(p + o, (u64)(n - o));

        if (r <= 0) {
            return 0u;
        }

        o += (u32)r;
    }

    return 1u;
}

void _start(void)
{
    u32 i = 0u;
    i32 os = INJ_OS;

#if GEN_MODE == 2
    os = 0;
#endif

    O[0] = (u8)'R';
    O[1] = (u8)'L';
    O[2] = (u8)'F';
    O[3] = (u8)'1';
    put32(4u, 1u);
    put32(8u, N);

    while (i < N) {
        i32 h = model(D[i * DSTRIDE + DZ], os, INJ_ZT, INJ_WT);

#if GEN_MODE == 1
        {
            i32 s = D[i * DSTRIDE + DS];
            i32 c = NOISE[i];
            i32 a = (c < 0) ? -c : c;
            i32 d = (i32)(((i64)s * (i64)a) >> 5u);
            h = (c < 0) ? (h - d) : (h + d);
        }
#endif

        put32(12u + i * 4u, (u32)h);
        i++;
    }

    ex(write_all(O, FIXTURE_BYTES) != 0u ? 0 : 1);
}
