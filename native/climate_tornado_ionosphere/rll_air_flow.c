#include "rll_air_flow.h"
static rllf_u32 div64(rllf_u64 n, rllf_u32 den) {
    rllf_u64 rem=0,q=0;unsigned i;
    for(i=64u;i>0u;--i) {
        unsigned bit=i-1u;
        rem=(rem<<1u)|((n>>bit)&1u);
        if(rem>=den){rem-=den;q|=(rllf_u64)1u<<bit;}
    }
    return (rllf_u32)q;
}
static rllf_u8 in_bounds(const rllf_wind *w) {
    return (rllf_u8)(w->east_cm_s>=-15000 && w->east_cm_s<=15000 &&
                     w->north_cm_s>=-15000 && w->north_cm_s<=15000 &&
                     w->up_cm_s>=-15000 && w->up_cm_s<=15000);
}
static rllf_i32 signed_flux(rllf_u32 rho, rllf_i32 velocity_cm_s) {
    rllf_u32 magnitude=(rllf_u32)(velocity_cm_s<0?-velocity_cm_s:velocity_cm_s);
    rllf_u32 result=div64((rllf_u64)rho*magnitude,100000u);
    return velocity_cm_s<0?-(rllf_i32)result:(rllf_i32)result;
}
int rllf_mass_transport(rllf_u32 rho_mg_m3, rllf_u8 rho_valid,
                        const rllf_wind *wind, rllf_u32 dz_m,
                        rllf_transport *out) {
    if(!out)return RLLF_INVALID;
    out->east_g_m2_s=0;out->north_g_m2_s=0;out->up_g_m2_s=0;
    out->hydrostatic_drop_pa=0;out->is_weather_warning=0;
    if(!wind || (wind->valid_mask & (rllf_u8)~RLLF_WIND_ALL))return RLLF_INVALID;
    if(!rho_valid || wind->valid_mask!=RLLF_WIND_ALL)return RLLF_MISSING;
    if(rho_mg_m3<100000u || rho_mg_m3>2000000u ||
       dz_m==0u || dz_m>1000u || !in_bounds(wind))return RLLF_INVALID;
    out->east_g_m2_s=signed_flux(rho_mg_m3,wind->east_cm_s);
    out->north_g_m2_s=signed_flux(rho_mg_m3,wind->north_cm_s);
    out->up_g_m2_s=signed_flux(rho_mg_m3,wind->up_cm_s);
    out->hydrostatic_drop_pa=div64((rllf_u64)rho_mg_m3*9807u*dz_m,1000000000u);
    return RLLF_OK;
}
static rllf_i32 gradient(rllf_i32 diff,rllf_u32 dz_m) {
    rllf_u32 mag=(rllf_u32)(diff<0?-diff:diff);
    rllf_u32 result=div64((rllf_u64)mag*1000u,dz_m);
    return diff<0?-(rllf_i32)result:(rllf_i32)result;
}
int rllf_vertical_shear(const rllf_wind *lower,const rllf_wind *upper,
                         rllf_u32 dz_m,rllf_shear *out){
    if(!out)return RLLF_INVALID;
    out->east_shear_cm_s_km=0;out->north_shear_cm_s_km=0;out->up_shear_cm_s_km=0;
    out->is_weather_warning=0;
    if(!lower || !upper ||
       (lower->valid_mask & (rllf_u8)~RLLF_WIND_ALL) ||
       (upper->valid_mask & (rllf_u8)~RLLF_WIND_ALL))return RLLF_INVALID;
    if(lower->valid_mask!=RLLF_WIND_ALL || upper->valid_mask!=RLLF_WIND_ALL)return RLLF_MISSING;
    if(dz_m<100u || dz_m>10000u || !in_bounds(lower) || !in_bounds(upper))return RLLF_INVALID;
    out->east_shear_cm_s_km=gradient(upper->east_cm_s-lower->east_cm_s,dz_m);
    out->north_shear_cm_s_km=gradient(upper->north_cm_s-lower->north_cm_s,dz_m);
    out->up_shear_cm_s_km=gradient(upper->up_cm_s-lower->up_cm_s,dz_m);
    return RLLF_OK;
}
