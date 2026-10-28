#include "../../native/climate_tornado_ionosphere/rll_climate_30min.h"
static int fail=0;
#define CHECK(x) do {if (!(x)) ++fail;} while(0)
static rll30_window make(void) {
    rll30_window w={0};
    w.issue_minute_utc=1000;w.count=4;
    w.sample[0]=(rll30_sample){970,250,0,20,7};
    w.sample[1]=(rll30_sample){980,450,10,20,7};
    w.sample[2]=(rll30_sample){990,550,10,20,7};
    w.sample[3]=(rll30_sample){1000,700,40,20,7};
    return w;
}
int main(void){
    rll30_window w=make();rll30_result r;int i;
    CHECK(rll30_evaluate(&w,&r)==RLL30_OK);
    CHECK(r.radar_only_diagnostic && r.tec_perturbation_diagnostic && r.combined_diagnostic);
    CHECK(!r.is_operational_warning && r.available_30min);
    w.sample[3].kp_deci=70;
    CHECK(rll30_evaluate(&w,&r)==RLL30_OK && !r.combined_diagnostic && r.geomagnetic_confounded);
    w=make();w.sample[3].radar_norm_1000=100;
    CHECK(rll30_evaluate(&w,&r)==RLL30_OK && !r.combined_diagnostic && !r.radar_only_diagnostic);
    w=make();w.sample[3].tec_residual_centi_tecu=10;
    CHECK(rll30_evaluate(&w,&r)==RLL30_OK && !r.combined_diagnostic);
    w=make();w.sample[3].minute_utc=1001;
    CHECK(rll30_evaluate(&w,&r)==RLL30_INVALID);
    w=make();w.sample[0].minute_utc=969;
    CHECK(rll30_evaluate(&w,&r)==RLL30_INVALID);
    w=make();w.sample[2].minute_utc=979;
    CHECK(rll30_evaluate(&w,&r)==RLL30_INVALID);
    w=make();w.sample[3].valid_mask=RLL30_RADAR|RLL30_KP;
    CHECK(rll30_evaluate(&w,&r)==RLL30_MISSING);
    w=make();w.sample[3].tec_residual_centi_tecu=20001;
    CHECK(rll30_evaluate(&w,&r)==RLL30_INVALID);
    w=make();w.sample[3].radar_norm_1000=1001;
    CHECK(rll30_evaluate(&w,&r)==RLL30_INVALID);
    w=make();w.sample[3].kp_deci=91;
    CHECK(rll30_evaluate(&w,&r)==RLL30_INVALID);
    w=make();w.sample[3].valid_mask=0x80;
    CHECK(rll30_evaluate(&w,&r)==RLL30_INVALID);
    w=make();w.sample[3].minute_utc=994;
    CHECK(rll30_evaluate(&w,&r)==RLL30_MISSING);
    w=make();w.sample[0].valid_mask=RLL30_KP;
    w.sample[1].valid_mask=RLL30_KP;
    w.sample[2].valid_mask=RLL30_KP;
    CHECK(rll30_evaluate(&w,&r)==RLL30_MISSING);
    w=make();w.count=0;
    CHECK(rll30_evaluate(&w,&r)==RLL30_INVALID);
    CHECK(rll30_evaluate((const rll30_window*)0,&r)==RLL30_INVALID);
    CHECK(rll30_evaluate(&w,(rll30_result*)0)==RLL30_INVALID);
    for(i=0;i<4096;++i){
       w=make();
       w.sample[3].tec_residual_centi_tecu=(rll_i32)(i%700)-350;
       if(i&1) w.sample[3].valid_mask &= (rll_u8)~RLL30_TEC;
       if(i&2) w.sample[3].kp_deci=70;
       if(i&4) w.sample[3].radar_norm_1000=200;
       CHECK(rll30_evaluate(&w,&r)==RLL30_OK || rll30_evaluate(&w,&r)==RLL30_MISSING);
       CHECK(!r.is_operational_warning);
       if(r.combined_diagnostic)CHECK(r.radar_only_diagnostic && r.tec_perturbation_diagnostic && !r.geomagnetic_confounded);
    }
    return fail?1:0;
}
