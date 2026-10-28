#include "../../native/geocycle_51y/rll_geocycle_falsifier.h"
static int fail=0;
#define CHECK(x) do {if(!(x))++fail;}while(0)
static rllc_annual a;
static void init(unsigned count) {
    unsigned i;
    a.first_year_utc=1873u;a.count=(rllc_u16)count;
    for(i=0;i<RLLC_MAX_YEARS;i++){
        a.valid[i]=(rllc_u8)(i<count);
        a.normalized[i]=(rllc_i16)(((i%51u)*20u)-500);
    }
}
int main(void) {
    rllc_screen r;
    unsigned i;
    init(51u);
    CHECK(rllc_screen_lag(&a,51u,&r)==RLLC_INSUFFICIENT_SPAN);
    CHECK(!r.is_verified_period&&!r.is_earthquake_warning&&!r.is_weather_warning);
    init(102u);
    CHECK(rllc_screen_lag(&a,51u,&r)==RLLC_INSUFFICIENT_SPAN);
    init(153u);
    CHECK(rllc_screen_lag(&a,51u,&r)==RLLC_OK);
    CHECK(r.pair_count==102u && r.lag_mean_absolute_difference_milli==0u);
    CHECK(rllc_screen_lag(&a,50u,&r)==RLLC_OK);
    CHECK(r.lag_mean_absolute_difference_milli>0u);
    CHECK(rllc_screen_lag(&a,52u,&r)==RLLC_INSUFFICIENT_SPAN);
    init(156u);
    CHECK(rllc_screen_lag(&a,52u,&r)==RLLC_OK);
    CHECK(r.lag_mean_absolute_difference_milli>0u);
    init(153u);
    for(i=0;i<153u;i++)a.normalized[i]=0;
    CHECK(rllc_screen_lag(&a,51u,&r)==RLLC_UNIDENTIFIABLE_CONSTANT);
    init(153u);
    for(i=0;i<50u;i++)a.valid[i]=0u;
    CHECK(rllc_screen_lag(&a,51u,&r)==RLLC_INSUFFICIENT_PAIRS);
    init(153u);a.valid[10]=2u;
    CHECK(rllc_screen_lag(&a,51u,&r)==RLLC_INVALID);
    init(153u);a.normalized[1]=1001;
    CHECK(rllc_screen_lag(&a,51u,&r)==RLLC_INVALID);
    init(153u);a.first_year_utc=2000u;
    CHECK(rllc_screen_lag(&a,51u,&r)==RLLC_INVALID);
    init(153u);
    CHECK(rllc_screen_lag((const rllc_annual*)0,51u,&r)==RLLC_INVALID);
    CHECK(rllc_screen_lag(&a,0u,&r)==RLLC_INVALID);
    CHECK(rllc_screen_lag(&a,51u,(rllc_screen*)0)==RLLC_INVALID);
    for(i=0;i<4096u;i++){
        init(153u);
        a.normalized[i%153u]=(rllc_i16)((i%2001u)-1000);
        if(i&1u)a.valid[i%153u]=0u;
        {
           int status=rllc_screen_lag(&a,51u,&r);
           CHECK(status==RLLC_OK || status==RLLC_INSUFFICIENT_PAIRS);
        }
        CHECK(!r.is_verified_period&&!r.is_earthquake_warning&&!r.is_weather_warning);
    }
    return fail?1:0;
}
