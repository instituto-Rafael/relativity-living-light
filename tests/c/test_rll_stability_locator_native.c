#include "../../native/climate_stability_locator/rll_stability_locator.h"
static int failures;
#define CHECK(x) do {if(!(x)) ++failures;} while(0)
static rl_locator_input in;
static void fixture(void) {
    rl_u8 i,j;
    in.issue_minute=30000000; in.forecast_target_minute=30020160; in.count=2;
    for(i=0;i<2u;i++) {
        rl_tile *t=&in.tiles[i];
        t->tile_id=(rl_u16)(20u+i);
        t->latitude_e4=10000;t->longitude_e4=-50000;
        for(j=0;j<RL_N_FEATURES;j++) {
            rl_forecast_feature *f=&t->forecast[j];
            f->z100=(j>=3u)?-100:100;
            f->model_issue_minute=in.issue_minute-60;
            f->available_minute=in.issue_minute-15;
            f->valid_target_minute=in.forecast_target_minute;
            f->is_valid=1u;
        }
        t->older=(rl_observation){in.issue_minute-30,in.issue_minute-15,10080,60,1};
        t->newer=(rl_observation){in.issue_minute-1,in.issue_minute-1,10040,120,1};
    }
}
int main(void) {
    rl_locator_output r; unsigned k;
    fixture(); CHECK(rl_locate_stability(&in,&r)==RL_OK);
    CHECK(r.selected_tile_id==20u&&r.candidate_score_0_600==100u&&r.evaluated_tiles==2u);
    CHECK(r.rapid_30min_state==2u&&!r.forecast_skill_validated&&!r.is_hurricane_warning);
    fixture();in.tiles[0].forecast[2].is_valid=0;
    CHECK(rl_locate_stability(&in,&r)==RL_OK&&r.missing_tiles==1u&&r.selected_tile_id==21u);
    fixture();in.tiles[0].forecast[0].available_minute=in.issue_minute+1;
    CHECK(rl_locate_stability(&in,&r)==RL_INVALID);
    fixture();in.tiles[0].forecast[0].valid_target_minute++;
    CHECK(rl_locate_stability(&in,&r)==RL_INVALID);
    fixture();in.tiles[0].forecast[0].model_issue_minute=in.issue_minute+1;
    CHECK(rl_locate_stability(&in,&r)==RL_INVALID);
    fixture();in.tiles[0].latitude_e4=900001;
    CHECK(rl_locate_stability(&in,&r)==RL_INVALID);
    fixture();in.count=0;
    CHECK(rl_locate_stability(&in,&r)==RL_INVALID);
    fixture();in.forecast_target_minute=in.issue_minute+20161;
    CHECK(rl_locate_stability(&in,&r)==RL_INVALID);
    fixture();in.tiles[0].forecast[0].is_valid=0;
    in.tiles[1].forecast[1].is_valid=0;
    CHECK(rl_locate_stability(&in,&r)==RL_MISSING&&r.evaluated_tiles==0u);
    fixture();in.tiles[0].newer.available_minute=in.issue_minute+1;
    CHECK(rl_locate_stability(&in,&r)==RL_OK&&r.rapid_30min_state==0u);
    fixture();in.tiles[0].newer.pressure_hpa10=10060;
    CHECK(rl_locate_stability(&in,&r)==RL_OK&&r.rapid_30min_state==1u);
    fixture();CHECK(rl_locate_stability((const rl_locator_input*)0,&r)==RL_INVALID);
    fixture();CHECK(rl_locate_stability(&in,(rl_locator_output*)0)==RL_INVALID);
    for(k=0u;k<4096u;k++) {
        int state;
        fixture();
        in.tiles[0].forecast[(k>>1u)%5u].z100=(rl_i32)(k%1201u)-600;
        if(k&1u) in.tiles[1].forecast[3].is_valid=0u;
        if(k&2u) in.tiles[0].newer.valid=0u;
        if(k&4u) in.tiles[0].forecast[1].available_minute=in.issue_minute+1;
        state=rl_locate_stability(&in,&r);
        CHECK(state==RL_OK||state==RL_MISSING||state==RL_INVALID);
        CHECK(!r.forecast_skill_validated&&!r.is_hurricane_warning&&r.candidate_score_0_600<=600u);
    }
    return failures?1:0;
}
