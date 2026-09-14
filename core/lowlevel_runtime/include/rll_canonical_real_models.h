#ifndef RLL_CANONICAL_REAL_MODELS_H
#define RLL_CANONICAL_REAL_MODELS_H

#include "rll_canonical_real_inputs.h"
#include "rll_hz_freestanding.h"
#include "rll_canonical_real.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum rll_real_model_profile {
    /* Backward-compatible H(z)-only profiles from V1. */
    RLL_REAL_PROFILE_LCDM_NOMINAL = 1,
    RLL_REAL_PROFILE_RLL_NOMINAL = 2,

    /* Full 65-observation profiles backed by the existing canonical evaluator. */
    RLL_REAL_PROFILE_LCDM_JOINT_FASE18E = 3,
    RLL_REAL_PROFILE_RLL_JOINT_FASE18E = 4
} rll_real_model_profile;

typedef struct rll_real_model_context {
    /* Preserve the V1 prefix so existing source initializers remain compatible. */
    rll_u32 profile;
    rll_u32 reserved;
    rll_hz_params_q16 hz_params;

    /* V2 joint-profile state. */
    rll_cosmo_params cosmo_params;
    rll_u32 model_kind;
    rll_u32 enabled_source_mask;
} rll_real_model_context;

/* V1 compatibility constructors: bind only the 33 H(z) observations. */
rll_real_model_context rll_real_model_lcdm_nominal(void);
rll_real_model_context rll_real_model_rll_nominal(void);

/* V2 constructors: bind H(z), DESI DR2 BAO, fσ8 and CMB distance priors. */
rll_real_model_context rll_real_model_lcdm_joint_fase18e(void);
rll_real_model_context rll_real_model_rll_joint_fase18e(void);

rll_u32 rll_real_canonical_model_callback(
    void *context,
    const rll_real_model_request *request,
    rll_i64 *model_q16
);

#ifdef __cplusplus
}
#endif

#endif
