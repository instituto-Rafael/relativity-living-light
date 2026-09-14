#ifndef RLL_CANONICAL_COUPLING_H
#define RLL_CANONICAL_COUPLING_H

#include "pantheon_freestanding.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Canonical RLL coupling contract.
 *
 * This module is deliberately freestanding: no libc, no heap, no file I/O and
 * no implicit unit conversion. It couples already-decoded observations to a
 * target RLL region while keeping local context, exact operators, synthetic
 * fixtures and observational evidence structurally distinct.
 */

#define RLL_Q16_ONE 65536ll

#define RLL_OBS_CALIBRATED          (1u << 0)
#define RLL_OBS_CLOCK_SYNC          (1u << 1)
#define RLL_OBS_RAW_HASHED          (1u << 2)
#define RLL_OBS_UNCERTAINTY_VALID   (1u << 3)
#define RLL_OBS_MODEL_REGISTERED    (1u << 4)
#define RLL_OBS_PREREGISTERED       (1u << 5)
#define RLL_OBS_STANDARD_REJECTED   (1u << 6)

typedef enum rll_canonical_domain {
    RLL_DOMAIN_INVALID = 0,
    RLL_DOMAIN_COSMOLOGY = 1,
    RLL_DOMAIN_LOCAL_GEOPHYSICS = 2,
    RLL_DOMAIN_STRONG_GRAVITY = 3,
    RLL_DOMAIN_TOROIDAL_GEOMETRY = 4,
    RLL_DOMAIN_MATHEMATICS = 5,
    RLL_DOMAIN_GOVERNANCE = 6
} rll_canonical_domain;

typedef enum rll_canonical_region {
    RLL_REGION_INVALID = 0,
    RLL_REGION_COSMOLOGY_EVIDENCE = 1,
    RLL_REGION_LOCAL_CONTEXT = 2,
    RLL_REGION_GEOMETRY_OPERATOR = 3,
    RLL_REGION_STRONG_GRAVITY_REFERENCE = 4
} rll_canonical_region;

typedef enum rll_canonical_state {
    RLL_STATE_TOKEN_VAZIO = 0,
    RLL_STATE_EXACT = 1,
    RLL_STATE_OBSERVED = 2,
    RLL_STATE_SYNTHETIC = 3,
    RLL_STATE_CONTRADICTION = 4,
    RLL_STATE_BLOCKED = 5
} rll_canonical_state;

typedef enum rll_canonical_quantity {
    RLL_Q_INVALID = 0,
    RLL_Q_REDSHIFT = 1,
    RLL_Q_DISTANCE_MODULUS = 2,
    RLL_Q_HUBBLE = 3,
    RLL_Q_BAO_DV_RS = 4,
    RLL_Q_FSIGMA8 = 5,
    RLL_Q_GEO_STRESS = 6,
    RLL_Q_GEO_ACOUSTIC = 7,
    RLL_Q_GEO_ELECTRIC_FIELD = 8,
    RLL_Q_GEO_MAGNETIC_FIELD = 9,
    RLL_Q_PHASE = 10,
    RLL_Q_TORUS_CLOSURE = 11,
    RLL_Q_DIMENSIONLESS_OPERATOR = 12
} rll_canonical_quantity;

typedef enum rll_canonical_unit {
    RLL_UNIT_INVALID = 0,
    RLL_UNIT_DIMENSIONLESS = 1,
    RLL_UNIT_MAGNITUDE = 2,
    RLL_UNIT_KM_S_MPC = 3,
    RLL_UNIT_PASCAL = 4,
    RLL_UNIT_VOLT_PER_METRE = 5,
    RLL_UNIT_TESLA = 6,
    RLL_UNIT_RADIAN = 7,
    RLL_UNIT_METRE = 8
} rll_canonical_unit;

typedef enum rll_coupling_decision {
    RLL_COUPLING_EVIDENCE = 1,
    RLL_COUPLING_CONTEXT_ONLY = 2,
    RLL_COUPLING_EXACT_OPERATOR = 3,
    RLL_COUPLING_SYNTHETIC_ONLY = 4,
    RLL_COUPLING_TOKEN_VAZIO = 5,
    RLL_COUPLING_BLOCKED = 6
} rll_coupling_decision;

typedef struct rll_canonical_observation {
    rll_u32 domain;
    rll_u32 quantity;
    rll_u32 unit;
    rll_u32 state;
    rll_i64 value_q16;
    rll_i64 model_q16;
    rll_i64 sigma_q16;
    rll_u64 sample_count;
    rll_u32 flags;
    rll_u32 sequence_id;
    rll_u64 source_fnv1a64;
    rll_u32 source_crc32;
} rll_canonical_observation;

typedef struct rll_canonical_accumulator {
    rll_u32 target_region;
    rll_u32 total;
    rll_u32 evidence;
    rll_u32 context_only;
    rll_u32 exact_operator;
    rll_u32 synthetic_only;
    rll_u32 token_vazio;
    rll_u32 blocked;
    rll_u32 contradictions;
    rll_u32 degrees_of_freedom;
    rll_i64 chi2_q16;
    rll_u64 receipt_fnv1a64;
    rll_u32 receipt_crc32_state;
} rll_canonical_accumulator;

typedef struct rll_canonical_receipt {
    rll_u32 target_region;
    rll_u32 total;
    rll_u32 evidence;
    rll_u32 context_only;
    rll_u32 exact_operator;
    rll_u32 synthetic_only;
    rll_u32 token_vazio;
    rll_u32 blocked;
    rll_u32 contradictions;
    rll_u32 degrees_of_freedom;
    rll_i64 chi2_q16;
    rll_u64 receipt_fnv1a64;
    rll_u32 receipt_crc32;
    rll_u32 claim_allowed;
} rll_canonical_receipt;

rll_u32 rll_canonical_expected_unit(rll_u32 quantity);
rll_u32 rll_canonical_classify(
    rll_u32 target_region,
    const rll_canonical_observation *observation
);
void rll_canonical_init(rll_canonical_accumulator *accumulator, rll_u32 target_region);
rll_u32 rll_canonical_push(
    rll_canonical_accumulator *accumulator,
    const rll_canonical_observation *observation
);
rll_canonical_receipt rll_canonical_snapshot(
    const rll_canonical_accumulator *accumulator
);

#ifdef __cplusplus
}
#endif

#endif
