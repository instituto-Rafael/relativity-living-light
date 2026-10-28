#include "rll_astroclock_calendar.h"
int rac_calendar(const rac_input *input,rac_output *output){
rac_u32 d;
if(!output)return RAC_INVALID;
output->tzolkin_day_index=0;output->haab_day_index=0;
output->calendar_round_day=0;output->long_count_kin=0;
output->long_count_winal=0;output->long_count_tun=0;
output->model_sector_12=0;output->historical_date_claim=0;
if(!input||(input->valid_mask&(rac_u8)~RAC_VALID_ALL))return RAC_INVALID;
if(input->valid_mask!=RAC_VALID_ALL)return RAC_MISSING;
d=input->day_index;
output->tzolkin_day_index=(rac_u16)(d%260u);
output->haab_day_index=(rac_u16)(d%365u);
output->calendar_round_day=(rac_u16)(d%RAC_ROUND_DAYS);
output->long_count_kin=(rac_u16)(d%20u);
output->long_count_winal=(rac_u16)((d/20u)%18u);
output->long_count_tun=(rac_u16)((d/360u)%20u);
output->model_sector_12=(rac_u8)(((d%365u)*12u)/365u);
return RAC_OK;
}
