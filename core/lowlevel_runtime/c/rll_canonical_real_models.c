#include "rll_canonical_real_models.h"

rll_real_model_context rll_real_model_lcdm_nominal(void) {
    rll_real_model_context context;
    context.profile = RLL_REAL_PROFILE_LCDM_NOMINAL;
    context.reserved = 0u;
    context.hz_params = rll_hz_nominal_planck_params_q16();
    return context;
}

rll_real_model_context rll_real_model_rll_nominal(void) {
    rll_real_model_context context;
    context.profile = RLL_REAL_PROFILE_RLL_NOMINAL;
    context.reserved = 0u;
    context.hz_params = rll_hz_nominal_planck_params_q16();
    return context;
}

rll_u32 rll_real_canonical_model_callback(
    void *opaque,
    const rll_real_model_request *request,
    rll_i64 *model_q16
) {
    rll_real_model_context *context = (rll_real_model_context *)opaque;
    if (context == (rll_real_model_context *)0 ||
        request == (const rll_real_model_request *)0 ||
        model_q16 == (rll_i64 *)0) {
        return RLL_REAL_MODEL_BLOCKED;
    }

    if (request->dataset_mask != RLL_REAL_SOURCE_HZ ||
        request->quantity != RLL_Q_HUBBLE) {
        return RLL_REAL_MODEL_TOKEN_VAZIO;
    }

    if (context->profile == RLL_REAL_PROFILE_LCDM_NOMINAL) {
        *model_q16 = rll_hz_lcdm_q16(request->axis_q16, &context->hz_params);
        return *model_q16 > 0ll ? RLL_REAL_MODEL_OK : RLL_REAL_MODEL_BLOCKED;
    }
    if (context->profile == RLL_REAL_PROFILE_RLL_NOMINAL) {
        *model_q16 = rll_hz_rll_q16(request->axis_q16, &context->hz_params);
        return *model_q16 > 0ll ? RLL_REAL_MODEL_OK : RLL_REAL_MODEL_BLOCKED;
    }
    return RLL_REAL_MODEL_BLOCKED;
}
