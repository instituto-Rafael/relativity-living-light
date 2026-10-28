#include "../../native/astroclock52/rll_astroclock_calendar.h"
static int errors;
#define T(x) do{if(!(x))++errors;}while(0)
int main(void){
rac_input a={0u,RAC_VALID_ALL};rac_output o;
rac_u32 i;
T(rac_calendar(&a,&o)==RAC_OK&&!o.historical_date_claim);
a.day_index=365u;T(rac_calendar(&a,&o)==RAC_OK&&o.tzolkin_day_index==105u&&o.haab_day_index==0);
a.day_index=18980u;T(rac_calendar(&a,&o)==RAC_OK&&o.calendar_round_day==0&&o.haab_day_index==0&&o.tzolkin_day_index==0);
a.day_index=359u;T(rac_calendar(&a,&o)==RAC_OK&&o.long_count_winal==17&&o.long_count_kin==19);
a.day_index=360u;T(rac_calendar(&a,&o)==RAC_OK&&o.long_count_winal==0&&o.long_count_tun==1);
a.valid_mask=RAC_VALID_DAY;T(rac_calendar(&a,&o)==RAC_MISSING);
a.valid_mask=255u;T(rac_calendar(&a,&o)==RAC_INVALID);
a.valid_mask=RAC_VALID_ALL;
T(rac_calendar((const rac_input*)0,&o)==RAC_INVALID);
T(rac_calendar(&a,(rac_output*)0)==RAC_INVALID);
for(i=0u;i<200000u;++i){
a.day_index=i;
T(rac_calendar(&a,&o)==RAC_OK);
T(o.tzolkin_day_index<260u&&o.haab_day_index<365u&&o.calendar_round_day<18980u);
T(o.model_sector_12<12u&&!o.historical_date_claim);
if(i>=18980u){
rac_input b={i-18980u,RAC_VALID_ALL};rac_output p;
T(rac_calendar(&b,&p)==RAC_OK&&p.tzolkin_day_index==o.tzolkin_day_index&&p.haab_day_index==o.haab_day_index);
}}
return errors?1:0;
}
