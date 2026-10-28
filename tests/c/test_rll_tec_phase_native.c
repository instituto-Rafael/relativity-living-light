#include "../../native/climate_tornado_ionosphere/rll_tec_phase.h"
int main(void) {
    rllt_pair p={100,10,3};rllt_result r;
    if(rllt_phase_speed(&p,&r)!=RLLT_OK || r.apparent_speed_m_s!=166 ||
       r.direction_identifiable || r.is_tornado_predictor)return 1;
    p.projected_separation_km=60;
    if(rllt_phase_speed(&p,&r)!=RLLT_OK || r.apparent_speed_m_s!=100)return 2;
    p.valid_mask=1;
    if(rllt_phase_speed(&p,&r)!=RLLT_MISSING || r.apparent_speed_m_s)return 3;
    p.valid_mask=3;p.arrival_delay_minutes=0;
    if(rllt_phase_speed(&p,&r)!=RLLT_INVALID)return 4;
    p.arrival_delay_minutes=-2;
    if(rllt_phase_speed(&p,&r)!=RLLT_INVALID)return 5;
    p.arrival_delay_minutes=10;p.projected_separation_km=501;
    if(rllt_phase_speed(&p,&r)!=RLLT_INVALID)return 6;
    p.projected_separation_km=100;p.valid_mask=0x80;
    if(rllt_phase_speed(&p,&r)!=RLLT_INVALID)return 7;
    if(rllt_phase_speed((const rllt_pair*)0,&r)!=RLLT_INVALID)return 8;
    if(rllt_phase_speed(&p,(rllt_result*)0)!=RLLT_INVALID)return 9;
    return 0;
}
