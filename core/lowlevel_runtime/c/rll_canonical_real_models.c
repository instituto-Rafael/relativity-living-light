#include "rll_canonical_real_models.h"

#define RLL_REAL_Q16_SCALE 65536.0
#define RLL_REAL_I64_BOUND 9.2233720368547750e18

static rll_real_model_context rll_real_context_base(rll_u32 profile) {
    rll_real_model_context context;
    context.profile = profile;
    context.reserved = 0u;
    context.hz_params = rll_hz_nominal_planck_params_q16();
    context.cosmo_params = rll_params_fase18e_lcdm();
    context.model_kind = RLL_MODEL_LCDM;
    context.enabled_source_mask = RLL_REAL_SOURCE_HZ;
    return context;
}

rll_real_model_context rll_real_model_lcdm_nominal(void) {
    return rll_real_context_base(RLL_REAL_PROFILE_LCDM_NOMINAL);
}

rll_real_model_context rll_real_model_rll_nominal(void) {
    rll_real_model_context context =
        rll_real_context_base(RLL_REAL_PROFILE_RLL_NOMINAL);
    context.cosmo_params = rll_params_fase18e_map();
    context.model_kind = RLL_MODEL_LOGISTIC;
    return context;
}

rll_real_model_context rll_real_model_lcdm_joint_fase18e(void) {
    rll_real_model_context context =
        rll_real_context_base(RLL_REAL_PROFILE_LCDM_JOINT_FASE18E);
    context.cosmo_params = rll_params_fase18e_lcdm();
    context.model_kind = RLL_MODEL_LCDM;
    context.enabled_source_mask = RLL_REAL_SOURCE_ALL;
    return context;
}

rll_real_model_context rll_real_model_rll_joint_fase18e(void) {
    rll_real_model_context context =
        rll_real_context_base(RLL_REAL_PROFILE_RLL_JOINT_FASE18E);
    context.cosmo_params = rll_params_fase18e_map();
    context.model_kind = RLL_MODEL_LOGISTIC;
    context.enabled_source_mask = RLL_REAL_SOURCE_ALL;
    return context;
}

static rll_u32 rll_real_quantity_to_observable(
    rll_u32 quantity,
    rll_u32 *observable
) {
    if (observable == (rll_u32 *)0) {
        return 0u;
    }
    if (quantity == RLL_Q_HUBBLE) {
        *observable = RLL_OBS_HZ_KM_S_MPC;
    } else if (quantity == RLL_Q_FSIGMA8) {
        *observable = RLL_OBS_FSIGMA8;
    } else if (quantity == RLL_Q_BAO_DV_RS) {
        *observable = RLL_OBS_BAO_DV_OVER_RD;
    } else if (quantity == RLL_Q_BAO_DM_RS) {
        *observable = RLL_OBS_BAO_DM_OVER_RD;
    } else if (quantity == RLL_Q_BAO_DH_RS) {
        *observable = RLL_OBS_BAO_DH_OVER_RD;
    } else if (quantity == RLL_Q_CMB_SHIFT_R) {
        *observable = RLL_OBS_CMB_R;
    } else if (quantity == RLL_Q_CMB_ACOUSTIC_SCALE) {
        *observable = RLL_OBS_CMB_LA;
    } else if (quantity == RLL_Q_CMB_OMEGA_B_H2) {
        *observable = RLL_OBS_CMB_OBH2;
    } else if (quantity == RLL_Q_DISTANCE_MODULUS) {
        *observable = RLL_OBS_SN_MU;
    } else {
        return 0u;
    }
    return 1u;
}

static rll_u32 rll_real_double_to_q16(double value, rll_i64 *out) {
    double scaled;
    if (out == (rll_i64 *)0 || value != value) {
        return 0u;
    }
    scaled = value * RLL_REAL_Q16_SCALE;
    if (scaled >= RLL_REAL_I64_BOUND || scaled <= -RLL_REAL_I64_BOUND) {
        return 0u;
    }
    if (scaled >= 0.0) {
        *out = (rll_i64)(scaled + 0.5);
    } else {
        *out = (rll_i64)(scaled - 0.5);
    }
    return 1u;
}

static rll_u32 rll_real_v1_hz_callback(
    rll_real_model_context *context,
    const rll_real_model_request *request,
    rll_i64 *model_q16
) {
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

static rll_u32 rll_real_joint_callback(
    rll_real_model_context *context,
    const rll_real_model_request *request,
    rll_i64 *model_q16
) {
    rll_u32 observable;
    rll_u32 status = RLL_RUN_OK;
    double axis;
    double prediction;

    if ((context->enabled_source_mask & request->dataset_mask) == 0u) {
        return RLL_REAL_MODEL_TOKEN_VAZIO;
    }
    if (!rll_real_quantity_to_observable(request->quantity, &observable)) {
        return RLL_REAL_MODEL_TOKEN_VAZIO;
    }

    axis = (double)request->axis_q16 / RLL_REAL_Q16_SCALE;
    prediction = rll_predict_observable(
        observable,
        axis,
        &context->cosmo_params,
        context->model_kind,
        &status
    );

    if (status != RLL_RUN_OK || prediction < 0.0 ||
        !rll_real_double_to_q16(prediction, model_q16)) {
        return RLL_REAL_MODEL_BLOCKED;
    }
    return RLL_REAL_MODEL_OK;
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

    if (context->profile == RLL_REAL_PROFILE_LCDM_NOMINAL ||
        context->profile == RLL_REAL_PROFILE_RLL_NOMINAL) {
        return rll_real_v1_hz_callback(context, request, model_q16);
    }
    if (context->profile == RLL_REAL_PROFILE_LCDM_JOINT_FASE18E ||
        context->profile == RLL_REAL_PROFILE_RLL_JOINT_FASE18E) {
        return rll_real_joint_callback(context, request, model_q16);
    }
    return RLL_REAL_MODEL_BLOCKED;
}
