#include "rll_canonical_coupling.h"

#define Q16(x) ((rll_i64)(x) * RLL_Q16_ONE)
#define COSMO_FLAGS (RLL_OBS_CALIBRATED | RLL_OBS_RAW_HASHED | RLL_OBS_UNCERTAINTY_VALID | RLL_OBS_MODEL_REGISTERED)
#define GEO_FLAGS (RLL_OBS_CALIBRATED | RLL_OBS_CLOCK_SYNC | RLL_OBS_RAW_HASHED | RLL_OBS_UNCERTAINTY_VALID)

static rll_canonical_observation base_observation(void) {
    rll_canonical_observation o;
    o.domain = RLL_DOMAIN_COSMOLOGY;
    o.quantity = RLL_Q_HUBBLE;
    o.unit = RLL_UNIT_KM_S_MPC;
    o.state = RLL_STATE_OBSERVED;
    o.value_q16 = Q16(3);
    o.model_q16 = Q16(2);
    o.sigma_q16 = Q16(1);
    o.sample_count = 64ull;
    o.flags = COSMO_FLAGS;
    o.sequence_id = 1u;
    o.source_fnv1a64 = 0x1020304050607080ull;
    o.source_crc32 = 0xA1B2C3D4u;
    return o;
}

int main(void) {
    rll_canonical_accumulator cosmology;
    rll_canonical_accumulator local;
    rll_canonical_accumulator geometry;
    rll_canonical_observation o;
    rll_canonical_receipt r;

    rll_canonical_init(&cosmology, RLL_REGION_COSMOLOGY_EVIDENCE);

    o = base_observation();
    if (rll_canonical_push(&cosmology, &o) != RLL_COUPLING_EVIDENCE) return 1;

    o = base_observation();
    o.quantity = RLL_Q_FSIGMA8;
    o.unit = RLL_UNIT_DIMENSIONLESS;
    o.sequence_id = 2u;
    if (rll_canonical_push(&cosmology, &o) != RLL_COUPLING_EVIDENCE) return 2;

    o = base_observation();
    o.domain = RLL_DOMAIN_LOCAL_GEOPHYSICS;
    o.quantity = RLL_Q_GEO_MAGNETIC_FIELD;
    o.unit = RLL_UNIT_TESLA;
    o.flags = GEO_FLAGS;
    o.sequence_id = 3u;
    if (rll_canonical_push(&cosmology, &o) != RLL_COUPLING_CONTEXT_ONLY) return 3;

    o = base_observation();
    o.state = RLL_STATE_SYNTHETIC;
    o.sequence_id = 4u;
    if (rll_canonical_push(&cosmology, &o) != RLL_COUPLING_SYNTHETIC_ONLY) return 4;

    o = base_observation();
    o.state = RLL_STATE_TOKEN_VAZIO;
    o.sequence_id = 5u;
    if (rll_canonical_push(&cosmology, &o) != RLL_COUPLING_TOKEN_VAZIO) return 5;

    o = base_observation();
    o.unit = RLL_UNIT_TESLA;
    o.sequence_id = 6u;
    if (rll_canonical_push(&cosmology, &o) != RLL_COUPLING_BLOCKED) return 6;

    r = rll_canonical_snapshot(&cosmology);
    if (r.total != 6u) return 7;
    if (r.evidence != 2u || r.degrees_of_freedom != 2u) return 8;
    if (r.context_only != 1u || r.synthetic_only != 1u) return 9;
    if (r.token_vazio != 1u || r.blocked != 1u) return 10;
    if (r.exact_operator != 0u || r.contradictions != 0u) return 11;
    if (r.chi2_q16 != Q16(2)) return 12;
    if (r.receipt_fnv1a64 == 0ull || r.receipt_crc32 == 0u) return 13;
    if (r.claim_allowed != 0u) return 14;

    rll_canonical_init(&local, RLL_REGION_LOCAL_CONTEXT);
    o = base_observation();
    o.domain = RLL_DOMAIN_LOCAL_GEOPHYSICS;
    o.quantity = RLL_Q_GEO_STRESS;
    o.unit = RLL_UNIT_PASCAL;
    o.flags = GEO_FLAGS;
    if (rll_canonical_push(&local, &o) != RLL_COUPLING_CONTEXT_ONLY) return 15;
    r = rll_canonical_snapshot(&local);
    if (r.total != 1u || r.context_only != 1u || r.evidence != 0u) return 16;

    rll_canonical_init(&geometry, RLL_REGION_GEOMETRY_OPERATOR);
    o = base_observation();
    o.domain = RLL_DOMAIN_MATHEMATICS;
    o.quantity = RLL_Q_DIMENSIONLESS_OPERATOR;
    o.unit = RLL_UNIT_DIMENSIONLESS;
    o.state = RLL_STATE_EXACT;
    o.sigma_q16 = 0ll;
    o.flags = RLL_OBS_RAW_HASHED;
    if (rll_canonical_push(&geometry, &o) != RLL_COUPLING_EXACT_OPERATOR) return 17;
    r = rll_canonical_snapshot(&geometry);
    if (r.total != 1u || r.exact_operator != 1u || r.claim_allowed != 0u) return 18;

    return 0;
}
