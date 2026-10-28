#include "rll_air_mass.h"
/* Exactly 64 steps; no compiler division helpers on ARM32. */
static rlla_u32 rlla_div64_u32(rlla_u64 n, rlla_u32 den) {
    rlla_u64 rem = 0u;
    rlla_u64 q = 0u;
    unsigned i;
    for (i=64u; i>0u; --i) {
        unsigned bit = i-1u;
        rem = (rem<<1u) | ((n>>bit)&1u);
        if (rem >= (rlla_u64)den) {
            rem -= (rlla_u64)den;
            q |= ((rlla_u64)1u<<bit);
        }
    }
    return (rlla_u32)q; /* validated inputs bound q below 2^32 */
}
static rlla_i32 rlla_sdiv1000(rlla_i32 change, rlla_u32 height_m) {
    rlla_u32 mag = change < 0 ? (rlla_u32)(-change) : (rlla_u32)change;
    rlla_u32 q=rlla_div64_u32((rlla_u64)mag*1000u,height_m);
    return change < 0 ? -(rlla_i32)q:(rlla_i32)q;
}
int rlla_air_properties(const rlla_air *a, rlla_properties *out) {
    rlla_u32 dry, factor;
    if (!out) return RLLA_INVALID;
    out->rho_dry_mg_m3=0u;out->rho_moist_mg_m3=0u;
    out->virtual_temperature_ck=0u;out->vapor_mass_ppm=0u;
    out->is_weather_warning=0u;
    if (!a || (a->valid_mask & (rlla_u8)~RLLA_VALID_ALL)) return RLLA_INVALID;
    if (a->valid_mask != RLLA_VALID_ALL) return RLLA_MISSING;
    if (a->phase != RLLA_PHASE_VAPOR_ONLY) {
        return a->phase == RLLA_PHASE_CLOUD_OR_PRECIP ? RLLA_UNSUPPORTED_PHASE : RLLA_INVALID;
    }
    if (a->pressure_pa < 20000u || a->pressure_pa > 110000u ||
        a->temperature_ck < 18000u || a->temperature_ck > 34000u ||
        a->vapor_volume_ppm > 40000u) return RLLA_INVALID;
    /* Ideal mixture: rho/rho_dry = 1 - 0.378 * x_v, x_v is mole fraction. */
    factor = 1000000000u - 378u*a->vapor_volume_ppm;
    dry = rlla_div64_u32((rlla_u64)10000000000ull*a->pressure_pa,
                         28705u*a->temperature_ck); /* Rd = 287.05 J/kg/K */
    out->rho_dry_mg_m3 = dry;
    out->rho_moist_mg_m3 = rlla_div64_u32((rlla_u64)dry*factor,1000000000u);
    out->virtual_temperature_ck = rlla_div64_u32((rlla_u64)a->temperature_ck*1000000000u,factor);
    out->vapor_mass_ppm = rlla_div64_u32((rlla_u64)622u*a->vapor_volume_ppm*1000000u,factor);
    return RLLA_OK;
}
int rlla_parcel_buoyancy(const rlla_air *env, const rlla_air *parcel, rlla_buoyancy *out) {
    rlla_properties pe, pp;
    rlla_i32 diff;
    rlla_u32 mag;
    int se, sp;
    if (!out) return RLLA_INVALID;
    out->buoyancy_milli_m_s2=0;out->is_weather_warning=0;
    se=rlla_air_properties(env,&pe);sp=rlla_air_properties(parcel,&pp);
    if(se!=RLLA_OK) return se;
    if(sp!=RLLA_OK) return sp;
    /* Same-pressure parcel comparison only; otherwise buoyancy is undefined. */
    if(env->pressure_pa!=parcel->pressure_pa) return RLLA_INVALID;
    diff=(rlla_i32)pe.rho_moist_mg_m3-(rlla_i32)pp.rho_moist_mg_m3;
    mag=(rlla_u32)(diff<0?-diff:diff);
    mag=rlla_div64_u32((rlla_u64)mag*9807u,pe.rho_moist_mg_m3);
    out->buoyancy_milli_m_s2=diff<0?-(rlla_i32)mag:(rlla_i32)mag;
    return RLLA_OK;
}
int rlla_layer_dry_screen(const rlla_air *lower, const rlla_air *upper,
                          rlla_u32 height_lower_m, rlla_u32 height_upper_m,
                          rlla_layer_screen *out) {
    rlla_properties pl, pu;
    rlla_i32 delta, grad;
    rlla_u32 dz;
    int sl,su;
    if(!out)return RLLA_INVALID;
    out->virtual_temp_gradient_ck_per_km=0;
    out->dry_lapse_screen_ck_per_km=0;out->class_code=0;out->is_weather_warning=0;
    sl=rlla_air_properties(lower,&pl);su=rlla_air_properties(upper,&pu);
    if(sl!=RLLA_OK)return sl;
    if(su!=RLLA_OK)return su;
    if(height_upper_m<=height_lower_m || height_upper_m>20000u)return RLLA_INVALID;
    dz=height_upper_m-height_lower_m;
    if(dz<100u)return RLLA_INVALID;
    delta=(rlla_i32)pu.virtual_temperature_ck-(rlla_i32)pl.virtual_temperature_ck;
    grad=rlla_sdiv1000(delta,dz);
    out->virtual_temp_gradient_ck_per_km=grad;
    out->dry_lapse_screen_ck_per_km=grad+980;
    out->class_code=(rlla_i32)(out->dry_lapse_screen_ck_per_km>20?1:
                   (out->dry_lapse_screen_ck_per_km < -20?-1:0));
    return RLLA_OK;
}
