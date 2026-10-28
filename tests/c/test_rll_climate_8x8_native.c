#include "../../native/climate_tornado_ionosphere/rll_climate_8x8.h"
int main(void) {
  rll8_matrix m={0};rll8_audit r;unsigned i;
  if(rll8_validate(&m,&r)!=RLL8_INCOMPLETE || r.missing_physical!=56 || r.valid_gates!=0 || r.is_operational_warning) return 1;
  m.gate_valid_mask=255;
  for(i=0;i<8;i++)m.physical_valid_mask[i]=127;
  m.q16[2][3]=196608;m.q16[6][6]=-196608;
  if(rll8_validate(&m,&r)!=RLL8_OK || r.valid_physical!=56 || r.valid_gates!=8 || r.above_three_sigma!=2 || r.is_operational_warning) return 2;
  m.physical_valid_mask[6]=126;
  if(rll8_validate(&m,&r)!=RLL8_INCOMPLETE || r.missing_physical!=1 || r.valid_physical!=55 || !(r.missing_sector_mask&64))return 3;
  m.physical_valid_mask[6]=255;
  if(rll8_validate(&m,&r)!=RLL8_INVALID) return 4;
  m.physical_valid_mask[6]=127;m.q16[0][2]=0x7fffffff;
  if(rll8_validate(&m,&r)!=RLL8_INVALID)return 5;
  if(rll8_validate((const rll8_matrix*)0,&r)!=RLL8_INVALID)return 6;
  if(rll8_validate(&m,(rll8_audit*)0)!=RLL8_INVALID)return 7;
  return 0;
}
