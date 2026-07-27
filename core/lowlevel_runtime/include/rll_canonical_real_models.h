#ifndef RLL_CANONICAL_REAL_MODELS_H
#define RLL_CANONICAL_REAL_MODELS_H

#include "rll_canonical_real_inputs.h"
#include "rll_hz_freestanding.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum rll_real_model_profile {
    RLL_REAL_PROFILE_LCDM_NOMINAL = 1,
    RLL_REAL_PROFILE_RLL_NOMINAL = 2
} rll_real_model_profile;

typedef struct rll_real_model_context {
    rll_u32 profile;
    rll_u32 reserved;
    rll_hz_params_q16 hz_params;
} rll_real_model_context;

rll_real_model_context rll_real_model_lcdm_nominal(void);
rll_real_model_context rll_real_model_rll_nominal(void);

rll_u32 rll_real_canonical_model_callback(
    void *context,
    const rll_real_model_request *request,
    rll_i64 *model_q16
);

#ifdef __cplusplus
}
#endif

#endif
