#include "rll_geocycle_falsifier.h"
static rllc_u32 rllc_div_u32(rllc_u32 n, rllc_u32 den) {
    rllc_u32 q=0u, r=0u;
    unsigned i;
    /* 32 fixed steps: no compiler libgcc division on ARM32. den > 0. */
    for (i=32u;i>0u;--i) {
        unsigned bit=i-1u;
        r=(r<<1u)|((n>>bit)&1u);
        if(r>=den){r-=den;q|=1u<<bit;}
    }
    return q;
}
int rllc_screen_lag(const rllc_annual *a, rllc_u16 period_years,
                    rllc_screen *out) {
    unsigned i;
    rllc_u32 sum=0u,pairs=0u,possible;
    rllc_i16 first=0;
    rllc_u8 seen=0u,varied=0u;
    if(!out)return RLLC_INVALID;
    out->candidate_period_years=period_years;
    out->pair_count=0u;
    out->lag_mean_absolute_difference_milli=0u;
    out->is_verified_period=0u;
    out->is_earthquake_warning=0u;
    out->is_weather_warning=0u;
    if(!a || a->count>RLLC_MAX_YEARS ||
       a->first_year_utc<1700u || a->first_year_utc>2100u ||
       (rllc_u32)a->first_year_utc+(rllc_u32)a->count>2101u ||
       period_years<2u || period_years>70u)return RLLC_INVALID;
    for(i=0u;i<(unsigned)a->count;i++){
        if(a->valid[i]>1u || a->normalized[i]<-1000 ||
           a->normalized[i]>1000)return RLLC_INVALID;
        if(a->valid[i]){
            if(!seen){first=a->normalized[i];seen=1u;}
            else if(a->normalized[i]!=first)varied=1u;
        }
    }
    /* >=3 complete candidate cycles is only a SCREENING PRECONDITION,
       never sufficient evidence for an actual recurrence. */
    if((rllc_u32)a->count < 3u*(rllc_u32)period_years)
        return RLLC_INSUFFICIENT_SPAN;
    if(!varied)return RLLC_UNIDENTIFIABLE_CONSTANT;
    possible=(rllc_u32)a->count-(rllc_u32)period_years;
    for(i=period_years;i<(unsigned)a->count;i++){
        if(a->valid[i]&&a->valid[i-period_years]){
            rllc_u32 d;
            int delta=(int)a->normalized[i]-(int)a->normalized[i-period_years];
            d=(rllc_u32)(delta<0?-delta:delta);
            sum+=d; ++pairs;
        }
    }
    out->pair_count=(rllc_u16)pairs;
    /* >=80% paired coverage; this is a data-quality gate, not significance. */
    if(pairs*5u < possible*4u)return RLLC_INSUFFICIENT_PAIRS;
    out->lag_mean_absolute_difference_milli=rllc_div_u32(sum*1000u,pairs);
    return RLLC_OK;
}
