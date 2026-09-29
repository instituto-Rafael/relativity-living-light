/*
 * RLL non-null recovery Q16.16 — standalone freestanding consumer.
 *
 * Reads one canonical fixture from stdin, scans the frozen manifold, and emits
 * only the recovered coordinates. It does not contain an injection label,
 * expected result, success comparison, generator mode, RNG, optimizer or MCMC.
 *
 * No headers, libc, heap, malloc, GC, structs, classes, parser or filesystem.
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

#define OSN 22u
#define ZTN 9u
#define WTN 9u

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

static const i32 ZT[ZTN] = {
    39322,45875,52429,58982,65536,72090,78643,85197,91750
};

static const i32 WT[WTN] = {
    13107,14746,16384,18022,19661,21299,22938,24576,26214
};

static u8 IN[FIXTURE_BYTES];
static i32 Y[N];
static i32 B[6];
static char OUT[256];

static u32 au32(i32 v)
{
    u32 x = (u32)v;
    u32 m = (u32)(v >> 31);
    return (x ^ m) - m;
}

static u64 udiv6432(u64 n, u32 d, u32 *rr)
{
    u64 q = 0ull;
    u64 r = 0ull;
    i32 b = 63;

    if (d == 0u) {
        if (rr != (u32 *)0) {
            *rr = 0u;
        }
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

    if (rr != (u32 *)0) {
        *rr = (u32)r;
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
    q = udiv6432(n, d, (u32 *)0);

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
    q = udiv6432((u64)n, d, (u32 *)0);

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

static i32 os_at(u32 i)
{
    if (i == 0u) {
        return 0;
    }
    return 1 + (i32)(i - 1u) * 131;
}

static u32 get32(u32 p)
{
    return ((u32)IN[p + 0u]) |
           ((u32)IN[p + 1u] << 8u) |
           ((u32)IN[p + 2u] << 16u) |
           ((u32)IN[p + 3u] << 24u);
}

#if defined(__x86_64__)

static i64 rd(void *b, u64 n)
{
    register u64 a __asm__("rax") = 0ull;
    register u64 d __asm__("rdi") = 0ull;
    register void *s __asm__("rsi") = b;
    register u64 c __asm__("rdx") = n;

    __asm__ volatile(
        "syscall"
        : "+a"(a)
        : "D"(d), "S"(s), "d"(c)
        : "rcx", "r11", "memory"
    );

    return (i64)a;
}

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

static i64 rd(void *b, u64 n)
{
    register u32 r0 __asm__("r0") = 0u;
    register void *r1 __asm__("r1") = b;
    register u32 r2 __asm__("r2") = (u32)n;
    register u32 r7 __asm__("r7") = 3u;

    __asm__ volatile(
        "svc 0"
        : "+r"(r0)
        : "r"(r1), "r"(r2), "r"(r7)
        : "memory"
    );

    return (i64)(i32)r0;
}

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

static u32 read_all(u8 *p, u32 n)
{
    u32 o = 0u;

    while (o < n) {
        i64 r = rd(p + o, (u64)(n - o));

        if (r <= 0) {
            return 0u;
        }

        o += (u32)r;
    }

    return 1u;
}

static u32 write_all(const char *p, u32 n)
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

static u64 score(i32 os, i32 zt, i32 wt)
{
    u32 i = 0u;
    u64 c = 0ull;

    while (i < N) {
        i32 p = model(D[i * DSTRIDE + DZ], os, zt, wt);
        i32 residual = sat((i64)Y[i] - (i64)p);
        i32 n = qdiv(residual, D[i * DSTRIDE + DS]);
        i32 t = qmul(n, n);

        if (t < 0) {
            return ~0ull;
        }

        c += (u64)(u32)t;
        i++;
    }

    return c;
}

static void scan(void)
{
    u32 oi = 0u;
    u32 zi;
    u32 wi;
    u64 best = ~0ull;
    u32 evals = 0u;

    B[0] = 0;
    B[1] = 0;
    B[2] = 0;
    B[3] = 0;
    B[4] = 0;
    B[5] = 0;

    while (oi < OSN) {
        i32 os = os_at(oi);
        zi = 0u;

        while (zi < ZTN) {
            wi = 0u;

            while (wi < WTN) {
                u64 c = score(os, ZT[zi], WT[wi]);
                evals++;

                if (c < best) {
                    best = c;
                    B[0] = os;
                    B[1] = ZT[zi];
                    B[2] = WT[wi];
                    B[3] = (i32)(u32)best;
                    B[4] = (i32)(u32)(best >> 32u);
                }

                wi++;
            }

            zi++;
        }

        oi++;
    }

    B[5] = (i32)evals;
}

static u32 ac(u32 p, char c)
{
    if (p < (u32)sizeof(OUT)) {
        OUT[p] = c;
    }
    return p + 1u;
}

static u32 at(u32 p, const char *s)
{
    u32 i = 0u;

    while (s[i] != '\0') {
        p = ac(p, s[i]);
        i++;
    }

    return p;
}

static u32 au(u32 p, u64 v)
{
    char r[24];
    u32 n = 0u;

    if (v == 0ull) {
        return ac(p, '0');
    }

    while (v != 0ull) {
        u32 m = 0u;
        v = udiv6432(v, 10u, &m);
        r[n] = (char)('0' + m);
        n++;
    }

    while (n != 0u) {
        n--;
        p = ac(p, r[n]);
    }

    return p;
}

static u32 ai(u32 p, i32 v)
{
    if (v < 0) {
        p = ac(p, '-');
        return au(p, (u64)au32(v));
    }
    return au(p, (u64)(u32)v);
}

void _start(void)
{
    u32 i;
    u32 p = 0u;
    u64 best;

    if (read_all(IN, FIXTURE_BYTES) == 0u) {
        ex(70);
    }

    if ((IN[0] != (u8)'R') ||
        (IN[1] != (u8)'L') ||
        (IN[2] != (u8)'F') ||
        (IN[3] != (u8)'1') ||
        (get32(4u) != 1u) ||
        (get32(8u) != N)) {
        ex(71);
    }

    i = 0u;
    while (i < N) {
        Y[i] = (i32)get32(12u + i * 4u);
        i++;
    }

    scan();

    best = ((u64)(u32)B[4] << 32u) | (u64)(u32)B[3];

    p = at(p, "RLLREC1 state=PASS best=");
    p = ai(p, B[0]);
    p = ac(p, ',');
    p = ai(p, B[1]);
    p = ac(p, ',');
    p = ai(p, B[2]);
    p = at(p, " score_q16=");
    p = au(p, best);
    p = at(p, " grid_evals=");
    p = ai(p, B[5]);
    p = at(p, " claim_allowed=0\n");

    if (p > (u32)sizeof(OUT)) {
        p = (u32)sizeof(OUT);
    }

    ex(write_all(OUT, p) != 0u ? 0 : 72);
}
