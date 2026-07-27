#ifndef RLL_CANONICAL_REAL_INPUTS_H
#define RLL_CANONICAL_REAL_INPUTS_H

#include "rll_canonical_coupling.h"

#ifdef __cplusplus
extern "C" {
#endif

#define RLL_REAL_SCHEMA_V1 0x524C5231u /* RLR1 */
#define RLL_REAL_SOURCE_HZ   (1u << 0)
#define RLL_REAL_SOURCE_BAO  (1u << 1)
#define RLL_REAL_SOURCE_FS8  (1u << 2)
#define RLL_REAL_SOURCE_CMB  (1u << 3)
#define RLL_REAL_SOURCE_ALL  0x0Fu

/* Extension IDs preserve the numeric ABI introduced by canonical_coupling V1. */
#define RLL_Q_BAO_DM_RS            13u
#define RLL_Q_BAO_DH_RS            14u
#define RLL_Q_CMB_SHIFT_R          15u
#define RLL_Q_CMB_ACOUSTIC_SCALE   16u
#define RLL_Q_CMB_OMEGA_B_H2       17u

#define RLL_REAL_MODEL_OK           1u
#define RLL_REAL_MODEL_TOKEN_VAZIO  0u
#define RLL_REAL_MODEL_BLOCKED      2u

#define RLL_REAL_OK                  0
#define RLL_REAL_TOKEN_VAZIO         1
#define RLL_REAL_E_NULL             -1
#define RLL_REAL_E_SHA256           -2
#define RLL_REAL_E_SCHEMA           -3
#define RLL_REAL_E_FORMAT           -4
#define RLL_REAL_E_RANGE            -5
#define RLL_REAL_E_UNCERTAINTY      -6
#define RLL_REAL_E_COVARIANCE       -7
#define RLL_REAL_E_MODEL            -8

typedef struct rll_real_model_request {
    rll_u32 dataset_mask;
    rll_u32 quantity;
    rll_u32 sequence_id;
    rll_u32 reserved;
    rll_i64 axis_q16;
    rll_i64 observed_q16;
    rll_i64 sigma_q16;
} rll_real_model_request;

typedef rll_u32 (*rll_real_model_callback)(
    void *context,
    const rll_real_model_request *request,
    rll_i64 *model_q16
);

typedef struct rll_real_input_bundle {
    const rll_u8 *hz_csv;
    rll_u64 hz_len;
    const rll_u8 *bao_csv;
    rll_u64 bao_len;
    const rll_u8 *fsigma8_csv;
    rll_u64 fsigma8_len;
    const rll_u8 *cmb_json;
    rll_u64 cmb_len;
} rll_real_input_bundle;

typedef struct rll_real_ingest_receipt {
    rll_u32 schema;
    int status;
    rll_u32 source_verified_mask;
    rll_u32 required_source_mask;
    rll_u32 parsed_rows;
    rll_u32 model_bound_rows;
    rll_u32 model_token_vazio_rows;
    rll_u32 parse_errors;
    rll_u32 hz_rows;
    rll_u32 bao_rows;
    rll_u32 fsigma8_rows;
    rll_u32 cmb_rows;
    rll_u32 cmb_covariance_used;
    rll_u32 claim_allowed;
    rll_canonical_receipt canonical;
} rll_real_ingest_receipt;

rll_u32 rll_canonical_expected_unit_extended(rll_u32 quantity);
rll_u32 rll_canonical_push_extended(
    rll_canonical_accumulator *accumulator,
    const rll_canonical_observation *observation
);

int rll_real_ingest_all(
    const rll_real_input_bundle *bundle,
    rll_real_model_callback model_callback,
    void *model_context,
    rll_real_ingest_receipt *receipt
);

#ifdef __cplusplus
}
#endif

#endif
