#include "rll_canonical_coupling.h"

#define RLL_FNV_OFFSET 14695981039346656037ull
#define RLL_FNV_PRIME 1099511628211ull
#define RLL_CRC32_INIT 0xFFFFFFFFu
#define RLL_CRC32_POLY_REV 0xEDB88320u
#define RLL_CRC32_FINAL_XOR 0xFFFFFFFFu
#define RLL_I64_MAX 0x7FFFFFFFFFFFFFFFll
#define RLL_I64_MIN (-RLL_I64_MAX - 1ll)
#define RLL_SQRT_I64_MAX 3037000499ll

#define RLL_COSMO_REQUIRED_FLAGS \
    (RLL_OBS_CALIBRATED | RLL_OBS_RAW_HASHED | \
     RLL_OBS_UNCERTAINTY_VALID | RLL_OBS_MODEL_REGISTERED)

#define RLL_LOCAL_REQUIRED_FLAGS \
    (RLL_OBS_CALIBRATED | RLL_OBS_CLOCK_SYNC | \
     RLL_OBS_RAW_HASHED | RLL_OBS_UNCERTAINTY_VALID)

static rll_u32 rll_is_valid_region(rll_u32 region) {
    return (region >= RLL_REGION_COSMOLOGY_EVIDENCE) &&
           (region <= RLL_REGION_STRONG_GRAVITY_REFERENCE);
}

static rll_u32 rll_is_valid_domain(rll_u32 domain) {
    return (domain >= RLL_DOMAIN_COSMOLOGY) &&
           (domain <= RLL_DOMAIN_GOVERNANCE);
}

static rll_u32 rll_is_cosmology_quantity(rll_u32 quantity) {
    return (quantity >= RLL_Q_REDSHIFT) && (quantity <= RLL_Q_FSIGMA8);
}

static rll_u32 rll_is_geophysics_quantity(rll_u32 quantity) {
    return (quantity >= RLL_Q_GEO_STRESS) &&
           (quantity <= RLL_Q_GEO_MAGNETIC_FIELD);
}

static rll_u32 rll_is_geometry_quantity(rll_u32 quantity) {
    return (quantity == RLL_Q_PHASE) ||
           (quantity == RLL_Q_TORUS_CLOSURE) ||
           (quantity == RLL_Q_DIMENSIONLESS_OPERATOR);
}

static rll_u32 rll_has_flags(rll_u32 flags, rll_u32 required) {
    return (flags & required) == required;
}

static rll_u32 rll_source_is_bound(const rll_canonical_observation *o) {
    return (o->sample_count != 0ull) &&
           (o->source_fnv1a64 != 0ull) &&
           (o->source_crc32 != 0u);
}

static rll_u32 rll_domain_quantity_match(const rll_canonical_observation *o) {
    if (o->domain == RLL_DOMAIN_COSMOLOGY) {
        return rll_is_cosmology_quantity(o->quantity);
    }
    if (o->domain == RLL_DOMAIN_LOCAL_GEOPHYSICS) {
        return rll_is_geophysics_quantity(o->quantity);
    }
    if ((o->domain == RLL_DOMAIN_TOROIDAL_GEOMETRY) ||
        (o->domain == RLL_DOMAIN_MATHEMATICS) ||
        (o->domain == RLL_DOMAIN_STRONG_GRAVITY)) {
        return rll_is_geometry_quantity(o->quantity);
    }
    return o->domain == RLL_DOMAIN_GOVERNANCE;
}

rll_u32 rll_canonical_expected_unit(rll_u32 quantity) {
    if ((quantity == RLL_Q_REDSHIFT) ||
        (quantity == RLL_Q_BAO_DV_RS) ||
        (quantity == RLL_Q_FSIGMA8) ||
        (quantity == RLL_Q_DIMENSIONLESS_OPERATOR)) {
        return RLL_UNIT_DIMENSIONLESS;
    }
    if (quantity == RLL_Q_DISTANCE_MODULUS) {
        return RLL_UNIT_MAGNITUDE;
    }
    if (quantity == RLL_Q_HUBBLE) {
        return RLL_UNIT_KM_S_MPC;
    }
    if ((quantity == RLL_Q_GEO_STRESS) ||
        (quantity == RLL_Q_GEO_ACOUSTIC)) {
        return RLL_UNIT_PASCAL;
    }
    if (quantity == RLL_Q_GEO_ELECTRIC_FIELD) {
        return RLL_UNIT_VOLT_PER_METRE;
    }
    if (quantity == RLL_Q_GEO_MAGNETIC_FIELD) {
        return RLL_UNIT_TESLA;
    }
    if (quantity == RLL_Q_PHASE) {
        return RLL_UNIT_RADIAN;
    }
    if (quantity == RLL_Q_TORUS_CLOSURE) {
        return RLL_UNIT_METRE;
    }
    return RLL_UNIT_INVALID;
}

static rll_u32 rll_observation_shape_is_valid(const rll_canonical_observation *o) {
    rll_u32 expected_unit;
    if (o == (const rll_canonical_observation *)0) {
        return 0u;
    }
    if (!rll_is_valid_domain(o->domain) ||
        (o->state > RLL_STATE_BLOCKED) ||
        !rll_domain_quantity_match(o)) {
        return 0u;
    }
    expected_unit = rll_canonical_expected_unit(o->quantity);
    if ((expected_unit == RLL_UNIT_INVALID) || (o->unit != expected_unit)) {
        return 0u;
    }
    return rll_source_is_bound(o);
}

rll_u32 rll_canonical_classify(
    rll_u32 target_region,
    const rll_canonical_observation *o
) {
    if (!rll_is_valid_region(target_region) || !rll_observation_shape_is_valid(o)) {
        return RLL_COUPLING_BLOCKED;
    }
    if ((o->state == RLL_STATE_BLOCKED) ||
        (o->state == RLL_STATE_CONTRADICTION)) {
        return RLL_COUPLING_BLOCKED;
    }
    if (o->state == RLL_STATE_TOKEN_VAZIO) {
        return RLL_COUPLING_TOKEN_VAZIO;
    }
    if (o->state == RLL_STATE_SYNTHETIC) {
        return RLL_COUPLING_SYNTHETIC_ONLY;
    }

    if (target_region == RLL_REGION_COSMOLOGY_EVIDENCE) {
        if (o->domain == RLL_DOMAIN_COSMOLOGY) {
            if ((o->state == RLL_STATE_OBSERVED) &&
                (o->sigma_q16 > 0ll) &&
                rll_has_flags(o->flags, RLL_COSMO_REQUIRED_FLAGS)) {
                return RLL_COUPLING_EVIDENCE;
            }
            return RLL_COUPLING_BLOCKED;
        }
        if ((o->domain == RLL_DOMAIN_MATHEMATICS) ||
            (o->domain == RLL_DOMAIN_TOROIDAL_GEOMETRY)) {
            return (o->state == RLL_STATE_EXACT)
                ? RLL_COUPLING_EXACT_OPERATOR
                : RLL_COUPLING_CONTEXT_ONLY;
        }
        return RLL_COUPLING_CONTEXT_ONLY;
    }

    if (target_region == RLL_REGION_LOCAL_CONTEXT) {
        if (o->domain != RLL_DOMAIN_LOCAL_GEOPHYSICS) {
            return RLL_COUPLING_BLOCKED;
        }
        if ((o->state == RLL_STATE_OBSERVED) &&
            (o->sigma_q16 > 0ll) &&
            rll_has_flags(o->flags, RLL_LOCAL_REQUIRED_FLAGS)) {
            return RLL_COUPLING_CONTEXT_ONLY;
        }
        return RLL_COUPLING_BLOCKED;
    }

    if (target_region == RLL_REGION_GEOMETRY_OPERATOR) {
        if ((o->domain != RLL_DOMAIN_MATHEMATICS) &&
            (o->domain != RLL_DOMAIN_TOROIDAL_GEOMETRY)) {
            return RLL_COUPLING_BLOCKED;
        }
        return (o->state == RLL_STATE_EXACT)
            ? RLL_COUPLING_EXACT_OPERATOR
            : RLL_COUPLING_CONTEXT_ONLY;
    }

    if (target_region == RLL_REGION_STRONG_GRAVITY_REFERENCE) {
        if (o->domain != RLL_DOMAIN_STRONG_GRAVITY) {
            return RLL_COUPLING_BLOCKED;
        }
        return RLL_COUPLING_CONTEXT_ONLY;
    }

    return RLL_COUPLING_BLOCKED;
}

static rll_i64 rll_sat_sub_i64(rll_i64 a, rll_i64 b) {
    if ((b > 0ll) && (a < (RLL_I64_MIN + b))) {
        return RLL_I64_MIN;
    }
    if ((b < 0ll) && (a > (RLL_I64_MAX + b))) {
        return RLL_I64_MAX;
    }
    return a - b;
}

static rll_i64 rll_sat_add_nonnegative_i64(rll_i64 a, rll_i64 b) {
    if ((b < 0ll) || (a < 0ll)) {
        return RLL_I64_MAX;
    }
    if (a > (RLL_I64_MAX - b)) {
        return RLL_I64_MAX;
    }
    return a + b;
}

static rll_i64 rll_residual_q16(const rll_canonical_observation *o) {
    rll_i64 delta = rll_sat_sub_i64(o->value_q16, o->model_q16);
    if (o->sigma_q16 <= 0ll) {
        return RLL_I64_MAX;
    }
    if (delta > (RLL_I64_MAX >> 16)) {
        return RLL_I64_MAX;
    }
    if (delta < (RLL_I64_MIN >> 16)) {
        return RLL_I64_MIN;
    }
    return (delta << 16) / o->sigma_q16;
}

static rll_i64 rll_square_q16_sat(rll_i64 x_q16) {
    rll_i64 abs_x;
    if (x_q16 == RLL_I64_MIN) {
        return RLL_I64_MAX;
    }
    abs_x = (x_q16 < 0ll) ? -x_q16 : x_q16;
    if (abs_x > RLL_SQRT_I64_MAX) {
        return RLL_I64_MAX;
    }
    return (abs_x * abs_x) >> 16;
}

static void rll_digest_byte(rll_canonical_accumulator *a, rll_u8 byte) {
    rll_u32 x;
    rll_u32 j;
    a->receipt_fnv1a64 ^= (rll_u64)byte;
    a->receipt_fnv1a64 *= RLL_FNV_PRIME;

    x = (a->receipt_crc32_state ^ (rll_u32)byte) & 0xFFu;
    j = 0u;
    while (j < 8u) {
        rll_u32 mask = (rll_u32)(-(rll_i64)(x & 1u));
        x = (x >> 1u) ^ (RLL_CRC32_POLY_REV & mask);
        j++;
    }
    a->receipt_crc32_state = (a->receipt_crc32_state >> 8u) ^ x;
}

static void rll_digest_u32(rll_canonical_accumulator *a, rll_u32 value) {
    rll_u32 i = 0u;
    while (i < 4u) {
        rll_digest_byte(a, (rll_u8)((value >> (i * 8u)) & 0xFFu));
        i++;
    }
}

static void rll_digest_u64(rll_canonical_accumulator *a, rll_u64 value) {
    rll_u32 i = 0u;
    while (i < 8u) {
        rll_digest_byte(a, (rll_u8)((value >> (i * 8u)) & 0xFFu));
        i++;
    }
}

static void rll_digest_observation(
    rll_canonical_accumulator *a,
    const rll_canonical_observation *o,
    rll_u32 decision
) {
    rll_digest_u32(a, o->domain);
    rll_digest_u32(a, o->quantity);
    rll_digest_u32(a, o->unit);
    rll_digest_u32(a, o->state);
    rll_digest_u64(a, (rll_u64)o->value_q16);
    rll_digest_u64(a, (rll_u64)o->model_q16);
    rll_digest_u64(a, (rll_u64)o->sigma_q16);
    rll_digest_u64(a, o->sample_count);
    rll_digest_u32(a, o->flags);
    rll_digest_u32(a, o->sequence_id);
    rll_digest_u64(a, o->source_fnv1a64);
    rll_digest_u32(a, o->source_crc32);
    rll_digest_u32(a, decision);
}

void rll_canonical_init(rll_canonical_accumulator *a, rll_u32 target_region) {
    if (a == (rll_canonical_accumulator *)0) {
        return;
    }
    a->target_region = target_region;
    a->total = 0u;
    a->evidence = 0u;
    a->context_only = 0u;
    a->exact_operator = 0u;
    a->synthetic_only = 0u;
    a->token_vazio = 0u;
    a->blocked = 0u;
    a->contradictions = 0u;
    a->degrees_of_freedom = 0u;
    a->chi2_q16 = 0ll;
    a->receipt_fnv1a64 = RLL_FNV_OFFSET;
    a->receipt_crc32_state = RLL_CRC32_INIT;
}

rll_u32 rll_canonical_push(
    rll_canonical_accumulator *a,
    const rll_canonical_observation *o
) {
    rll_u32 decision;
    if ((a == (rll_canonical_accumulator *)0) ||
        (o == (const rll_canonical_observation *)0)) {
        return RLL_COUPLING_BLOCKED;
    }

    decision = rll_canonical_classify(a->target_region, o);
    a->total++;
    if (o->state == RLL_STATE_CONTRADICTION) {
        a->contradictions++;
    }

    if (decision == RLL_COUPLING_EVIDENCE) {
        rll_i64 residual = rll_residual_q16(o);
        rll_i64 chi2 = rll_square_q16_sat(residual);
        a->evidence++;
        a->degrees_of_freedom++;
        a->chi2_q16 = rll_sat_add_nonnegative_i64(a->chi2_q16, chi2);
    } else if (decision == RLL_COUPLING_CONTEXT_ONLY) {
        a->context_only++;
    } else if (decision == RLL_COUPLING_EXACT_OPERATOR) {
        a->exact_operator++;
    } else if (decision == RLL_COUPLING_SYNTHETIC_ONLY) {
        a->synthetic_only++;
    } else if (decision == RLL_COUPLING_TOKEN_VAZIO) {
        a->token_vazio++;
    } else {
        a->blocked++;
    }

    rll_digest_observation(a, o, decision);
    return decision;
}

rll_canonical_receipt rll_canonical_snapshot(const rll_canonical_accumulator *a) {
    rll_canonical_receipt r;
    if (a == (const rll_canonical_accumulator *)0) {
        r.target_region = RLL_REGION_INVALID;
        r.total = 0u;
        r.evidence = 0u;
        r.context_only = 0u;
        r.exact_operator = 0u;
        r.synthetic_only = 0u;
        r.token_vazio = 0u;
        r.blocked = 1u;
        r.contradictions = 0u;
        r.degrees_of_freedom = 0u;
        r.chi2_q16 = 0ll;
        r.receipt_fnv1a64 = RLL_FNV_OFFSET;
        r.receipt_crc32 = 0u;
        r.claim_allowed = 0u;
        return r;
    }
    r.target_region = a->target_region;
    r.total = a->total;
    r.evidence = a->evidence;
    r.context_only = a->context_only;
    r.exact_operator = a->exact_operator;
    r.synthetic_only = a->synthetic_only;
    r.token_vazio = a->token_vazio;
    r.blocked = a->blocked;
    r.contradictions = a->contradictions;
    r.degrees_of_freedom = a->degrees_of_freedom;
    r.chi2_q16 = a->chi2_q16;
    r.receipt_fnv1a64 = a->receipt_fnv1a64;
    r.receipt_crc32 = a->receipt_crc32_state ^ RLL_CRC32_FINAL_XOR;
    r.claim_allowed = 0u;
    return r;
}
