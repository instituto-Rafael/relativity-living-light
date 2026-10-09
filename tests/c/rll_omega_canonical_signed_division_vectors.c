/* Adversarial hosted test vectors for authorial freestanding Q16 division.
 * No libc/includes beyond the local freestanding RLL header.
 * main() is invoked by the HOST runtime; it is not ARM physical evidence.
 */
#include "rll_canonical_coupling.h"

#define Q16(v) ((rll_i64)(v) * RLL_Q16_ONE)
#define FLAGS (RLL_OBS_CALIBRATED | RLL_OBS_RAW_HASHED | RLL_OBS_UNCERTAINTY_VALID | RLL_OBS_MODEL_REGISTERED)

static rll_canonical_observation vector(rll_i64 value, rll_i64 model, rll_i64 sigma) {
    rll_canonical_observation o;
    o.domain = RLL_DOMAIN_COSMOLOGY;
    o.quantity = RLL_Q_HUBBLE;
    o.unit = RLL_UNIT_KM_S_MPC;
    o.state = RLL_STATE_OBSERVED;
    o.value_q16 = value;
    o.model_q16 = model;
    o.sigma_q16 = sigma;
    o.sample_count = 1ull;
    o.flags = FLAGS;
    o.sequence_id = 1u;
    o.source_fnv1a64 = 0x12345678ull;
    o.source_crc32 = 0x10203040u;
    return o;
}

int main(void) {
    rll_canonical_accumulator a;
    rll_canonical_observation o;
    rll_canonical_receipt r;
    rll_canonical_init(&a, RLL_REGION_COSMOLOGY_EVIDENCE);

    /* -1/2 and +1/2 must both produce one quarter Q16 chi-square. */
    o = vector(Q16(2), Q16(3), Q16(2));
    if (rll_canonical_push(&a, &o) != RLL_COUPLING_EVIDENCE) return 1;
    r = rll_canonical_snapshot(&a);
    if (r.chi2_q16 != Q16(1) / 4) return 2;

    o = vector(Q16(3), Q16(2), Q16(2));
    o.sequence_id = 2u;
    if (rll_canonical_push(&a, &o) != RLL_COUPLING_EVIDENCE) return 3;
    r = rll_canonical_snapshot(&a);
    if (r.chi2_q16 != Q16(1) / 2) return 4;

    /* Non-integral division truncates toward zero, not minus infinity. */
    o = vector(Q16(2), Q16(3), Q16(3));
    o.sequence_id = 3u;
    if (rll_canonical_push(&a, &o) != RLL_COUPLING_EVIDENCE) return 5;
    r = rll_canonical_snapshot(&a);
    if (r.chi2_q16 != Q16(1) / 2 + ((rll_i64)21845 * 21845 >> 16)) return 6;

    /* Numeric zero residual is valid evidence; TOKEN_VAZIO is not. */
    o = vector(Q16(2), Q16(2), Q16(1));
    o.sequence_id = 4u;
    if (rll_canonical_push(&a, &o) != RLL_COUPLING_EVIDENCE) return 7;
    r = rll_canonical_snapshot(&a);
    if (r.evidence != 4u) return 8;
    o.state = RLL_STATE_TOKEN_VAZIO;
    o.sequence_id = 5u;
    if (rll_canonical_push(&a, &o) != RLL_COUPLING_TOKEN_VAZIO) return 9;
    r = rll_canonical_snapshot(&a);
    if (r.evidence != 4u || r.token_vazio != 1u) return 10;

    /* Invalid uncertainty must fail closed without divide by zero. */
    o = vector(Q16(2), Q16(3), 0ll);
    o.sequence_id = 6u;
    if (rll_canonical_push(&a, &o) != RLL_COUPLING_BLOCKED) return 11;

    /* Overflow/saturation path: no undefined negative left shift. */
    o = vector(-0x7FFFFFFFFFFFFFFFll - 1ll, 0x7FFFFFFFFFFFFFFFll, Q16(1));
    o.sequence_id = 7u;
    if (rll_canonical_push(&a, &o) != RLL_COUPLING_EVIDENCE) return 12;
    r = rll_canonical_snapshot(&a);
    if (r.chi2_q16 != 0x7FFFFFFFFFFFFFFFll) return 13;
    if (r.claim_allowed != 0u) return 14;

    return 0;
}
