#include "rll_canonical_freestanding.h"

#define RLLC_I32_MAX 2147483647
#define RLLC_I32_MIN (-2147483647 - 1)

#define RLLC_FNV_OFFSET 14695981039346656037ull
#define RLLC_FNV_PRIME  1099511628211ull
#define RLLC_CRC_INIT   0xFFFFFFFFu
#define RLLC_CRC_POLY   0xEDB88320u
#define RLLC_CRC_XOR    0xFFFFFFFFu

#define RLLC_LN2_Q16       45426
#define RLLC_EXP_LIMIT_Q16 (10 * RLLC_Q16_ONE)

typedef struct rllc_hash_state {
    rllc_u64 fnv;
    rllc_u32 crc;
} rllc_hash_state;

static rllc_u32 rllc_abs_u32(rllc_i32 value) {
    rllc_u32 x = (rllc_u32)value;
    rllc_u32 mask = (rllc_u32)(value >> 31);
    return (x ^ mask) - mask;
}

static rllc_u64 rllc_abs_u64(rllc_i64 value) {
    rllc_u64 x = (rllc_u64)value;
    rllc_u64 mask = (rllc_u64)(value >> 63);
    return (x ^ mask) - mask;
}

/* Software 64/32 division: no compiler/runtime division helper is required. */
static rllc_u64 rllc_udivmod_u64_u32(
    rllc_u64 numerator,
    rllc_u32 denominator,
    rllc_u32 *remainder
) {
    rllc_u64 quotient = 0ull;
    rllc_u64 rem = 0ull;
    rllc_i32 bit = 63;

    if (denominator == 0u) {
        if (remainder != (rllc_u32 *)0) {
            *remainder = 0u;
        }
        return ~0ull;
    }

    while (bit >= 0) {
        rem = (rem << 1u) | ((numerator >> (rllc_u32)bit) & 1ull);
        if (rem >= (rllc_u64)denominator) {
            rem -= (rllc_u64)denominator;
            quotient |= 1ull << (rllc_u32)bit;
        }
        bit--;
    }

    if (remainder != (rllc_u32 *)0) {
        *remainder = (rllc_u32)rem;
    }
    return quotient;
}

static rllc_i32 rllc_div_i32(rllc_i32 numerator, rllc_i32 denominator, rllc_u32 *flags) {
    rllc_u32 sign;
    rllc_u32 n;
    rllc_u32 d;
    rllc_u64 q;

    if (denominator == 0) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_DIV_ZERO;
        }
        return (numerator < 0) ? RLLC_I32_MIN : RLLC_I32_MAX;
    }

    sign = (rllc_u32)((numerator ^ denominator) >> 31);
    n = rllc_abs_u32(numerator);
    d = rllc_abs_u32(denominator);
    q = rllc_udivmod_u64_u32((rllc_u64)n, d, (rllc_u32 *)0);

    if (q > 2147483648ull) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_SATURATED;
        }
        return (sign != 0u) ? RLLC_I32_MIN : RLLC_I32_MAX;
    }

    if (sign != 0u) {
        if (q == 2147483648ull) {
            return RLLC_I32_MIN;
        }
        return -(rllc_i32)q;
    }
    if (q > 2147483647ull) {
        return RLLC_I32_MAX;
    }
    return (rllc_i32)q;
}

static rllc_i32 rllc_sat_i64_to_i32(rllc_i64 value, rllc_u32 *flags) {
    if (value > (rllc_i64)RLLC_I32_MAX) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_SATURATED;
        }
        return RLLC_I32_MAX;
    }
    if (value < (rllc_i64)RLLC_I32_MIN) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_SATURATED;
        }
        return RLLC_I32_MIN;
    }
    return (rllc_i32)value;
}

static rllc_i32 rllc_q16_mul(rllc_i32 a, rllc_i32 b, rllc_u32 *flags) {
    rllc_i64 product = (rllc_i64)a * (rllc_i64)b;
    return rllc_sat_i64_to_i32(product >> 16u, flags);
}

static rllc_i32 rllc_q16_div(rllc_i32 numerator, rllc_i32 denominator, rllc_u32 *flags) {
    rllc_u32 sign;
    rllc_u64 n;
    rllc_u32 d;
    rllc_u64 q;

    if (denominator == 0) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_DIV_ZERO;
        }
        return (numerator < 0) ? RLLC_I32_MIN : RLLC_I32_MAX;
    }

    sign = (rllc_u32)((numerator ^ denominator) >> 31);
    n = ((rllc_u64)rllc_abs_u32(numerator)) << 16u;
    d = rllc_abs_u32(denominator);
    q = rllc_udivmod_u64_u32(n, d, (rllc_u32 *)0);

    if (q > 2147483648ull) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_SATURATED;
        }
        return (sign != 0u) ? RLLC_I32_MIN : RLLC_I32_MAX;
    }

    if (sign != 0u) {
        if (q == 2147483648ull) {
            return RLLC_I32_MIN;
        }
        return -(rllc_i32)q;
    }
    if (q > 2147483647ull) {
        return RLLC_I32_MAX;
    }
    return (rllc_i32)q;
}

static rllc_u64 rllc_isqrt_u64(rllc_u64 value) {
    rllc_u64 result = 0ull;
    rllc_u64 bit = 1ull << 62u;

    while (bit > value) {
        bit >>= 2u;
    }

    while (bit != 0ull) {
        if (value >= result + bit) {
            value -= result + bit;
            result = (result >> 1u) + bit;
        } else {
            result >>= 1u;
        }
        bit >>= 2u;
    }
    return result;
}

static rllc_i32 rllc_q16_sqrt(rllc_i32 value, rllc_u32 *flags) {
    rllc_u64 root;
    if (value < 0) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_NEGATIVE_E2;
        }
        return 0;
    }
    root = rllc_isqrt_u64(((rllc_u64)(rllc_u32)value) << 16u);
    if (root > (rllc_u64)RLLC_I32_MAX) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_SATURATED;
        }
        return RLLC_I32_MAX;
    }
    return (rllc_i32)root;
}

/* exp(x), x in Q16.16. Range reduction by ln(2), 6th-order Taylor. */
static rllc_i32 rllc_exp_q16(rllc_i32 x, rllc_u32 *flags) {
    rllc_i32 k;
    rllc_i32 r;
    rllc_i32 term;
    rllc_i32 sum;
    rllc_i32 n;

    if (x <= -RLLC_EXP_LIMIT_Q16) {
        return 3; /* ~= exp(-10) in Q16.16 */
    }
    if (x >= RLLC_EXP_LIMIT_Q16) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_SATURATED;
        }
        return 1443549184; /* round(exp(10) * 65536) */
    }

    k = rllc_div_i32(x, RLLC_LN2_Q16, flags);
    r = x - (k * RLLC_LN2_Q16);

    term = RLLC_Q16_ONE;
    sum = RLLC_Q16_ONE;
    n = 1;
    while (n <= 6) {
        term = rllc_q16_mul(term, r, flags);
        term = rllc_div_i32(term, n, flags);
        sum = rllc_sat_i64_to_i32((rllc_i64)sum + (rllc_i64)term, flags);
        n++;
    }

    if (k > 0) {
        if (k >= 15) {
            if (flags != (rllc_u32 *)0) {
                *flags |= RLLC_NUMERIC_SATURATED;
            }
            return RLLC_I32_MAX;
        }
        return rllc_sat_i64_to_i32(((rllc_i64)sum) << (rllc_u32)k, flags);
    }
    if (k < 0) {
        rllc_i32 shift = -k;
        if (shift >= 31) {
            return 0;
        }
        return sum >> (rllc_u32)shift;
    }
    return sum;
}

static rllc_i32 rllc_transition_f_q16(
    rllc_i32 z_q16,
    const rllc_phase20_params_q16 *params,
    rllc_u32 *flags
) {
    rllc_i32 x;
    rllc_i32 exp_x;
    rllc_i32 denom;

    x = rllc_q16_div(z_q16 - params->z_t_q16, params->w_t_q16, flags);
    exp_x = rllc_exp_q16(x, flags);
    denom = rllc_sat_i64_to_i32((rllc_i64)RLLC_Q16_ONE + (rllc_i64)exp_x, flags);
    return rllc_q16_div(RLLC_Q16_ONE, denom, flags);
}

static rllc_i32 rllc_hubble_model_q16(
    rllc_i32 z_q16,
    const rllc_phase20_params_q16 *params,
    rllc_u32 use_rll,
    rllc_u32 *flags
) {
    rllc_i32 one_plus_z;
    rllc_i32 one_plus_z2;
    rllc_i32 one_plus_z3;
    rllc_i32 omega_lambda;
    rllc_i32 e2;
    rllc_i32 matter;
    rllc_i32 transition;
    rllc_i32 sector;
    rllc_i32 root;

    if ((params == (const rllc_phase20_params_q16 *)0) || (z_q16 < 0)) {
        if (flags != (rllc_u32 *)0) {
            *flags |= RLLC_NUMERIC_INVALID_SAMPLE;
        }
        return 0;
    }

    one_plus_z = rllc_sat_i64_to_i32((rllc_i64)RLLC_Q16_ONE + (rllc_i64)z_q16, flags);
    one_plus_z2 = rllc_q16_mul(one_plus_z, one_plus_z, flags);
    one_plus_z3 = rllc_q16_mul(one_plus_z2, one_plus_z, flags);
    matter = rllc_q16_mul(params->omega_m_q16, one_plus_z3, flags);

    if (use_rll != 0u) {
        omega_lambda = RLLC_Q16_ONE - params->omega_m_q16 - params->omega_s0_q16;
        transition = rllc_transition_f_q16(z_q16, params, flags);
        sector = transition + rllc_q16_mul(
            RLLC_Q16_ONE - transition,
            one_plus_z3,
            flags
        );
        e2 = matter + omega_lambda + rllc_q16_mul(params->omega_s0_q16, sector, flags);
    } else {
        omega_lambda = RLLC_Q16_ONE - params->omega_m_q16;
        e2 = matter + omega_lambda;
    }

    root = rllc_q16_sqrt(e2, flags);
    return rllc_q16_mul(params->h0_q16, root, flags);
}

static void rllc_hash_init(rllc_hash_state *state) {
    state->fnv = RLLC_FNV_OFFSET;
    state->crc = RLLC_CRC_INIT;
}

static void rllc_hash_byte(rllc_hash_state *state, rllc_u8 byte) {
    rllc_u32 x;
    rllc_u32 j;

    state->fnv ^= (rllc_u64)byte;
    state->fnv *= RLLC_FNV_PRIME;

    x = (state->crc ^ (rllc_u32)byte) & 0xFFu;
    j = 0u;
    while (j < 8u) {
        rllc_u32 mask = (rllc_u32)(-(rllc_i32)(x & 1u));
        x = (x >> 1u) ^ (RLLC_CRC_POLY & mask);
        j++;
    }
    state->crc = (state->crc >> 8u) ^ x;
}

static void rllc_hash_u32_le(rllc_hash_state *state, rllc_u32 value) {
    rllc_hash_byte(state, (rllc_u8)(value & 0xFFu));
    rllc_hash_byte(state, (rllc_u8)((value >> 8u) & 0xFFu));
    rllc_hash_byte(state, (rllc_u8)((value >> 16u) & 0xFFu));
    rllc_hash_byte(state, (rllc_u8)((value >> 24u) & 0xFFu));
}

static void rllc_hash_u64_le(rllc_hash_state *state, rllc_u64 value) {
    rllc_u32 i = 0u;
    while (i < 8u) {
        rllc_hash_byte(state, (rllc_u8)((value >> (i * 8u)) & 0xFFull));
        i++;
    }
}

static rllc_u32 rllc_hash_crc_final(const rllc_hash_state *state) {
    return state->crc ^ RLLC_CRC_XOR;
}

static void rllc_hash_samples(
    const rllc_hz_sample_q16 *samples,
    rllc_u32 count,
    rllc_u32 *crc,
    rllc_u64 *fnv
) {
    rllc_hash_state state;
    rllc_u32 i = 0u;
    rllc_hash_init(&state);
    while (i < count) {
        rllc_hash_u32_le(&state, (rllc_u32)samples[i].z_q16);
        rllc_hash_u32_le(&state, (rllc_u32)samples[i].h_obs_q16);
        rllc_hash_u32_le(&state, (rllc_u32)samples[i].sigma_h_q16);
        rllc_hash_u32_le(&state, samples[i].source_id);
        i++;
    }
    *crc = rllc_hash_crc_final(&state);
    *fnv = state.fnv;
}

static void rllc_hash_params(
    const rllc_phase20_params_q16 *params,
    rllc_u32 *crc,
    rllc_u64 *fnv
) {
    rllc_hash_state state;
    rllc_hash_init(&state);
    rllc_hash_u32_le(&state, (rllc_u32)params->h0_q16);
    rllc_hash_u32_le(&state, (rllc_u32)params->omega_m_q16);
    rllc_hash_u32_le(&state, (rllc_u32)params->omega_b_q16);
    rllc_hash_u32_le(&state, (rllc_u32)params->omega_s0_q16);
    rllc_hash_u32_le(&state, (rllc_u32)params->z_t_q16);
    rllc_hash_u32_le(&state, (rllc_u32)params->w_t_q16);
    *crc = rllc_hash_crc_final(&state);
    *fnv = state.fnv;
}

static rllc_u32 rllc_receipt_crc(const rllc_receipt_v1 *receipt) {
    rllc_hash_state state;
    rllc_hash_init(&state);
    rllc_hash_u32_le(&state, receipt->abi_version);
    rllc_hash_u32_le(&state, receipt->row_count);
    rllc_hash_u32_le(&state, receipt->valid_count);
    rllc_hash_u32_le(&state, receipt->rejected_count);
    rllc_hash_u32_le(&state, receipt->data_crc32);
    rllc_hash_u32_le(&state, receipt->params_crc32);
    rllc_hash_u64_le(&state, receipt->data_fnv1a64);
    rllc_hash_u64_le(&state, receipt->params_fnv1a64);
    rllc_hash_u32_le(&state, receipt->phase20_summary_crc32);
    rllc_hash_u32_le(&state, receipt->phase20_n_total);
    rllc_hash_u32_le(&state, (rllc_u32)receipt->phase20_ln_b10_q16);
    rllc_hash_u32_le(&state, (rllc_u32)receipt->phase20_ln_b10_err_q16);
    rllc_hash_u32_le(&state, (rllc_u32)receipt->phase20_delta_bic_q16);
    rllc_hash_u32_le(&state, (rllc_u32)receipt->phase20_os0_upper95_q16);
    rllc_hash_u32_le(&state, receipt->phase20_joint_best_model);
    rllc_hash_u64_le(&state, receipt->chi2_rll_q16);
    rllc_hash_u64_le(&state, receipt->chi2_lcdm_q16);
    rllc_hash_u64_le(&state, (rllc_u64)receipt->delta_chi2_rll_minus_lcdm_q16);
    rllc_hash_u32_le(&state, receipt->best_model);
    rllc_hash_u32_le(&state, receipt->claim_allowed);
    rllc_hash_u32_le(&state, receipt->token_vazio_mask);
    rllc_hash_u32_le(&state, receipt->numeric_flags);
    return rllc_hash_crc_final(&state);
}

void rllc_phase20_default_params(rllc_phase20_params_q16 *out) {
    if (out == (rllc_phase20_params_q16 *)0) {
        return;
    }

    /* FASE 20 posterior means from results/rll_fase20_mcmc_bayes.json. */
    out->h0_q16       = 4384137; /* 66.89662043032884 */
    out->omega_m_q16  = 20603;   /* 0.3143746952449269 */
    out->omega_b_q16  = 3264;    /* 0.049798276368180995 */
    out->omega_s0_q16 = 38;      /* 0.0005722653892687908 */
    out->z_t_q16      = 727496;  /* 11.100703006674221 */
    out->w_t_q16      = 66700;   /* 1.0177609039997741 */
}

rllc_i32 rllc_hubble_lcdm_q16(
    rllc_i32 z_q16,
    const rllc_phase20_params_q16 *params,
    rllc_u32 *numeric_flags
) {
    return rllc_hubble_model_q16(z_q16, params, 0u, numeric_flags);
}

rllc_i32 rllc_hubble_rll_q16(
    rllc_i32 z_q16,
    const rllc_phase20_params_q16 *params,
    rllc_u32 *numeric_flags
) {
    return rllc_hubble_model_q16(z_q16, params, 1u, numeric_flags);
}

void rllc_evaluate_canonical_hz(
    const rllc_hz_sample_q16 *samples,
    rllc_u32 count,
    const rllc_phase20_params_q16 *params,
    rllc_receipt_v1 *out
) {
    rllc_u32 i;
    rllc_u32 flags;
    rllc_u64 chi2_rll;
    rllc_u64 chi2_lcdm;

    if (out == (rllc_receipt_v1 *)0) {
        return;
    }

    out->abi_version = RLLC_ABI_VERSION;
    out->row_count = count;
    out->valid_count = 0u;
    out->rejected_count = 0u;
    out->data_crc32 = 0u;
    out->params_crc32 = 0u;
    out->data_fnv1a64 = 0ull;
    out->params_fnv1a64 = 0ull;
    out->phase20_summary_crc32 = 0u;
    out->phase20_n_total = 1677u;
    out->phase20_ln_b10_q16 = -405682;
    out->phase20_ln_b10_err_q16 = 45263;
    out->phase20_delta_bic_q16 = 1459487;
    out->phase20_os0_upper95_q16 = 116;
    out->phase20_joint_best_model = RLLC_BEST_LCDM;
    out->chi2_rll_q16 = 0ull;
    out->chi2_lcdm_q16 = 0ull;
    out->delta_chi2_rll_minus_lcdm_q16 = 0ll;
    out->best_model = RLLC_BEST_TIE;
    out->claim_allowed = RLLC_CLAIM_ALLOWED_FALSE;
    out->token_vazio_mask =
        RLLC_TV_FULL_COVARIANCE |
        RLLC_TV_INDEPENDENT_REPL |
        RLLC_TV_EXTERNAL_BIN_AUDIT;
    out->numeric_flags = 0u;
    out->receipt_crc32 = 0u;

    if ((samples == (const rllc_hz_sample_q16 *)0) ||
        (params == (const rllc_phase20_params_q16 *)0)) {
        out->numeric_flags |= RLLC_NUMERIC_INVALID_SAMPLE;
        out->rejected_count = count;
        out->receipt_crc32 = rllc_receipt_crc(out);
        return;
    }

    rllc_hash_samples(samples, count, &out->data_crc32, &out->data_fnv1a64);
    rllc_hash_params(params, &out->params_crc32, &out->params_fnv1a64);
    {
        rllc_hash_state phase20_state;
        rllc_hash_init(&phase20_state);
        rllc_hash_u32_le(&phase20_state, out->phase20_n_total);
        rllc_hash_u32_le(&phase20_state, (rllc_u32)out->phase20_ln_b10_q16);
        rllc_hash_u32_le(&phase20_state, (rllc_u32)out->phase20_ln_b10_err_q16);
        rllc_hash_u32_le(&phase20_state, (rllc_u32)out->phase20_delta_bic_q16);
        rllc_hash_u32_le(&phase20_state, (rllc_u32)out->phase20_os0_upper95_q16);
        rllc_hash_u32_le(&phase20_state, out->phase20_joint_best_model);
        out->phase20_summary_crc32 = rllc_hash_crc_final(&phase20_state);
    }

    i = 0u;
    flags = 0u;
    chi2_rll = 0ull;
    chi2_lcdm = 0ull;

    while (i < count) {
        rllc_i32 pred_rll;
        rllc_i32 pred_lcdm;
        rllc_i32 norm_rll;
        rllc_i32 norm_lcdm;
        rllc_i32 term_rll;
        rllc_i32 term_lcdm;

        if ((samples[i].z_q16 < 0) ||
            (samples[i].h_obs_q16 <= 0) ||
            (samples[i].sigma_h_q16 <= 0) ||
            (samples[i].source_id < RLLC_SOURCE_CC_MORESCO_2022) ||
            (samples[i].source_id > RLLC_SOURCE_BAO_LYA)) {
            out->rejected_count++;
            flags |= RLLC_NUMERIC_INVALID_SAMPLE;
            i++;
            continue;
        }

        pred_rll = rllc_hubble_rll_q16(samples[i].z_q16, params, &flags);
        pred_lcdm = rllc_hubble_lcdm_q16(samples[i].z_q16, params, &flags);

        norm_rll = rllc_q16_div(samples[i].h_obs_q16 - pred_rll, samples[i].sigma_h_q16, &flags);
        norm_lcdm = rllc_q16_div(samples[i].h_obs_q16 - pred_lcdm, samples[i].sigma_h_q16, &flags);

        term_rll = rllc_q16_mul(norm_rll, norm_rll, &flags);
        term_lcdm = rllc_q16_mul(norm_lcdm, norm_lcdm, &flags);

        chi2_rll += (rllc_u64)(rllc_u32)term_rll;
        chi2_lcdm += (rllc_u64)(rllc_u32)term_lcdm;
        out->valid_count++;
        i++;
    }

    out->chi2_rll_q16 = chi2_rll;
    out->chi2_lcdm_q16 = chi2_lcdm;
    if (chi2_rll >= chi2_lcdm) {
        out->delta_chi2_rll_minus_lcdm_q16 = (rllc_i64)(chi2_rll - chi2_lcdm);
        out->best_model = (chi2_rll == chi2_lcdm) ? RLLC_BEST_TIE : RLLC_BEST_LCDM;
    } else {
        out->delta_chi2_rll_minus_lcdm_q16 = -(rllc_i64)(chi2_lcdm - chi2_rll);
        out->best_model = RLLC_BEST_RLL;
    }

    out->numeric_flags = flags;
    out->receipt_crc32 = rllc_receipt_crc(out);
}

/* ---------- deterministic text receipt ---------- */

static rllc_u32 rllc_append_char(char *out, rllc_u32 cap, rllc_u32 pos, char value) {
    if (pos < cap) {
        out[pos] = value;
    }
    return pos + 1u;
}

static rllc_u32 rllc_append_text(char *out, rllc_u32 cap, rllc_u32 pos, const char *text) {
    rllc_u32 i = 0u;
    while (text[i] != '\0') {
        pos = rllc_append_char(out, cap, pos, text[i]);
        i++;
    }
    return pos;
}

static rllc_u32 rllc_append_u64_dec(char *out, rllc_u32 cap, rllc_u32 pos, rllc_u64 value) {
    char reverse[24];
    rllc_u32 n = 0u;

    if (value == 0ull) {
        return rllc_append_char(out, cap, pos, '0');
    }

    while (value != 0ull) {
        rllc_u32 rem = 0u;
        value = rllc_udivmod_u64_u32(value, 10u, &rem);
        reverse[n] = (char)('0' + rem);
        n++;
    }

    while (n != 0u) {
        n--;
        pos = rllc_append_char(out, cap, pos, reverse[n]);
    }
    return pos;
}

static rllc_u32 rllc_append_i64_dec(char *out, rllc_u32 cap, rllc_u32 pos, rllc_i64 value) {
    if (value < 0ll) {
        pos = rllc_append_char(out, cap, pos, '-');
        return rllc_append_u64_dec(out, cap, pos, rllc_abs_u64(value));
    }
    return rllc_append_u64_dec(out, cap, pos, (rllc_u64)value);
}

static rllc_u32 rllc_append_u32_hex(char *out, rllc_u32 cap, rllc_u32 pos, rllc_u32 value) {
    static const char hex[] = "0123456789abcdef";
    rllc_i32 shift = 28;
    while (shift >= 0) {
        pos = rllc_append_char(out, cap, pos, hex[(value >> (rllc_u32)shift) & 0xFu]);
        shift -= 4;
    }
    return pos;
}

static rllc_u32 rllc_append_u64_hex(char *out, rllc_u32 cap, rllc_u32 pos, rllc_u64 value) {
    static const char hex[] = "0123456789abcdef";
    rllc_i32 shift = 60;
    while (shift >= 0) {
        pos = rllc_append_char(out, cap, pos, hex[(rllc_u32)((value >> (rllc_u32)shift) & 0xFull)]);
        shift -= 4;
    }
    return pos;
}

rllc_u32 rllc_format_receipt_line(
    const rllc_receipt_v1 *receipt,
    char *out,
    rllc_u32 capacity
) {
    rllc_u32 pos = 0u;
    const char *best;

    if ((receipt == (const rllc_receipt_v1 *)0) ||
        (out == (char *)0) ||
        (capacity == 0u)) {
        return 0u;
    }

    if (receipt->best_model == RLLC_BEST_LCDM) {
        best = "LCDM";
    } else if (receipt->best_model == RLLC_BEST_RLL) {
        best = "RLL";
    } else {
        best = "TIE";
    }

    pos = rllc_append_text(out, capacity, pos, "RLLCAN1 rows=");
    pos = rllc_append_u64_dec(out, capacity, pos, receipt->row_count);
    pos = rllc_append_text(out, capacity, pos, " valid=");
    pos = rllc_append_u64_dec(out, capacity, pos, receipt->valid_count);
    pos = rllc_append_text(out, capacity, pos, " rejected=");
    pos = rllc_append_u64_dec(out, capacity, pos, receipt->rejected_count);
    pos = rllc_append_text(out, capacity, pos, " chi2_rll_q16=");
    pos = rllc_append_u64_dec(out, capacity, pos, receipt->chi2_rll_q16);
    pos = rllc_append_text(out, capacity, pos, " chi2_lcdm_q16=");
    pos = rllc_append_u64_dec(out, capacity, pos, receipt->chi2_lcdm_q16);
    pos = rllc_append_text(out, capacity, pos, " delta_q16=");
    pos = rllc_append_i64_dec(out, capacity, pos, receipt->delta_chi2_rll_minus_lcdm_q16);
    pos = rllc_append_text(out, capacity, pos, " data_crc32=");
    pos = rllc_append_u32_hex(out, capacity, pos, receipt->data_crc32);
    pos = rllc_append_text(out, capacity, pos, " data_fnv64=");
    pos = rllc_append_u64_hex(out, capacity, pos, receipt->data_fnv1a64);
    pos = rllc_append_text(out, capacity, pos, " params_crc32=");
    pos = rllc_append_u32_hex(out, capacity, pos, receipt->params_crc32);
    pos = rllc_append_text(out, capacity, pos, " phase20_crc32=");
    pos = rllc_append_u32_hex(out, capacity, pos, receipt->phase20_summary_crc32);
    pos = rllc_append_text(out, capacity, pos, " joint_n=");
    pos = rllc_append_u64_dec(out, capacity, pos, receipt->phase20_n_total);
    pos = rllc_append_text(out, capacity, pos, " lnB10_q16=");
    pos = rllc_append_i64_dec(out, capacity, pos, receipt->phase20_ln_b10_q16);
    pos = rllc_append_text(out, capacity, pos, " lnB10_err_q16=");
    pos = rllc_append_i64_dec(out, capacity, pos, receipt->phase20_ln_b10_err_q16);
    pos = rllc_append_text(out, capacity, pos, " delta_bic_q16=");
    pos = rllc_append_i64_dec(out, capacity, pos, receipt->phase20_delta_bic_q16);
    pos = rllc_append_text(out, capacity, pos, " os0_ul95_q16=");
    pos = rllc_append_i64_dec(out, capacity, pos, receipt->phase20_os0_upper95_q16);
    pos = rllc_append_text(out, capacity, pos, " joint_best=LCDM");
    pos = rllc_append_text(out, capacity, pos, " receipt_crc32=");
    pos = rllc_append_u32_hex(out, capacity, pos, receipt->receipt_crc32);
    pos = rllc_append_text(out, capacity, pos, " best=");
    pos = rllc_append_text(out, capacity, pos, best);
    pos = rllc_append_text(out, capacity, pos, " claim_allowed=");
    pos = rllc_append_u64_dec(out, capacity, pos, receipt->claim_allowed);
    pos = rllc_append_text(out, capacity, pos, " token_vazio=");
    pos = rllc_append_u64_dec(out, capacity, pos, receipt->token_vazio_mask);
    pos = rllc_append_text(out, capacity, pos, " numeric_flags=");
    pos = rllc_append_u64_dec(out, capacity, pos, receipt->numeric_flags);
    pos = rllc_append_char(out, capacity, pos, '\n');

    if (pos > capacity) {
        return capacity;
    }
    return pos;
}
