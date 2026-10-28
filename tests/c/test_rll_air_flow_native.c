#include "../../native/climate_tornado_ionosphere/rll_air_flow.h"
static int fails=0;
#define CHECK(x) do{if(!(x))fails++;}while(0)
int main(void){
  rllf_wind lower={1000,200,-50,RLLF_WIND_ALL},upper={2000,-800,100,RLLF_WIND_ALL},invalid;
  rllf_transport t;
  rllf_shear s;
  unsigned i;
  CHECK(rllf_mass_transport(1200000u,1u,&lower,100u,&t)==RLLF_OK);
  CHECK(t.east_g_m2_s==12000 && t.north_g_m2_s==2400 && t.up_g_m2_s==-600);
  CHECK(t.hydrostatic_drop_pa==1176 && !t.is_weather_warning);
  CHECK(rllf_mass_transport(1200000u,0u,&lower,100u,&t)==RLLF_MISSING);
  CHECK(rllf_mass_transport(1200000u,1u,&lower,0u,&t)==RLLF_INVALID);
  CHECK(rllf_vertical_shear(&lower,&upper,1000u,&s)==RLLF_OK);
  CHECK(s.east_shear_cm_s_km==1000 && s.north_shear_cm_s_km==-1000 && s.up_shear_cm_s_km==150);
  invalid=lower;invalid.valid_mask=0;
  CHECK(rllf_vertical_shear(&invalid,&upper,1000u,&s)==RLLF_MISSING);
  invalid=lower;invalid.east_cm_s=15001;
  CHECK(rllf_vertical_shear(&invalid,&upper,1000u,&s)==RLLF_INVALID);
  CHECK(rllf_mass_transport(1200000u,1u,(const rllf_wind*)0,100u,&t)==RLLF_INVALID);
  CHECK(rllf_mass_transport(1200000u,1u,&lower,100u,(rllf_transport*)0)==RLLF_INVALID);
  CHECK(rllf_vertical_shear(&lower,&upper,1000u,(rllf_shear*)0)==RLLF_INVALID);
  for(i=0u;i<=30000u;i++){
    invalid=lower;invalid.east_cm_s=(rllf_i32)i-15000;
    CHECK(rllf_mass_transport(1200000u,1u,&invalid,100u,&t)==RLLF_OK);
    CHECK((invalid.east_cm_s<0 && t.east_g_m2_s<=0)||
          (invalid.east_cm_s>=0 && t.east_g_m2_s>=0));
    CHECK(!t.is_weather_warning);
  }
  return fails?1:0;
}
