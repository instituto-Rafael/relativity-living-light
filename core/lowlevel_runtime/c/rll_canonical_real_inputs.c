#include "rll_canonical_real_inputs.h"

#define RR_FNV_OFFSET 14695981039346656037ull
#define RR_FNV_PRIME 1099511628211ull
#define RR_CRC32_INIT 0xFFFFFFFFu
#define RR_CRC32_POLY_REV 0xEDB88320u
#define RR_CRC32_FINAL_XOR 0xFFFFFFFFu
#define RR_I64_MAX 0x7FFFFFFFFFFFFFFFll
#define RR_I64_MIN (-RR_I64_MAX - 1ll)
#define RR_MAX_FIELDS 16u
#define RR_MAX_DIGITS 15u

#define RR_FLAGS_BASE \
    (RLL_OBS_CALIBRATED | RLL_OBS_RAW_HASHED | \
     RLL_OBS_UNCERTAINTY_VALID | RLL_OBS_PREREGISTERED)

/* SHA-256 values pinned by data/real/cosmology/real_source_signatures.json. */
static const rll_u8 RR_SHA_HZ[32] = {
    0x11,0x94,0xfe,0x20,0x66,0xdc,0x3d,0x92,0xb4,0x87,0x0c,0xfb,0x03,0xd2,0xcd,0xbe,
    0x2a,0x31,0x6d,0xea,0xe2,0xe1,0x35,0x59,0x43,0xf7,0xf2,0xcc,0xca,0x6d,0x52,0xb6
};
static const rll_u8 RR_SHA_BAO[32] = {
    0x5a,0xb3,0x28,0x70,0x59,0x37,0xc6,0x9c,0xed,0xb6,0x62,0xbb,0xb3,0x58,0x88,0xdf,
    0x20,0xc6,0xca,0xbf,0x38,0x10,0xec,0x3c,0x5e,0x73,0x76,0xd6,0x9c,0xcb,0x0a,0x69
};
static const rll_u8 RR_SHA_FS8[32] = {
    0x37,0x81,0xa2,0xfa,0x7b,0xce,0x9e,0xa6,0x00,0x06,0x0f,0x9f,0xeb,0x6e,0x74,0xba,
    0x49,0xf4,0xba,0xa4,0xce,0x2e,0x73,0x44,0x80,0x32,0x95,0xc9,0x12,0x31,0x82,0x11
};
static const rll_u8 RR_SHA_CMB[32] = {
    0xe8,0x6d,0x99,0x61,0x31,0xcf,0x4b,0x37,0x58,0xf4,0xfe,0x03,0x19,0xb6,0xc7,0xda,
    0x75,0x2a,0x38,0xab,0x2f,0x14,0x1a,0xba,0xa8,0x1b,0xec,0x66,0xd8,0xe6,0xd9,0x79
};

static const rll_u32 RR_SHA_K[64] = {
    0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
    0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
    0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
    0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
    0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
    0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
    0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
    0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u
};

typedef struct rr_sha256 {
    rll_u32 h[8];
    rll_u8 block[64];
    rll_u64 bytes;
    rll_u32 used;
} rr_sha256;

typedef struct rr_slice {
    const rll_u8 *ptr;
    rll_u64 len;
} rr_slice;

typedef struct rr_context {
    rll_canonical_accumulator accumulator;
    rll_real_model_callback model_callback;
    void *model_context;
    rll_real_ingest_receipt *receipt;
} rr_context;

static rll_u32 rr_rotr(rll_u32 x, rll_u32 n) {
    return (x >> n) | (x << (32u - n));
}

static rll_u32 rr_load_be32(const rll_u8 *p) {
    return ((rll_u32)p[0] << 24u) | ((rll_u32)p[1] << 16u) |
           ((rll_u32)p[2] << 8u) | (rll_u32)p[3];
}

static void rr_store_be32(rll_u8 *p, rll_u32 v) {
    p[0] = (rll_u8)(v >> 24u);
    p[1] = (rll_u8)(v >> 16u);
    p[2] = (rll_u8)(v >> 8u);
    p[3] = (rll_u8)v;
}

static void rr_sha_transform(rr_sha256 *s, const rll_u8 block[64]) {
    rll_u32 w[64];
    rll_u32 a,b,c,d,e,f,g,h;
    rll_u32 i = 0u;
    while (i < 16u) {
        w[i] = rr_load_be32(block + (i * 4u));
        i++;
    }
    while (i < 64u) {
        rll_u32 s0 = rr_rotr(w[i-15u],7u) ^ rr_rotr(w[i-15u],18u) ^ (w[i-15u] >> 3u);
        rll_u32 s1 = rr_rotr(w[i-2u],17u) ^ rr_rotr(w[i-2u],19u) ^ (w[i-2u] >> 10u);
        w[i] = w[i-16u] + s0 + w[i-7u] + s1;
        i++;
    }
    a=s->h[0]; b=s->h[1]; c=s->h[2]; d=s->h[3];
    e=s->h[4]; f=s->h[5]; g=s->h[6]; h=s->h[7];
    i = 0u;
    while (i < 64u) {
        rll_u32 s1 = rr_rotr(e,6u) ^ rr_rotr(e,11u) ^ rr_rotr(e,25u);
        rll_u32 ch = (e & f) ^ ((~e) & g);
        rll_u32 t1 = h + s1 + ch + RR_SHA_K[i] + w[i];
        rll_u32 s0 = rr_rotr(a,2u) ^ rr_rotr(a,13u) ^ rr_rotr(a,22u);
        rll_u32 maj = (a & b) ^ (a & c) ^ (b & c);
        rll_u32 t2 = s0 + maj;
        h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
        i++;
    }
    s->h[0]+=a; s->h[1]+=b; s->h[2]+=c; s->h[3]+=d;
    s->h[4]+=e; s->h[5]+=f; s->h[6]+=g; s->h[7]+=h;
}

static void rr_sha_init(rr_sha256 *s) {
    s->h[0]=0x6a09e667u; s->h[1]=0xbb67ae85u; s->h[2]=0x3c6ef372u; s->h[3]=0xa54ff53au;
    s->h[4]=0x510e527fu; s->h[5]=0x9b05688cu; s->h[6]=0x1f83d9abu; s->h[7]=0x5be0cd19u;
    s->bytes=0ull; s->used=0u;
}

static void rr_sha_update(rr_sha256 *s, const rll_u8 *data, rll_u64 len) {
    rll_u64 i = 0ull;
    while (i < len) {
        s->block[s->used++] = data[i++];
        s->bytes++;
        if (s->used == 64u) {
            rr_sha_transform(s, s->block);
            s->used = 0u;
        }
    }
}

static void rr_sha_final(rr_sha256 *s, rll_u8 out[32]) {
    rll_u64 bits = s->bytes * 8ull;
    rll_u32 i;
    s->block[s->used++] = 0x80u;
    if (s->used > 56u) {
        while (s->used < 64u) s->block[s->used++] = 0u;
        rr_sha_transform(s, s->block);
        s->used = 0u;
    }
    while (s->used < 56u) s->block[s->used++] = 0u;
    i = 0u;
    while (i < 8u) {
        s->block[63u-i] = (rll_u8)(bits >> (i * 8u));
        i++;
    }
    rr_sha_transform(s, s->block);
    i = 0u;
    while (i < 8u) {
        rr_store_be32(out + (i * 4u), s->h[i]);
        i++;
    }
}

static int rr_equal(const rll_u8 *a, const rll_u8 *b, rll_u64 len) {
    rll_u8 diff = 0u;
    rll_u64 i = 0ull;
    while (i < len) { diff = (rll_u8)(diff | (rll_u8)(a[i] ^ b[i])); i++; }
    return diff == 0u;
}

static rll_u64 rr_fnv(const rll_u8 *data, rll_u64 len) {
    rll_u64 h = RR_FNV_OFFSET;
    rll_u64 i = 0ull;
    while (i < len) { h ^= (rll_u64)data[i++]; h *= RR_FNV_PRIME; }
    return h;
}

static rll_u32 rr_crc(const rll_u8 *data, rll_u64 len) {
    rll_u32 crc = RR_CRC32_INIT;
    rll_u64 i = 0ull;
    while (i < len) {
        rll_u32 x = (crc ^ (rll_u32)data[i++]) & 0xFFu;
        rll_u32 j = 0u;
        while (j < 8u) {
            rll_u32 mask = (rll_u32)(-(rll_i64)(x & 1u));
            x = (x >> 1u) ^ (RR_CRC32_POLY_REV & mask);
            j++;
        }
        crc = (crc >> 8u) ^ x;
    }
    return crc ^ RR_CRC32_FINAL_XOR;
}

static int rr_verify_sha(const rll_u8 *data, rll_u64 len, const rll_u8 expected[32]) {
    rr_sha256 state;
    rll_u8 actual[32];
    rr_sha_init(&state);
    rr_sha_update(&state, data, len);
    rr_sha_final(&state, actual);
    return rr_equal(actual, expected, 32ull);
}

static int rr_next_line(const rll_u8 *data, rll_u64 len, rll_u64 *cursor, rr_slice *line) {
    rll_u64 start, end;
    if (*cursor >= len) return 0;
    start = *cursor;
    end = start;
    while (end < len && data[end] != (rll_u8)'\n') end++;
    line->ptr = data + start;
    line->len = end - start;
    if (line->len && line->ptr[line->len-1ull] == (rll_u8)'\r') line->len--;
    *cursor = end < len ? end + 1ull : end;
    return 1;
}

static int rr_split(rr_slice line, rr_slice fields[RR_MAX_FIELDS], rll_u32 *count) {
    rll_u64 i = 0ull, start = 0ull;
    rll_u32 n = 0u;
    while (i <= line.len) {
        if (i < line.len && line.ptr[i] == (rll_u8)'"') return RLL_REAL_E_FORMAT;
        if (i == line.len || line.ptr[i] == (rll_u8)',') {
            if (n >= RR_MAX_FIELDS) return RLL_REAL_E_FORMAT;
            fields[n].ptr = line.ptr + start;
            fields[n].len = i - start;
            n++;
            start = i + 1ull;
        }
        i++;
    }
    *count = n;
    return RLL_REAL_OK;
}

static int rr_slice_eq(rr_slice s, const char *literal, rll_u64 n) {
    return s.len == n && rr_equal(s.ptr, (const rll_u8 *)literal, n);
}

static int rr_pow10(rll_u32 n, rll_u64 *out) {
    rll_u64 v = 1ull;
    while (n--) {
        if (v > 0xFFFFFFFFFFFFFFFFull / 10ull) return RLL_REAL_E_RANGE;
        v *= 10ull;
    }
    *out = v;
    return RLL_REAL_OK;
}

static int rr_parse_q16(const rll_u8 *text, rll_u64 len, rll_i64 *out) {
    rll_u64 i = 0ull, mantissa = 0ull, denom;
    rll_u32 digits = 0u, frac = 0u, dot = 0u, seen = 0u;
    rll_u32 neg = 0u, exp_seen = 0u, exp_neg = 0u, exp_digits = 0u;
    rll_i64 exp = 0ll;
    rll_u64 absolute;
    if (!text || !out || !len) return RLL_REAL_E_NULL;
    if (text[i] == (rll_u8)'-' || text[i] == (rll_u8)'+') { neg = text[i] == (rll_u8)'-'; i++; }
    while (i < len) {
        rll_u8 c = text[i];
        if (c >= (rll_u8)'0' && c <= (rll_u8)'9') {
            if (exp_seen) {
                if (exp_digits >= 3u) return RLL_REAL_E_RANGE;
                exp = exp * 10ll + (rll_i64)(c - (rll_u8)'0');
                exp_digits++;
            } else {
                if (digits >= RR_MAX_DIGITS) return RLL_REAL_E_RANGE;
                mantissa = mantissa * 10ull + (rll_u64)(c - (rll_u8)'0');
                digits++; seen = 1u; if (dot) frac++;
            }
        } else if (c == (rll_u8)'.' && !dot && !exp_seen) {
            dot = 1u;
        } else if ((c == (rll_u8)'e' || c == (rll_u8)'E') && seen && !exp_seen) {
            exp_seen = 1u;
            if (i+1ull < len && (text[i+1ull] == (rll_u8)'-' || text[i+1ull] == (rll_u8)'+')) {
                exp_neg = text[i+1ull] == (rll_u8)'-'; i++;
            }
        } else return RLL_REAL_E_FORMAT;
        i++;
    }
    if (!seen || (exp_seen && !exp_digits)) return RLL_REAL_E_FORMAT;
    if (exp_neg) exp = -exp;
    exp -= (rll_i64)frac;
    if (exp > 9ll || exp < -18ll) return RLL_REAL_E_RANGE;
    if (exp >= 0ll) {
        rll_u32 n = (rll_u32)exp;
        while (n--) {
            if (mantissa > 0x7FFFFFFFFFFFull / 10ull) return RLL_REAL_E_RANGE;
            mantissa *= 10ull;
        }
        if (mantissa > 0x7FFFFFFFFFFFull) return RLL_REAL_E_RANGE;
        absolute = mantissa << 16u;
    } else {
        rll_u64 integer, remainder, fraction;
        if (rr_pow10((rll_u32)(-exp), &denom) != RLL_REAL_OK) return RLL_REAL_E_RANGE;
        integer = mantissa / denom;
        remainder = mantissa % denom;
        if (integer > 0x7FFFFFFFFFFFull) return RLL_REAL_E_RANGE;
        fraction = ((remainder << 16u) + (denom >> 1u)) / denom;
        absolute = (integer << 16u) + fraction;
    }
    if (absolute > 0x7FFFFFFFFFFFFFFFull) return RLL_REAL_E_RANGE;
    *out = neg ? -(rll_i64)absolute : (rll_i64)absolute;
    return RLL_REAL_OK;
}

static void rr_digest_byte(rll_canonical_accumulator *a, rll_u8 byte) {
    rll_u32 x, j;
    a->receipt_fnv1a64 ^= (rll_u64)byte;
    a->receipt_fnv1a64 *= RR_FNV_PRIME;
    x = (a->receipt_crc32_state ^ (rll_u32)byte) & 0xFFu;
    j = 0u;
    while (j < 8u) {
        rll_u32 mask = (rll_u32)(-(rll_i64)(x & 1u));
        x = (x >> 1u) ^ (RR_CRC32_POLY_REV & mask);
        j++;
    }
    a->receipt_crc32_state = (a->receipt_crc32_state >> 8u) ^ x;
}

static void rr_digest_u32(rll_canonical_accumulator *a, rll_u32 v) {
    rll_u32 i=0u; while (i<4u) { rr_digest_byte(a,(rll_u8)(v>>(i*8u))); i++; }
}
static void rr_digest_u64(rll_canonical_accumulator *a, rll_u64 v) {
    rll_u32 i=0u; while (i<8u) { rr_digest_byte(a,(rll_u8)(v>>(i*8u))); i++; }
}
static void rr_digest_obs(rll_canonical_accumulator *a, const rll_canonical_observation *o, rll_u32 decision) {
    rr_digest_u32(a,o->domain); rr_digest_u32(a,o->quantity); rr_digest_u32(a,o->unit); rr_digest_u32(a,o->state);
    rr_digest_u64(a,(rll_u64)o->value_q16); rr_digest_u64(a,(rll_u64)o->model_q16); rr_digest_u64(a,(rll_u64)o->sigma_q16);
    rr_digest_u64(a,o->sample_count); rr_digest_u32(a,o->flags); rr_digest_u32(a,o->sequence_id);
    rr_digest_u64(a,o->source_fnv1a64); rr_digest_u32(a,o->source_crc32); rr_digest_u32(a,decision);
}

rll_u32 rll_canonical_expected_unit_extended(rll_u32 quantity) {
    if (quantity == RLL_Q_BAO_DM_RS || quantity == RLL_Q_BAO_DH_RS ||
        quantity == RLL_Q_CMB_SHIFT_R || quantity == RLL_Q_CMB_ACOUSTIC_SCALE ||
        quantity == RLL_Q_CMB_OMEGA_B_H2) return RLL_UNIT_DIMENSIONLESS;
    return rll_canonical_expected_unit(quantity);
}

static int rr_is_extended(rll_u32 q) {
    return q >= RLL_Q_BAO_DM_RS && q <= RLL_Q_CMB_OMEGA_B_H2;
}

static rll_i64 rr_chi_diag_q16(const rll_canonical_observation *o) {
    rll_i64 delta, ratio, abs_ratio;
    if (o->sigma_q16 <= 0ll) return RR_I64_MAX;
    delta = o->value_q16 - o->model_q16;
    if (delta > (RR_I64_MAX >> 16) || delta < (RR_I64_MIN >> 16)) return RR_I64_MAX;
    ratio = (delta << 16u) / o->sigma_q16;
    abs_ratio = ratio < 0ll ? -ratio : ratio;
    if (abs_ratio > 3037000499ll) return RR_I64_MAX;
    return (abs_ratio * abs_ratio) >> 16u;
}

rll_u32 rll_canonical_push_extended(rll_canonical_accumulator *a, const rll_canonical_observation *o) {
    rll_u32 decision;
    rll_i64 chi;
    rll_u32 required = RLL_OBS_CALIBRATED | RLL_OBS_RAW_HASHED |
                       RLL_OBS_UNCERTAINTY_VALID | RLL_OBS_MODEL_REGISTERED;
    if (!a || !o) return RLL_COUPLING_BLOCKED;
    if (!rr_is_extended(o->quantity)) return rll_canonical_push(a,o);
    decision = RLL_COUPLING_BLOCKED;
    if (a->target_region == RLL_REGION_COSMOLOGY_EVIDENCE &&
        o->domain == RLL_DOMAIN_COSMOLOGY && o->unit == RLL_UNIT_DIMENSIONLESS &&
        o->state == RLL_STATE_OBSERVED && o->sigma_q16 > 0ll &&
        o->sample_count && o->source_fnv1a64 && o->source_crc32 &&
        (o->flags & required) == required) decision = RLL_COUPLING_EVIDENCE;
    else if (o->state == RLL_STATE_TOKEN_VAZIO) decision = RLL_COUPLING_TOKEN_VAZIO;
    else if (o->state == RLL_STATE_SYNTHETIC) decision = RLL_COUPLING_SYNTHETIC_ONLY;
    a->total++;
    if (decision == RLL_COUPLING_EVIDENCE) {
        chi = rr_chi_diag_q16(o);
        a->evidence++; a->degrees_of_freedom++;
        if (chi == RR_I64_MAX || a->chi2_q16 > RR_I64_MAX-chi) a->chi2_q16 = RR_I64_MAX;
        else a->chi2_q16 += chi;
    } else if (decision == RLL_COUPLING_TOKEN_VAZIO) a->token_vazio++;
    else if (decision == RLL_COUPLING_SYNTHETIC_ONLY) a->synthetic_only++;
    else a->blocked++;
    rr_digest_obs(a,o,decision);
    return decision;
}

static int rr_bind_and_push(rr_context *ctx, rll_u32 dataset, rll_u32 quantity,
                            rll_u32 unit, rll_u32 seq, rll_i64 axis, rll_i64 value,
                            rll_i64 sigma, rll_u64 source_fnv, rll_u32 source_crc) {
    rll_real_model_request req;
    rll_canonical_observation o;
    rll_u32 model_state = RLL_REAL_MODEL_TOKEN_VAZIO;
    rll_i64 model = 0ll;
    o.domain=RLL_DOMAIN_COSMOLOGY; o.quantity=quantity; o.unit=unit; o.state=RLL_STATE_OBSERVED;
    o.value_q16=value; o.model_q16=0ll; o.sigma_q16=sigma; o.sample_count=1ull;
    o.flags=RR_FLAGS_BASE; o.sequence_id=seq; o.source_fnv1a64=source_fnv; o.source_crc32=source_crc;
    req.dataset_mask=dataset; req.quantity=quantity; req.sequence_id=seq; req.reserved=0u;
    req.axis_q16=axis; req.observed_q16=value; req.sigma_q16=sigma;
    if (ctx->model_callback) model_state=ctx->model_callback(ctx->model_context,&req,&model);
    if (model_state == RLL_REAL_MODEL_OK) {
        o.model_q16=model; o.flags |= RLL_OBS_MODEL_REGISTERED; ctx->receipt->model_bound_rows++;
    } else {
        ctx->receipt->model_token_vazio_rows++;
        if (model_state == RLL_REAL_MODEL_BLOCKED) o.state=RLL_STATE_BLOCKED;
    }
    (void)rll_canonical_push_extended(&ctx->accumulator,&o);
    ctx->receipt->parsed_rows++;
    return RLL_REAL_OK;
}

static int rr_parse_hz(rr_context *ctx, const rll_u8 *data, rll_u64 len) {
    rll_u64 cursor=0ull,row=0ull; rr_slice line;
    rll_u64 fnv=rr_fnv(data,len); rll_u32 crc=rr_crc(data,len);
    while (rr_next_line(data,len,&cursor,&line)) {
        rr_slice f[RR_MAX_FIELDS]; rll_u32 n=0u; rll_i64 z,v,s;
        if (!line.len) continue;
        if (row++==0ull) {
            if (!rr_slice_eq(line,"z,H_obs,sigma_H,source",22ull)) return RLL_REAL_E_SCHEMA;
            continue;
        }
        if (rr_split(line,f,&n)!=RLL_REAL_OK || n!=4u) return RLL_REAL_E_FORMAT;
        if (rr_parse_q16(f[0].ptr,f[0].len,&z)||rr_parse_q16(f[1].ptr,f[1].len,&v)||rr_parse_q16(f[2].ptr,f[2].len,&s)) return RLL_REAL_E_FORMAT;
        if (s<=0ll) return RLL_REAL_E_UNCERTAINTY;
        rr_bind_and_push(ctx,RLL_REAL_SOURCE_HZ,RLL_Q_HUBBLE,RLL_UNIT_KM_S_MPC,(rll_u32)(row-1ull),z,v,s,fnv,crc);
        ctx->receipt->hz_rows++;
    }
    return ctx->receipt->hz_rows ? RLL_REAL_OK : RLL_REAL_TOKEN_VAZIO;
}

static int rr_parse_fs8(rr_context *ctx, const rll_u8 *data, rll_u64 len) {
    rll_u64 cursor=0ull,row=0ull; rr_slice line;
    rll_u64 fnv=rr_fnv(data,len); rll_u32 crc=rr_crc(data,len);
    while (rr_next_line(data,len,&cursor,&line)) {
        rr_slice f[RR_MAX_FIELDS]; rll_u32 n=0u; rll_i64 z,v,s;
        if (!line.len) continue;
        if (row++==0ull) {
            if (!rr_slice_eq(line,"z,fs8,sigma,survey,method,reference,source_url,notes",52ull)) return RLL_REAL_E_SCHEMA;
            continue;
        }
        if (rr_split(line,f,&n)!=RLL_REAL_OK || n!=8u) return RLL_REAL_E_FORMAT;
        if (rr_parse_q16(f[0].ptr,f[0].len,&z)||rr_parse_q16(f[1].ptr,f[1].len,&v)||rr_parse_q16(f[2].ptr,f[2].len,&s)) return RLL_REAL_E_FORMAT;
        if (s<=0ll) return RLL_REAL_E_UNCERTAINTY;
        rr_bind_and_push(ctx,RLL_REAL_SOURCE_FS8,RLL_Q_FSIGMA8,RLL_UNIT_DIMENSIONLESS,(rll_u32)(row-1ull),z,v,s,fnv,crc);
        ctx->receipt->fsigma8_rows++;
    }
    return ctx->receipt->fsigma8_rows ? RLL_REAL_OK : RLL_REAL_TOKEN_VAZIO;
}

static int rr_parse_bao(rr_context *ctx, const rll_u8 *data, rll_u64 len) {
    static const char header[]="release,tracer,z_eff,observable,value,sigma,covariance_block,paired_observable,correlation_coefficient,primary_likelihood,source_table,source_url,notes";
    rll_u64 cursor=0ull,row=0ull; rr_slice line;
    rll_u64 fnv=rr_fnv(data,len); rll_u32 crc=rr_crc(data,len);
    while (rr_next_line(data,len,&cursor,&line)) {
        rr_slice f[RR_MAX_FIELDS]; rll_u32 n=0u,q; rll_i64 z,v,s;
        if (!line.len) continue;
        if (row++==0ull) {
            if (!rr_slice_eq(line,header,(rll_u64)(sizeof(header)-1u))) return RLL_REAL_E_SCHEMA;
            continue;
        }
        if (rr_split(line,f,&n)!=RLL_REAL_OK || n!=13u) return RLL_REAL_E_FORMAT;
        if (rr_slice_eq(f[3],"DV_over_rd",10ull)) q=RLL_Q_BAO_DV_RS;
        else if (rr_slice_eq(f[3],"DM_over_rd",10ull)) q=RLL_Q_BAO_DM_RS;
        else if (rr_slice_eq(f[3],"DH_over_rd",10ull)) q=RLL_Q_BAO_DH_RS;
        else return RLL_REAL_E_SCHEMA;
        if (!rr_slice_eq(f[9],"true",4ull)) return RLL_REAL_E_SCHEMA;
        if (rr_parse_q16(f[2].ptr,f[2].len,&z)||rr_parse_q16(f[4].ptr,f[4].len,&v)||rr_parse_q16(f[5].ptr,f[5].len,&s)) return RLL_REAL_E_FORMAT;
        if (s<=0ll) return RLL_REAL_E_UNCERTAINTY;
        rr_bind_and_push(ctx,RLL_REAL_SOURCE_BAO,q,RLL_UNIT_DIMENSIONLESS,(rll_u32)(row-1ull),z,v,s,fnv,crc);
        ctx->receipt->bao_rows++;
    }
    return ctx->receipt->bao_rows ? RLL_REAL_OK : RLL_REAL_TOKEN_VAZIO;
}

static int rr_find_number(const rll_u8 *data,rll_u64 len,const char *key,rll_u64 key_len,rll_i64 *out) {
    rll_u64 i=0ull;
    while (i+key_len+2ull<len) {
        if (data[i]=='"' && rr_equal(data+i+1ull,(const rll_u8*)key,key_len) && data[i+key_len+1ull]=='"') {
            rll_u64 p=i+key_len+2ull,start;
            while (p<len && (data[p]==' '||data[p]=='\t'||data[p]=='\r'||data[p]=='\n')) p++;
            if (p>=len||data[p]!=':') return RLL_REAL_E_FORMAT;
            p++; while (p<len && (data[p]==' '||data[p]=='\t'||data[p]=='\r'||data[p]=='\n')) p++;
            start=p;
            while (p<len) { rll_u8 c=data[p]; if (!((c>='0'&&c<='9')||c=='-'||c=='+'||c=='.'||c=='e'||c=='E')) break; p++; }
            return rr_parse_q16(data+start,p-start,out);
        }
        i++;
    }
    return RLL_REAL_TOKEN_VAZIO;
}

static int rr_find_matrix(const rll_u8 *data,rll_u64 len,const char *key,rll_u64 key_len,rll_i64 out[9]) {
    rll_u64 i=0ull;
    while (i+key_len+2ull<len) {
        if (data[i]=='"' && rr_equal(data+i+1ull,(const rll_u8*)key,key_len) && data[i+key_len+1ull]=='"') {
            rll_u64 p=i+key_len+2ull; rll_u32 n=0u;
            while (p<len && data[p]!='[') p++;
            while (p<len && n<9u) {
                while (p<len && !((data[p]>='0'&&data[p]<='9')||data[p]=='-'||data[p]=='+')) p++;
                if (p>=len) break;
                { rll_u64 start=p; int rc;
                  while (p<len) { rll_u8 c=data[p]; if (!((c>='0'&&c<='9')||c=='-'||c=='+'||c=='.'||c=='e'||c=='E')) break; p++; }
                  rc=rr_parse_q16(data+start,p-start,&out[n]); if (rc!=RLL_REAL_OK) return rc; n++; }
            }
            return n==9u?RLL_REAL_OK:RLL_REAL_E_COVARIANCE;
        }
        i++;
    }
    return RLL_REAL_TOKEN_VAZIO;
}

static rll_i64 rr_ratio_q16(rll_i64 delta_q16,rll_i64 sigma_q16) {
    if (sigma_q16<=0ll || delta_q16>(RR_I64_MAX>>16) || delta_q16<(RR_I64_MIN>>16)) return RR_I64_MAX;
    return (delta_q16<<16u)/sigma_q16;
}

static int rr_inverse_corr_q16(const rll_i64 r[9],rll_i64 inv[9]) {
    rll_i64 c00=(r[4]*r[8]-r[5]*r[7]);
    rll_i64 c01=-(r[3]*r[8]-r[5]*r[6]);
    rll_i64 c02=(r[3]*r[7]-r[4]*r[6]);
    rll_i64 c10=-(r[1]*r[8]-r[2]*r[7]);
    rll_i64 c11=(r[0]*r[8]-r[2]*r[6]);
    rll_i64 c12=-(r[0]*r[7]-r[1]*r[6]);
    rll_i64 c20=(r[1]*r[5]-r[2]*r[4]);
    rll_i64 c21=-(r[0]*r[5]-r[2]*r[3]);
    rll_i64 c22=(r[0]*r[4]-r[1]*r[3]);
    rll_i64 det=r[0]*c00+r[1]*c01+r[2]*c02;
    rll_i64 cof[9]={c00,c10,c20,c01,c11,c21,c02,c12,c22};
    rll_i64 den=det>>17u; rll_u32 i=0u;
    if (den<=0ll) return RLL_REAL_E_COVARIANCE;
    while (i<9u) { if (cof[i]>(RR_I64_MAX>>15)||cof[i]<(RR_I64_MIN>>15)) return RLL_REAL_E_RANGE; inv[i]=(cof[i]<<15u)/den; i++; }
    return RLL_REAL_OK;
}

static int rr_push_cmb_correlated(rr_context *ctx,rll_i64 z,const rll_i64 obs[3],const rll_i64 sig[3],const rll_i64 corr[9],rll_u64 fnv,rll_u32 crc) {
    rll_canonical_observation o[3]; rll_i64 model[3],u[3],inv[9],tmp[3],chi=0ll;
    rll_u32 q[3]={RLL_Q_CMB_SHIFT_R,RLL_Q_CMB_ACOUSTIC_SCALE,RLL_Q_CMB_OMEGA_B_H2};
    rll_u32 i,j; int rc; rll_u32 all_models=1u;
    for (i=0u;i<3u;i++) {
        rll_real_model_request req;
        o[i].domain=RLL_DOMAIN_COSMOLOGY; o[i].quantity=q[i]; o[i].unit=RLL_UNIT_DIMENSIONLESS; o[i].state=RLL_STATE_OBSERVED;
        o[i].value_q16=obs[i]; o[i].model_q16=0ll; o[i].sigma_q16=sig[i]; o[i].sample_count=1ull;
        o[i].flags=RR_FLAGS_BASE; o[i].sequence_id=i+1u; o[i].source_fnv1a64=fnv; o[i].source_crc32=crc;
        req.dataset_mask=RLL_REAL_SOURCE_CMB; req.quantity=q[i]; req.sequence_id=i+1u; req.reserved=0u; req.axis_q16=z; req.observed_q16=obs[i]; req.sigma_q16=sig[i];
        if (!ctx->model_callback || ctx->model_callback(ctx->model_context,&req,&model[i])!=RLL_REAL_MODEL_OK) all_models=0u;
    }
    if (!all_models) {
        for (i=0u;i<3u;i++) { ctx->receipt->model_token_vazio_rows++; (void)rll_canonical_push_extended(&ctx->accumulator,&o[i]); }
        ctx->receipt->parsed_rows+=3u;
        return RLL_REAL_OK;
    }
    rc=rr_inverse_corr_q16(corr,inv); if (rc!=RLL_REAL_OK) return rc;
    for (i=0u;i<3u;i++) { o[i].model_q16=model[i]; o[i].flags|=RLL_OBS_MODEL_REGISTERED; u[i]=rr_ratio_q16(obs[i]-model[i],sig[i]); if (u[i]==RR_I64_MAX) return RLL_REAL_E_RANGE; }
    for (i=0u;i<3u;i++) { tmp[i]=0ll; for (j=0u;j<3u;j++) tmp[i]+=(inv[i*3u+j]*u[j])>>16u; }
    for (i=0u;i<3u;i++) chi+=(u[i]*tmp[i])>>16u;
    if (chi<0ll) return RLL_REAL_E_COVARIANCE;
    for (i=0u;i<3u;i++) { ctx->accumulator.total++; ctx->accumulator.evidence++; ctx->accumulator.degrees_of_freedom++; rr_digest_obs(&ctx->accumulator,&o[i],RLL_COUPLING_EVIDENCE); }
    if (ctx->accumulator.chi2_q16>RR_I64_MAX-chi) ctx->accumulator.chi2_q16=RR_I64_MAX; else ctx->accumulator.chi2_q16+=chi;
    ctx->receipt->model_bound_rows+=3u; ctx->receipt->parsed_rows+=3u; ctx->receipt->cmb_covariance_used=1u;
    return RLL_REAL_OK;
}

static int rr_parse_cmb(rr_context *ctx,const rll_u8 *data,rll_u64 len) {
    rll_i64 z,obs[3],sig[3],corr[9]; rll_u64 fnv=rr_fnv(data,len); rll_u32 crc=rr_crc(data,len); int rc;
    rc=rr_find_number(data,len,"z_CMB",5ull,&z); if(rc!=RLL_REAL_OK)return rc;
    rc=rr_find_number(data,len,"R_obs",5ull,&obs[0]); if(rc!=RLL_REAL_OK)return rc;
    rc=rr_find_number(data,len,"R_sig",5ull,&sig[0]); if(rc!=RLL_REAL_OK)return rc;
    rc=rr_find_number(data,len,"la_obs",6ull,&obs[1]); if(rc!=RLL_REAL_OK)return rc;
    rc=rr_find_number(data,len,"la_sig",6ull,&sig[1]); if(rc!=RLL_REAL_OK)return rc;
    rc=rr_find_number(data,len,"ob_h2_obs",9ull,&obs[2]); if(rc!=RLL_REAL_OK)return rc;
    rc=rr_find_number(data,len,"ob_h2_sig",9ull,&sig[2]); if(rc!=RLL_REAL_OK)return rc;
    rc=rr_find_matrix(data,len,"correlation_matrix",18ull,corr); if(rc!=RLL_REAL_OK)return rc;
    if(sig[0]<=0ll||sig[1]<=0ll||sig[2]<=0ll)return RLL_REAL_E_UNCERTAINTY;
    rc=rr_push_cmb_correlated(ctx,z,obs,sig,corr,fnv,crc); if(rc!=RLL_REAL_OK)return rc;
    ctx->receipt->cmb_rows=3u;
    return RLL_REAL_OK;
}

static void rr_receipt_init(rll_real_ingest_receipt *r) {
    rll_u8 *p=(rll_u8*)r; rll_u64 i=0ull;
    while(i<(rll_u64)sizeof(*r)){p[i++]=0u;}
    r->schema=RLL_REAL_SCHEMA_V1; r->required_source_mask=RLL_REAL_SOURCE_ALL; r->claim_allowed=0u;
}

int rll_real_ingest_all(const rll_real_input_bundle *b,rll_real_model_callback cb,void *model_ctx,rll_real_ingest_receipt *receipt) {
    rr_context ctx; int rc;
    if(!b||!receipt||!b->hz_csv||!b->bao_csv||!b->fsigma8_csv||!b->cmb_json)return RLL_REAL_E_NULL;
    rr_receipt_init(receipt); rll_canonical_init(&ctx.accumulator,RLL_REGION_COSMOLOGY_EVIDENCE);
    ctx.model_callback=cb; ctx.model_context=model_ctx; ctx.receipt=receipt;
    if(!rr_verify_sha(b->hz_csv,b->hz_len,RR_SHA_HZ))return (receipt->status=RLL_REAL_E_SHA256);
    receipt->source_verified_mask|=RLL_REAL_SOURCE_HZ;
    if(!rr_verify_sha(b->bao_csv,b->bao_len,RR_SHA_BAO))return (receipt->status=RLL_REAL_E_SHA256);
    receipt->source_verified_mask|=RLL_REAL_SOURCE_BAO;
    if(!rr_verify_sha(b->fsigma8_csv,b->fsigma8_len,RR_SHA_FS8))return (receipt->status=RLL_REAL_E_SHA256);
    receipt->source_verified_mask|=RLL_REAL_SOURCE_FS8;
    if(!rr_verify_sha(b->cmb_json,b->cmb_len,RR_SHA_CMB))return (receipt->status=RLL_REAL_E_SHA256);
    receipt->source_verified_mask|=RLL_REAL_SOURCE_CMB;
    rc=rr_parse_hz(&ctx,b->hz_csv,b->hz_len); if(rc!=RLL_REAL_OK)return (receipt->status=rc);
    rc=rr_parse_bao(&ctx,b->bao_csv,b->bao_len); if(rc!=RLL_REAL_OK)return (receipt->status=rc);
    rc=rr_parse_fs8(&ctx,b->fsigma8_csv,b->fsigma8_len); if(rc!=RLL_REAL_OK)return (receipt->status=rc);
    rc=rr_parse_cmb(&ctx,b->cmb_json,b->cmb_len); if(rc!=RLL_REAL_OK)return (receipt->status=rc);
    receipt->canonical=rll_canonical_snapshot(&ctx.accumulator);
    if(receipt->source_verified_mask!=RLL_REAL_SOURCE_ALL||receipt->parsed_rows!=65u||receipt->hz_rows!=33u||receipt->bao_rows!=13u||receipt->fsigma8_rows!=16u||receipt->cmb_rows!=3u) {
        receipt->status=RLL_REAL_TOKEN_VAZIO; return RLL_REAL_TOKEN_VAZIO;
    }
    receipt->status=RLL_REAL_OK; receipt->claim_allowed=0u; receipt->canonical.claim_allowed=0u;
    return RLL_REAL_OK;
}
