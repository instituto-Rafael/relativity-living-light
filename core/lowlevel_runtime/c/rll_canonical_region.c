#include "rll_canonical_region.h"

#define RLLC_FNV_OFFSET 14695981039346656037ull
#define RLLC_FNV_PRIME 1099511628211ull
#define RLLC_CRC32_INIT 0xFFFFFFFFu
#define RLLC_CRC32_POLY_REV 0xEDB88320u
#define RLLC_CRC32_FINAL_XOR 0xFFFFFFFFu
#define RLLC_I64_MAX 0x7FFFFFFFFFFFFFFFll
#define RLLC_I64_MIN (-0x7FFFFFFFFFFFFFFFll - 1ll)
#define RLLC_U64_MAX 0xFFFFFFFFFFFFFFFFull
#define RLLC_MAX_DECIMAL_DIGITS 15u
#define RLLC_MAX_LINE_FIELDS 16u

static rllc_u64 rllc_fnv1a64(const rllc_u8 *data, rllc_u64 len) {
    rllc_u64 h = RLLC_FNV_OFFSET;
    rllc_u64 i = 0ull;
    if ((data == (const rllc_u8 *)0) && (len != 0ull)) {
        return h;
    }
    while (i < len) {
        h ^= (rllc_u64)data[i];
        h *= RLLC_FNV_PRIME;
        i++;
    }
    return h;
}

static rllc_u32 rllc_crc32(const rllc_u8 *data, rllc_u64 len) {
    rllc_u32 crc = RLLC_CRC32_INIT;
    rllc_u64 i = 0ull;
    if ((data == (const rllc_u8 *)0) && (len != 0ull)) {
        return crc ^ RLLC_CRC32_FINAL_XOR;
    }
    while (i < len) {
        rllc_u32 x = (crc ^ (rllc_u32)data[i]) & 0xFFu;
        rllc_u32 j = 0u;
        while (j < 8u) {
            rllc_u32 mask = (rllc_u32)(-(rllc_i64)(x & 1u));
            x = (x >> 1u) ^ (RLLC_CRC32_POLY_REV & mask);
            j++;
        }
        crc = (crc >> 8u) ^ x;
        i++;
    }
    return crc ^ RLLC_CRC32_FINAL_XOR;
}

static int rllc_memeq(const rllc_u8 *a, const rllc_u8 *b, rllc_u64 len) {
    rllc_u8 diff = 0u;
    rllc_u64 i = 0ull;
    while (i < len) {
        diff = (rllc_u8)(diff | (rllc_u8)(a[i] ^ b[i]));
        i++;
    }
    return diff == 0u;
}

static void rllc_memcpy(rllc_u8 *dst, const rllc_u8 *src, rllc_u64 len) {
    rllc_u64 i = 0ull;
    while (i < len) {
        dst[i] = src[i];
        i++;
    }
}

static int rllc_sha_nonzero(const rllc_u8 sha[32]) {
    rllc_u8 x = 0u;
    rllc_u32 i = 0u;
    while (i < 32u) {
        x = (rllc_u8)(x | sha[i]);
        i++;
    }
    return x != 0u;
}

static rllc_u32 rllc_hex_value(rllc_u8 c) {
    if (c >= (rllc_u8)'0' && c <= (rllc_u8)'9') return (rllc_u32)(c - (rllc_u8)'0');
    if (c >= (rllc_u8)'a' && c <= (rllc_u8)'f') return (rllc_u32)(10u + c - (rllc_u8)'a');
    if (c >= (rllc_u8)'A' && c <= (rllc_u8)'F') return (rllc_u32)(10u + c - (rllc_u8)'A');
    return 0xFFFFFFFFu;
}

int rllc_sha256_from_hex(const rllc_u8 *hex64, rllc_u8 out[32]) {
    rllc_u32 i = 0u;
    if (hex64 == (const rllc_u8 *)0 || out == (rllc_u8 *)0) return RLLC_E_NULL;
    while (i < 32u) {
        rllc_u32 hi = rllc_hex_value(hex64[i * 2u]);
        rllc_u32 lo = rllc_hex_value(hex64[i * 2u + 1u]);
        if (hi > 15u || lo > 15u) return RLLC_E_FORMAT;
        out[i] = (rllc_u8)((hi << 4u) | lo);
        i++;
    }
    return RLLC_OK;
}

static int rllc_u64_mul10(rllc_u64 *value) {
    if (*value > RLLC_U64_MAX / 10ull) return RLLC_E_RANGE;
    *value *= 10ull;
    return RLLC_OK;
}

static int rllc_u64_mul_pow10(rllc_u64 *value, rllc_u32 n) {
    while (n != 0u) {
        int rc = rllc_u64_mul10(value);
        if (rc != RLLC_OK) return rc;
        n--;
    }
    return RLLC_OK;
}

static int rllc_pow10_u64(rllc_u32 n, rllc_u64 *out) {
    rllc_u64 v = 1ull;
    int rc = rllc_u64_mul_pow10(&v, n);
    if (rc != RLLC_OK) return rc;
    *out = v;
    return RLLC_OK;
}

int rllc_parse_q32(const rllc_u8 *text, rllc_u64 len, rllc_i64 *out_q32) {
    rllc_u64 i = 0ull;
    rllc_u64 mantissa = 0ull;
    rllc_u32 digits = 0u;
    rllc_u32 fractional_digits = 0u;
    rllc_u32 seen_dot = 0u;
    rllc_u32 seen_digit = 0u;
    rllc_u32 negative = 0u;
    rllc_i64 exponent = 0ll;
    rllc_u32 exponent_negative = 0u;
    rllc_u32 exponent_seen = 0u;
    rllc_u32 exponent_digits = 0u;
    rllc_u64 absolute_q32;

    if (text == (const rllc_u8 *)0 || out_q32 == (rllc_i64 *)0) return RLLC_E_NULL;
    if (len == 0ull) return RLLC_E_FORMAT;

    if (text[i] == (rllc_u8)'-' || text[i] == (rllc_u8)'+') {
        negative = text[i] == (rllc_u8)'-';
        i++;
    }

    while (i < len) {
        rllc_u8 c = text[i];
        if (c >= (rllc_u8)'0' && c <= (rllc_u8)'9') {
            if (exponent_seen != 0u) {
                if (exponent_digits >= 3u) return RLLC_E_RANGE;
                exponent = exponent * 10ll + (rllc_i64)(c - (rllc_u8)'0');
                exponent_digits++;
            } else {
                if (digits >= RLLC_MAX_DECIMAL_DIGITS) return RLLC_E_RANGE;
                if (mantissa > (RLLC_U64_MAX - (rllc_u64)(c - (rllc_u8)'0')) / 10ull) return RLLC_E_RANGE;
                mantissa = mantissa * 10ull + (rllc_u64)(c - (rllc_u8)'0');
                digits++;
                if (seen_dot != 0u) fractional_digits++;
                seen_digit = 1u;
            }
        } else if (c == (rllc_u8)'.' && exponent_seen == 0u && seen_dot == 0u) {
            seen_dot = 1u;
        } else if ((c == (rllc_u8)'e' || c == (rllc_u8)'E') && exponent_seen == 0u && seen_digit != 0u) {
            exponent_seen = 1u;
            if (i + 1ull < len && (text[i + 1ull] == (rllc_u8)'-' || text[i + 1ull] == (rllc_u8)'+')) {
                exponent_negative = text[i + 1ull] == (rllc_u8)'-';
                i++;
            }
        } else {
            return RLLC_E_FORMAT;
        }
        i++;
    }

    if (seen_digit == 0u || (exponent_seen != 0u && exponent_digits == 0u)) return RLLC_E_FORMAT;
    if (exponent_negative != 0u) exponent = -exponent;
    exponent -= (rllc_i64)fractional_digits;
    if (exponent > 12ll || exponent < -18ll) return RLLC_E_RANGE;

    if (exponent >= 0ll) {
        rllc_u64 scaled = mantissa;
        int rc = rllc_u64_mul_pow10(&scaled, (rllc_u32)exponent);
        if (rc != RLLC_OK) return rc;
        if (scaled > 0x7FFFFFFFull) return RLLC_E_RANGE;
        absolute_q32 = scaled << 32u;
    } else {
        rllc_u64 denominator;
        rllc_u64 integer_part;
        rllc_u64 remainder;
        rllc_u64 fractional_q32;
        int rc = rllc_pow10_u64((rllc_u32)(-exponent), &denominator);
        if (rc != RLLC_OK) return rc;
        integer_part = mantissa / denominator;
        remainder = mantissa % denominator;
        if (integer_part > 0x7FFFFFFFull) return RLLC_E_RANGE;
        if (remainder > (RLLC_U64_MAX >> 32u)) return RLLC_E_RANGE;
        fractional_q32 = ((remainder << 32u) + (denominator >> 1u)) / denominator;
        absolute_q32 = (integer_part << 32u) + fractional_q32;
    }

    if (negative != 0u) {
        if (absolute_q32 > 0x8000000000000000ull) return RLLC_E_RANGE;
        if (absolute_q32 == 0x8000000000000000ull) *out_q32 = RLLC_I64_MIN;
        else *out_q32 = -(rllc_i64)absolute_q32;
    } else {
        if (absolute_q32 > 0x7FFFFFFFFFFFFFFFull) return RLLC_E_RANGE;
        *out_q32 = (rllc_i64)absolute_q32;
    }
    return RLLC_OK;
}

void rllc_init(rllc_state *state) {
    rllc_u32 i = 0u;
    if (state == (rllc_state *)0) return;
    state->schema = RLLC_SCHEMA_V1;
    state->claim_allowed = 0u;
    state->violation_mask = 0u;
    state->real_dataset_mask = 0u;
    state->accepted = 0ull;
    state->rejected = 0ull;
    state->token_vazio_count = 0ull;
    while (i < RLLC_DATASET_SLOTS) {
        state->dataset_counts[i] = 0ull;
        i++;
    }
    state->rolling_fnv1a64 = RLLC_FNV_OFFSET;
    state->rolling_crc32 = 0u;
    state->cmb_covariance_present = 0u;
    i = 0u;
    while (i < 9u) {
        state->cmb_covariance_q32[i] = 0ll;
        i++;
    }
}

static int rllc_reject(rllc_state *state, int status, rllc_u32 violation) {
    if (state != (rllc_state *)0) {
        state->rejected++;
        state->violation_mask |= violation;
    }
    return status;
}

static rllc_u32 rllc_dataset_mask(rllc_u32 dataset) {
    if (dataset >= RLLC_DS_HZ && dataset <= RLLC_DS_CMB_SHIFT) {
        return 1u << (dataset - 1u);
    }
    return 0u;
}

static void rllc_mix_observation(rllc_state *state, const rllc_observation *obs) {
    const rllc_u8 *raw = (const rllc_u8 *)obs;
    rllc_u64 len = (rllc_u64)sizeof(*obs);
    rllc_u64 h = rllc_fnv1a64(raw, len);
    rllc_u32 c = rllc_crc32(raw, len);
    state->rolling_fnv1a64 ^= h;
    state->rolling_fnv1a64 *= RLLC_FNV_PRIME;
    state->rolling_crc32 ^= c + 0x9E3779B9u + (state->rolling_crc32 << 6u) + (state->rolling_crc32 >> 2u);
}

int rllc_ingest(rllc_state *state, const rllc_observation *obs) {
    rllc_u32 required_flags = RLLC_F_REAL | RLLC_F_PROVENANCE_VERIFIED | RLLC_F_CLAIM_BLOCKED;
    if (state == (rllc_state *)0 || obs == (const rllc_observation *)0) return RLLC_E_NULL;
    if (state->schema != RLLC_SCHEMA_V1 || obs->schema != RLLC_SCHEMA_V1) return rllc_reject(state, RLLC_E_SCHEMA, RLLC_V_SCHEMA);
    if (obs->dataset == RLLC_DS_NONE || obs->dataset >= RLLC_DATASET_SLOTS) return rllc_reject(state, RLLC_E_SCHEMA, RLLC_V_SCHEMA);
    if ((obs->flags & RLLC_F_SYNTHETIC) != 0u) return rllc_reject(state, RLLC_E_SYNTHETIC, RLLC_V_SYNTHETIC);
    if ((obs->flags & required_flags) != required_flags) {
        if ((obs->flags & RLLC_F_CLAIM_BLOCKED) == 0u) return rllc_reject(state, RLLC_E_CLAIM, RLLC_V_CLAIM);
        return rllc_reject(state, RLLC_E_PROVENANCE, RLLC_V_PROVENANCE);
    }
    if (!rllc_sha_nonzero(obs->source.sha256)) return rllc_reject(state, RLLC_E_PROVENANCE, RLLC_V_PROVENANCE);
    if (obs->sigma_q32 <= 0ll) return rllc_reject(state, RLLC_E_UNCERTAINTY, RLLC_V_UNCERTAINTY);
    if (obs->dataset != RLLC_DS_ADAPTER_LOCAL_PHYSICS && obs->x_q32 < 0ll) return rllc_reject(state, RLLC_E_RANGE, RLLC_V_RANGE);
    if (obs->value_q32 < 0ll) return rllc_reject(state, RLLC_E_RANGE, RLLC_V_RANGE);

    state->dataset_counts[obs->dataset]++;
    state->accepted++;
    state->real_dataset_mask |= rllc_dataset_mask(obs->dataset);
    rllc_mix_observation(state, obs);
    return RLLC_OK;
}

typedef struct rllc_slice {
    const rllc_u8 *ptr;
    rllc_u64 len;
} rllc_slice;

static int rllc_next_line(const rllc_u8 *data, rllc_u64 len, rllc_u64 *cursor, rllc_slice *line) {
    rllc_u64 start;
    rllc_u64 end;
    if (*cursor >= len) return 0;
    start = *cursor;
    end = start;
    while (end < len && data[end] != (rllc_u8)'\n') end++;
    line->ptr = data + start;
    line->len = end - start;
    if (line->len != 0ull && line->ptr[line->len - 1ull] == (rllc_u8)'\r') line->len--;
    *cursor = end < len ? end + 1ull : end;
    return 1;
}

static int rllc_split_csv(rllc_slice line, rllc_slice fields[RLLC_MAX_LINE_FIELDS], rllc_u32 *field_count) {
    rllc_u64 i = 0ull;
    rllc_u64 start = 0ull;
    rllc_u32 n = 0u;
    while (i <= line.len) {
        if (i < line.len && line.ptr[i] == (rllc_u8)'"') return RLLC_E_FORMAT;
        if (i == line.len || line.ptr[i] == (rllc_u8)',') {
            if (n >= RLLC_MAX_LINE_FIELDS) return RLLC_E_CAPACITY;
            fields[n].ptr = line.ptr + start;
            fields[n].len = i - start;
            n++;
            start = i + 1ull;
        }
        i++;
    }
    *field_count = n;
    return RLLC_OK;
}

static int rllc_slice_eq(rllc_slice s, const char *literal, rllc_u64 literal_len) {
    return s.len == literal_len && rllc_memeq(s.ptr, (const rllc_u8 *)literal, literal_len);
}

static void rllc_fill_source(
    rllc_source *source, const rllc_u8 sha256[32], rllc_u64 byte_count, rllc_slice source_name) {
    rllc_memcpy(source->sha256, sha256, 32ull);
    source->byte_count = byte_count;
    source->source_name_fnv1a64 = rllc_fnv1a64(source_name.ptr, source_name.len);
    source->source_name_crc32 = rllc_crc32(source_name.ptr, source_name.len);
}

static int rllc_emit_csv_observation(
    rllc_state *state,
    rllc_u32 dataset,
    rllc_u32 observable,
    rllc_u32 unit,
    rllc_u64 sequence,
    rllc_slice x,
    rllc_slice value,
    rllc_slice sigma,
    rllc_slice source_name,
    rllc_u64 byte_count,
    const rllc_u8 sha256[32]) {
    rllc_observation obs;
    int rc;
    obs.schema = RLLC_SCHEMA_V1;
    obs.dataset = dataset;
    obs.observable = observable;
    obs.unit = unit;
    obs.flags = RLLC_F_REAL | RLLC_F_PROVENANCE_VERIFIED | RLLC_F_CLAIM_BLOCKED;
    obs.reserved = 0u;
    obs.sequence = sequence;
    rc = rllc_parse_q32(x.ptr, x.len, &obs.x_q32);
    if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rc = rllc_parse_q32(value.ptr, value.len, &obs.value_q32);
    if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rc = rllc_parse_q32(sigma.ptr, sigma.len, &obs.sigma_q32);
    if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rllc_fill_source(&obs.source, sha256, byte_count, source_name);
    return rllc_ingest(state, &obs);
}

int rllc_parse_hz_csv(rllc_state *state, const rllc_u8 *data, rllc_u64 len, const rllc_u8 sha256[32]) {
    rllc_u64 cursor = 0ull;
    rllc_u64 row = 0ull;
    rllc_slice line;
    if (state == (rllc_state *)0 || data == (const rllc_u8 *)0 || sha256 == (const rllc_u8 *)0) return RLLC_E_NULL;
    if (!rllc_sha_nonzero(sha256)) return rllc_reject(state, RLLC_E_PROVENANCE, RLLC_V_PROVENANCE);
    while (rllc_next_line(data, len, &cursor, &line)) {
        rllc_slice fields[RLLC_MAX_LINE_FIELDS];
        rllc_u32 n = 0u;
        int rc;
        if (line.len == 0ull) continue;
        if (row++ == 0ull) {
            if (!rllc_slice_eq(line, "z,H_obs,sigma_H,source", 22ull)) return rllc_reject(state, RLLC_E_SCHEMA, RLLC_V_SCHEMA);
            continue;
        }
        rc = rllc_split_csv(line, fields, &n);
        if (rc != RLLC_OK || n != 4u) return rllc_reject(state, RLLC_E_FORMAT, RLLC_V_FORMAT);
        rc = rllc_emit_csv_observation(state, RLLC_DS_HZ, RLLC_OBS_H_KM_S_MPC, RLLC_UNIT_KM_S_MPC,
                                       row - 1ull, fields[0], fields[1], fields[2], fields[3], len, sha256);
        if (rc != RLLC_OK) return rc;
    }
    return state->dataset_counts[RLLC_DS_HZ] != 0ull ? RLLC_OK : RLLC_TOKEN_VAZIO;
}

int rllc_parse_fsigma8_csv(rllc_state *state, const rllc_u8 *data, rllc_u64 len, const rllc_u8 sha256[32]) {
    rllc_u64 cursor = 0ull;
    rllc_u64 row = 0ull;
    rllc_slice line;
    if (state == (rllc_state *)0 || data == (const rllc_u8 *)0 || sha256 == (const rllc_u8 *)0) return RLLC_E_NULL;
    while (rllc_next_line(data, len, &cursor, &line)) {
        rllc_slice fields[RLLC_MAX_LINE_FIELDS];
        rllc_u32 n = 0u;
        int rc;
        if (line.len == 0ull) continue;
        if (row++ == 0ull) {
            if (!rllc_slice_eq(line, "z,fs8,sigma,survey,method,reference,source_url,notes", 52ull)) return rllc_reject(state, RLLC_E_SCHEMA, RLLC_V_SCHEMA);
            continue;
        }
        rc = rllc_split_csv(line, fields, &n);
        if (rc != RLLC_OK || n != 8u) return rllc_reject(state, RLLC_E_FORMAT, RLLC_V_FORMAT);
        rc = rllc_emit_csv_observation(state, RLLC_DS_FSIGMA8, RLLC_OBS_FSIGMA8, RLLC_UNIT_DIMENSIONLESS,
                                       row - 1ull, fields[0], fields[1], fields[2], fields[5], len, sha256);
        if (rc != RLLC_OK) return rc;
    }
    return state->dataset_counts[RLLC_DS_FSIGMA8] != 0ull ? RLLC_OK : RLLC_TOKEN_VAZIO;
}

int rllc_parse_bao_csv(rllc_state *state, const rllc_u8 *data, rllc_u64 len, const rllc_u8 sha256[32]) {
    static const char header[] = "release,tracer,z_eff,observable,value,sigma,covariance_block,paired_observable,correlation_coefficient,primary_likelihood,source_table,source_url,notes";
    rllc_u64 cursor = 0ull;
    rllc_u64 row = 0ull;
    rllc_slice line;
    if (state == (rllc_state *)0 || data == (const rllc_u8 *)0 || sha256 == (const rllc_u8 *)0) return RLLC_E_NULL;
    while (rllc_next_line(data, len, &cursor, &line)) {
        rllc_slice fields[RLLC_MAX_LINE_FIELDS];
        rllc_u32 n = 0u;
        rllc_u32 observable;
        int rc;
        if (line.len == 0ull) continue;
        if (row++ == 0ull) {
            if (!rllc_slice_eq(line, header, (rllc_u64)(sizeof(header) - 1u))) return rllc_reject(state, RLLC_E_SCHEMA, RLLC_V_SCHEMA);
            continue;
        }
        rc = rllc_split_csv(line, fields, &n);
        if (rc != RLLC_OK || n != 13u) return rllc_reject(state, RLLC_E_FORMAT, RLLC_V_FORMAT);
        if (rllc_slice_eq(fields[3], "DV_over_rd", 10ull)) observable = RLLC_OBS_DV_OVER_RD;
        else if (rllc_slice_eq(fields[3], "DM_over_rd", 10ull)) observable = RLLC_OBS_DM_OVER_RD;
        else if (rllc_slice_eq(fields[3], "DH_over_rd", 10ull)) observable = RLLC_OBS_DH_OVER_RD;
        else return rllc_reject(state, RLLC_E_SCHEMA, RLLC_V_SCHEMA);
        if (!rllc_slice_eq(fields[9], "true", 4ull)) return rllc_reject(state, RLLC_E_CLAIM, RLLC_V_CLAIM);
        rc = rllc_emit_csv_observation(state, RLLC_DS_BAO, observable, RLLC_UNIT_DIMENSIONLESS,
                                       row - 1ull, fields[2], fields[4], fields[5], fields[11], len, sha256);
        if (rc != RLLC_OK) return rc;
    }
    return state->dataset_counts[RLLC_DS_BAO] != 0ull ? RLLC_OK : RLLC_TOKEN_VAZIO;
}

static rllc_i64 rllc_abs_i64(rllc_i64 v) {
    if (v == RLLC_I64_MIN) return RLLC_I64_MAX;
    return v < 0ll ? -v : v;
}

static int rllc_find_key_number(
    const rllc_u8 *data, rllc_u64 len, const char *key, rllc_u64 key_len, rllc_i64 *out) {
    rllc_u64 i = 0ull;
    while (i + key_len + 2ull < len) {
        if (data[i] == (rllc_u8)'"' && rllc_memeq(data + i + 1ull, (const rllc_u8 *)key, key_len) && data[i + key_len + 1ull] == (rllc_u8)'"') {
            rllc_u64 p = i + key_len + 2ull;
            rllc_u64 start;
            while (p < len && (data[p] == (rllc_u8)' ' || data[p] == (rllc_u8)'\t' || data[p] == (rllc_u8)'\r' || data[p] == (rllc_u8)'\n')) p++;
            if (p >= len || data[p] != (rllc_u8)':') return RLLC_E_FORMAT;
            p++;
            while (p < len && (data[p] == (rllc_u8)' ' || data[p] == (rllc_u8)'\t' || data[p] == (rllc_u8)'\r' || data[p] == (rllc_u8)'\n')) p++;
            start = p;
            while (p < len) {
                rllc_u8 c = data[p];
                if (!((c >= (rllc_u8)'0' && c <= (rllc_u8)'9') || c == (rllc_u8)'-' || c == (rllc_u8)'+' || c == (rllc_u8)'.' || c == (rllc_u8)'e' || c == (rllc_u8)'E')) break;
                p++;
            }
            return rllc_parse_q32(data + start, p - start, out);
        }
        i++;
    }
    return RLLC_TOKEN_VAZIO;
}

static int rllc_find_covariance(const rllc_u8 *data, rllc_u64 len, rllc_i64 out[9]) {
    static const char key[] = "covariance";
    rllc_u64 i = 0ull;
    while (i + sizeof(key) + 2ull < len) {
        if (data[i] == (rllc_u8)'"' && rllc_memeq(data + i + 1ull, (const rllc_u8 *)key, sizeof(key) - 1u)) {
            rllc_u64 p = i + sizeof(key);
            rllc_u32 n = 0u;
            while (p < len && data[p] != (rllc_u8)'[') p++;
            while (p < len && n < 9u) {
                while (p < len && !((data[p] >= (rllc_u8)'0' && data[p] <= (rllc_u8)'9') || data[p] == (rllc_u8)'-' || data[p] == (rllc_u8)'+')) p++;
                if (p >= len) break;
                {
                    rllc_u64 start = p;
                    int rc;
                    while (p < len) {
                        rllc_u8 c = data[p];
                        if (!((c >= (rllc_u8)'0' && c <= (rllc_u8)'9') || c == (rllc_u8)'-' || c == (rllc_u8)'+' || c == (rllc_u8)'.' || c == (rllc_u8)'e' || c == (rllc_u8)'E')) break;
                        p++;
                    }
                    rc = rllc_parse_q32(data + start, p - start, &out[n]);
                    if (rc != RLLC_OK) return rc;
                    n++;
                }
            }
            return n == 9u ? RLLC_OK : RLLC_E_COVARIANCE;
        }
        i++;
    }
    return RLLC_TOKEN_VAZIO;
}

static int rllc_emit_cmb(
    rllc_state *state,
    rllc_u64 sequence,
    rllc_u32 observable,
    rllc_i64 z_q32,
    rllc_i64 value_q32,
    rllc_i64 sigma_q32,
    const rllc_u8 sha256[32],
    rllc_u64 byte_count) {
    static const rllc_u8 source_name[] = "Planck2018_distance_prior";
    rllc_observation obs;
    obs.schema = RLLC_SCHEMA_V1;
    obs.dataset = RLLC_DS_CMB_SHIFT;
    obs.observable = observable;
    obs.unit = RLLC_UNIT_DIMENSIONLESS;
    obs.flags = RLLC_F_REAL | RLLC_F_PROVENANCE_VERIFIED | RLLC_F_CLAIM_BLOCKED | RLLC_F_COVARIANCE_PRESENT;
    obs.reserved = 0u;
    obs.sequence = sequence;
    obs.x_q32 = z_q32;
    obs.value_q32 = value_q32;
    obs.sigma_q32 = sigma_q32;
    rllc_memcpy(obs.source.sha256, sha256, 32ull);
    obs.source.byte_count = byte_count;
    obs.source.source_name_fnv1a64 = rllc_fnv1a64(source_name, sizeof(source_name) - 1u);
    obs.source.source_name_crc32 = rllc_crc32(source_name, sizeof(source_name) - 1u);
    return rllc_ingest(state, &obs);
}

int rllc_parse_cmb_shift_json(rllc_state *state, const rllc_u8 *data, rllc_u64 len, const rllc_u8 sha256[32]) {
    rllc_i64 z, r, r_sig, la, la_sig, ob, ob_sig;
    rllc_i64 cov[9];
    rllc_u32 i;
    int rc;
    if (state == (rllc_state *)0 || data == (const rllc_u8 *)0 || sha256 == (const rllc_u8 *)0) return RLLC_E_NULL;
    if (!rllc_sha_nonzero(sha256)) return rllc_reject(state, RLLC_E_PROVENANCE, RLLC_V_PROVENANCE);
    rc = rllc_find_key_number(data, len, "z_CMB", 5ull, &z); if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rc = rllc_find_key_number(data, len, "R_obs", 5ull, &r); if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rc = rllc_find_key_number(data, len, "R_sig", 5ull, &r_sig); if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rc = rllc_find_key_number(data, len, "la_obs", 6ull, &la); if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rc = rllc_find_key_number(data, len, "la_sig", 6ull, &la_sig); if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rc = rllc_find_key_number(data, len, "ob_h2_obs", 9ull, &ob); if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rc = rllc_find_key_number(data, len, "ob_h2_sig", 9ull, &ob_sig); if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_FORMAT);
    rc = rllc_find_covariance(data, len, cov);
    if (rc != RLLC_OK) return rllc_reject(state, rc, RLLC_V_COVARIANCE);
    if (cov[0] <= 0ll || cov[4] <= 0ll || cov[8] <= 0ll) return rllc_reject(state, RLLC_E_COVARIANCE, RLLC_V_COVARIANCE);
    if (rllc_abs_i64(cov[1] - cov[3]) > 2ll || rllc_abs_i64(cov[2] - cov[6]) > 2ll || rllc_abs_i64(cov[5] - cov[7]) > 2ll) {
        return rllc_reject(state, RLLC_E_COVARIANCE, RLLC_V_COVARIANCE);
    }
    i = 0u;
    while (i < 9u) {
        state->cmb_covariance_q32[i] = cov[i];
        i++;
    }
    state->cmb_covariance_present = 1u;
    rc = rllc_emit_cmb(state, 1ull, RLLC_OBS_CMB_R, z, r, r_sig, sha256, len); if (rc != RLLC_OK) return rc;
    rc = rllc_emit_cmb(state, 2ull, RLLC_OBS_CMB_LA, z, la, la_sig, sha256, len); if (rc != RLLC_OK) return rc;
    return rllc_emit_cmb(state, 3ull, RLLC_OBS_CMB_OB_H2, z, ob, ob_sig, sha256, len);
}

int rllc_ingest_local_adapter_scalar(
    rllc_state *state,
    rllc_u64 sequence,
    rllc_i64 time_or_axis_q32,
    rllc_i64 value_q32,
    rllc_i64 sigma_q32,
    const rllc_u8 sha256[32],
    rllc_u64 adapter_name_fnv1a64,
    rllc_u32 adapter_name_crc32) {
    rllc_observation obs;
    if (state == (rllc_state *)0 || sha256 == (const rllc_u8 *)0) return RLLC_E_NULL;
    obs.schema = RLLC_SCHEMA_V1;
    obs.dataset = RLLC_DS_ADAPTER_LOCAL_PHYSICS;
    obs.observable = RLLC_OBS_ADAPTER_SCALAR;
    obs.unit = RLLC_UNIT_SI_DECLARED_BY_ADAPTER;
    obs.flags = RLLC_F_REAL | RLLC_F_PROVENANCE_VERIFIED | RLLC_F_CLAIM_BLOCKED | RLLC_F_LOCAL_CONTEXT_ONLY;
    obs.reserved = 0u;
    obs.sequence = sequence;
    obs.x_q32 = time_or_axis_q32;
    obs.value_q32 = value_q32;
    obs.sigma_q32 = sigma_q32;
    rllc_memcpy(obs.source.sha256, sha256, 32ull);
    obs.source.byte_count = 0ull;
    obs.source.source_name_fnv1a64 = adapter_name_fnv1a64;
    obs.source.source_name_crc32 = adapter_name_crc32;
    return rllc_ingest(state, &obs);
}

int rllc_finalize(const rllc_state *state, rllc_receipt *receipt) {
    rllc_u32 complete;
    int status;
    if (state == (const rllc_state *)0 || receipt == (rllc_receipt *)0) return RLLC_E_NULL;
    if (state->schema != RLLC_SCHEMA_V1) return RLLC_E_SCHEMA;
    complete = ((state->real_dataset_mask & RLLC_REQUIRED_DATASETS_MASK) == RLLC_REQUIRED_DATASETS_MASK) &&
               state->dataset_counts[RLLC_DS_HZ] != 0ull &&
               state->dataset_counts[RLLC_DS_BAO] != 0ull &&
               state->dataset_counts[RLLC_DS_FSIGMA8] != 0ull &&
               state->dataset_counts[RLLC_DS_CMB_SHIFT] == 3ull &&
               state->cmb_covariance_present == 1u;
    if (state->violation_mask != 0u) status = RLLC_E_SCHEMA;
    else if (complete == 0u) status = RLLC_TOKEN_VAZIO;
    else status = RLLC_OK;

    receipt->schema = RLLC_SCHEMA_V1;
    receipt->status = (rllc_u32)status;
    receipt->claim_allowed = 0u;
    receipt->violation_mask = state->violation_mask;
    receipt->real_dataset_mask = state->real_dataset_mask;
    receipt->required_dataset_mask = RLLC_REQUIRED_DATASETS_MASK;
    receipt->accepted = state->accepted;
    receipt->rejected = state->rejected;
    receipt->hz_rows = state->dataset_counts[RLLC_DS_HZ];
    receipt->bao_rows = state->dataset_counts[RLLC_DS_BAO];
    receipt->fsigma8_rows = state->dataset_counts[RLLC_DS_FSIGMA8];
    receipt->cmb_rows = state->dataset_counts[RLLC_DS_CMB_SHIFT];
    receipt->rolling_fnv1a64 = state->rolling_fnv1a64;
    receipt->rolling_crc32 = state->rolling_crc32;
    receipt->covariance_present = state->cmb_covariance_present;
    return status;
}
