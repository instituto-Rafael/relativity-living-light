#include "rll_tec_phase.h"
/* Bounded 32-bit long division avoids ARM32 compiler helper symbols. */
static rllt_u32 div32(rllt_u32 a, rllt_u32 b) {
    rllt_u32 q=0, r=0;
    unsigned i;
    for(i=32u;i>0u;--i) {
        unsigned shift=i-1u;
        r=(r<<1u)|((a>>shift)&1u);
        if(r>=b){r-=b;q|=1u<<shift;}
    }
    return q;
}
int rllt_phase_speed(const rllt_pair *p, rllt_result *out) {
    rllt_u32 speed;
    if(!out)return RLLT_INVALID;
    out->apparent_speed_m_s=0;
    out->direction_identifiable=0;
    out->is_tornado_predictor=0;
    if(!p)return RLLT_INVALID;
    if(p->valid_mask & (rllt_u8)~3u)return RLLT_INVALID;
    if((p->valid_mask & 3u)!=3u)return RLLT_MISSING;
    if(!p->projected_separation_km || p->projected_separation_km>500u ||
       p->arrival_delay_minutes<=0 || p->arrival_delay_minutes>60)
       return RLLT_INVALID;
    speed=div32(1000u*(rllt_u32)p->projected_separation_km,
                60u*(rllt_u32)p->arrival_delay_minutes);
    if(speed>65535u)return RLLT_INVALID;
    out->apparent_speed_m_s=(rllt_u16)speed;
    return RLLT_OK;
}
