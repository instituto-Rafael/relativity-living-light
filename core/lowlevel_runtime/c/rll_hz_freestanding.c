#include "rll_hz_freestanding.h"

#define RLL_LN2_Q16 45426ll
#define RLL_HALF_LN2_Q16 22713ll
#define RLL_EXP_LIMIT_Q16 (16ll * RLL_Q16_ONE)
#define RLL_I64_MAX 0x7FFFFFFFFFFFFFFFll
#define RLL_I64_MIN (-RLL_I64_MAX - 1ll)
#define RLL_COSMO_FLAGS \
    (RLL_OBS_CALIBRATED | RLL_OBS_RAW_HASHED | \
     RLL_OBS_UNCERTAINTY_VALID | RLL_OBS_MODEL_REGISTERED)

static rll_i64 rll_q16_mul(rll_i64 a, rll_i64 b) {
    return (a * b) >> 16;
}

static rll_i64 rll_q16_div(rll_i64 a, rll_i64 b) {
    if (b == 0ll) {
        return (a < 0ll) ? RLL_I64_MIN : RLL_I64_MAX;
    }
    if ((a > (RLL_I64_MAX >> 16)) || (a < (RLL_I64_MIN >> 16))) {
        return (a < 0ll) ? RLL_I64_MIN : RLL_I64_MAX;
    }
    return (a << 16) / b;
}

static rll_u64 rll_isqrt_u64(rll_u64 n) {
    rll_u64 result = 0ull;
    rll_u64 bit = 1ull << 62;
    while (bit > n) {
        bit >>= 2;
    }
    while (bit != 0ull) {
        if (n >= result + bit) {
            n -= result + bit;
            result = (result >> 1) + bit;
        } else {
            result >>= 1;
        }
        bit >>= 2;
    }
    return result;
}

static rll_i64 rll_sqrt_q16(rll_i64 x_q16) {
    if (x_q16 <= 0ll) {
        return 0ll;
    }
    return (rll_i64)rll_isqrt_u64(((rll_u64)x_q16) << 16);
}

static rll_i64 rll_exp_q16(rll_i64 x_q16) {
    rll_i64 k;
    rll_i64 r;
    rll_i64 r2;
    rll_i64 r3;
    rll_i64 r4;
    rll_i64 r5;
    rll_i64 p;
    if (x_q16 >= RLL_EXP_LIMIT_Q16) {
        return RLL_I64_MAX;
    }
    if (x_q16 <= -RLL_EXP_LIMIT_Q16) {
        return 0ll;
    }
    if (x_q16 >= 0ll) {
        k = (x_q16 + RLL_HALF_LN2_Q16) / RLL_LN2_Q16;
    } else {
        k = -(((-x_q16) + RLL_HALF_LN2_Q16) / RLL_LN2_Q16);
    }
    r = x_q16 - (k * RLL_LN2_Q16);
    r2 = rll_q16_mul(r, r);
    r3 = rll_q16_mul(r2, r);
    r4 = rll_q16_mul(r3, r);
    r5 = rll_q16_mul(r4, r);
    p = RLL_Q16_ONE + r + (r2 / 2ll) + (r3 / 6ll) +
        (r4 / 24ll) + (r5 / 120ll);
    if (k >= 0ll) {
        if ((k >= 31ll) || (p > (RLL_I64_MAX >> k))) {
            return RLL_I64_MAX;
        }
        return p << k;
    }
    if (k <= -63ll) {
        return 0ll;
    }
    return p >> (-k);
}

static rll_i64 rll_rll_fraction_q16(
    rll_i64 z_q16,
    const rll_hz_params_q16 *params
) {
    rll_i64 arg_q16 = rll_q16_div(
        z_q16 - params->z_t_q16,
        params->w_t_q16
    );
    rll_i64 exp_q16 = rll_exp_q16(arg_q16);
    return rll_q16_div(RLL_Q16_ONE, RLL_Q16_ONE + exp_q16);
}

rll_hz_params_q16 rll_hz_nominal_planck_params_q16(void) {
    rll_hz_params_q16 params;
    params.h0_q16 = 4417126ll;       /* 67.4 */
    params.omega_m_q16 = 20644ll;    /* 0.315 */
    params.omega_s0_q16 = 1311ll;    /* 0.02 */
    params.z_t_q16 = 65536ll;        /* 1.0 */
    params.w_t_q16 = 19661ll;        /* 0.3 */
    return params;
}

rll_i64 rll_hz_lcdm_q16(
    rll_i64 z_q16,
    const rll_hz_params_q16 *params
) {
    rll_i64 one_plus_z;
    rll_i64 a2;
    rll_i64 a3;
    rll_i64 e2;
    if ((params == (const rll_hz_params_q16 *)0) || (z_q16 < 0ll)) {
        return 0ll;
    }
    one_plus_z = RLL_Q16_ONE + z_q16;
    a2 = rll_q16_mul(one_plus_z, one_plus_z);
    a3 = rll_q16_mul(a2, one_plus_z);
    e2 = rll_q16_mul(params->omega_m_q16, a3) +
         (RLL_Q16_ONE - params->omega_m_q16);
    return rll_q16_mul(params->h0_q16, rll_sqrt_q16(e2));
}

rll_i64 rll_hz_rll_q16(
    rll_i64 z_q16,
    const rll_hz_params_q16 *params
) {
    rll_i64 one_plus_z;
    rll_i64 a2;
    rll_i64 a3;
    rll_i64 fz;
    rll_i64 omega_l;
    rll_i64 transition_term;
    rll_i64 e2;
    if ((params == (const rll_hz_params_q16 *)0) ||
        (z_q16 < 0ll) || (params->w_t_q16 <= 0ll)) {
        return 0ll;
    }
    one_plus_z = RLL_Q16_ONE + z_q16;
    a2 = rll_q16_mul(one_plus_z, one_plus_z);
    a3 = rll_q16_mul(a2, one_plus_z);
    fz = rll_rll_fraction_q16(z_q16, params);
    omega_l = RLL_Q16_ONE - params->omega_m_q16 - params->omega_s0_q16;
    transition_term = fz + rll_q16_mul(RLL_Q16_ONE - fz, a3);
    e2 = rll_q16_mul(params->omega_m_q16, a3) + omega_l +
         rll_q16_mul(params->omega_s0_q16, transition_term);
    return rll_q16_mul(params->h0_q16, rll_sqrt_q16(e2));
}

rll_hz_dual_receipt rll_hz_run_canonical_q16(
    const rll_hz_sample_q16 *samples,
    rll_u32 count,
    const rll_hz_params_q16 *params,
    rll_u64 dataset_fnv1a64,
    rll_u32 dataset_crc32
) {
    rll_hz_dual_receipt out;
    rll_canonical_accumulator lcdm_acc;
    rll_canonical_accumulator rll_acc;
    rll_u32 i = 0u;
    rll_canonical_init(&lcdm_acc, RLL_REGION_COSMOLOGY_EVIDENCE);
    rll_canonical_init(&rll_acc, RLL_REGION_COSMOLOGY_EVIDENCE);
    while ((samples != (const rll_hz_sample_q16 *)0) &&
           (params != (const rll_hz_params_q16 *)0) &&
           (i < count)) {
        rll_canonical_observation observation;
        observation.domain = RLL_DOMAIN_COSMOLOGY;
        observation.quantity = RLL_Q_HUBBLE;
        observation.unit = RLL_UNIT_KM_S_MPC;
        observation.state = RLL_STATE_OBSERVED;
        observation.value_q16 = samples[i].h_obs_q16;
        observation.sigma_q16 = samples[i].sigma_q16;
        observation.sample_count = (rll_u64)count;
        observation.flags = RLL_COSMO_FLAGS;
        observation.sequence_id = samples[i].sequence_id;
        observation.source_fnv1a64 = dataset_fnv1a64;
        observation.source_crc32 = dataset_crc32;
        observation.model_q16 = rll_hz_lcdm_q16(samples[i].z_q16, params);
        (void)rll_canonical_push(&lcdm_acc, &observation);
        observation.model_q16 = rll_hz_rll_q16(samples[i].z_q16, params);
        (void)rll_canonical_push(&rll_acc, &observation);
        i++;
    }
    out.lcdm = rll_canonical_snapshot(&lcdm_acc);
    out.rll = rll_canonical_snapshot(&rll_acc);
    out.delta_chi2_q16 = out.rll.chi2_q16 - out.lcdm.chi2_q16;
    out.rows = count;
    out.dataset_fnv1a64 = dataset_fnv1a64;
    out.dataset_crc32 = dataset_crc32;
    out.claim_allowed = 0u;
    return out;
}

rll_hz_dual_receipt rll_hz_run_moresco_nominal_q16(void) {
    rll_hz_params_q16 params = rll_hz_nominal_planck_params_q16();
    return rll_hz_run_canonical_q16(
        rll_hz_moresco_2022_q16,
        RLL_HZ_DATASET_ROWS,
        &params,
        RLL_HZ_DATASET_FNV1A64,
        RLL_HZ_DATASET_CRC32
    );
}
