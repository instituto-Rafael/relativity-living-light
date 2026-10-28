#include "../../native/climate_tornado_ionosphere/rll_air_mass.h"
static int failures=0;
#define CHECK(a) do{if(!(a)) failures++;}while(0)
static rlla_air base(rlla_u32 x){rlla_air a={101325u,30315u,x,RLLA_PHASE_VAPOR_ONLY,RLLA_VALID_ALL};return a;}
int main(void) {
    rlla_air dry=base(0), wet=base(40000), bad;
    rlla_properties d,w,p;
    rlla_buoyancy b;
    rlla_layer_screen s;
    unsigned i;
    CHECK(rlla_air_properties(&dry,&d)==RLLA_OK);
    CHECK(rlla_air_properties(&wet,&w)==RLLA_OK);
    CHECK(d.rho_dry_mg_m3==1164398u);
    CHECK(d.rho_moist_mg_m3==1164398u);
    CHECK(w.rho_moist_mg_m3==1146792u);
    CHECK(w.virtual_temperature_ck==30780u);
    CHECK(w.vapor_mass_ppm==25261u);
    CHECK(w.rho_moist_mg_m3<d.rho_moist_mg_m3);
    CHECK(rlla_parcel_buoyancy(&dry,&wet,&b)==RLLA_OK && b.buoyancy_milli_m_s2>0 && !b.is_weather_warning);
    CHECK(rlla_parcel_buoyancy(&wet,&dry,&b)==RLLA_OK && b.buoyancy_milli_m_s2<0);
    bad=wet;bad.pressure_pa=100000;
    CHECK(rlla_parcel_buoyancy(&dry,&bad,&b)==RLLA_INVALID);
    bad=wet;bad.valid_mask &= (rlla_u8)~RLLA_VALID_VAPOR;
    CHECK(rlla_air_properties(&bad,&p)==RLLA_MISSING && !p.rho_moist_mg_m3);
    bad=wet;bad.phase=RLLA_PHASE_CLOUD_OR_PRECIP;
    CHECK(rlla_air_properties(&bad,&p)==RLLA_UNSUPPORTED_PHASE);
    bad=wet;bad.vapor_volume_ppm=40001;
    CHECK(rlla_air_properties(&bad,&p)==RLLA_INVALID);
    bad=wet;bad.temperature_ck=17999;
    CHECK(rlla_air_properties(&bad,&p)==RLLA_INVALID);
    bad=wet;bad.valid_mask=0xff;
    CHECK(rlla_air_properties(&bad,&p)==RLLA_INVALID);
    CHECK(rlla_air_properties((const rlla_air*)0,&p)==RLLA_INVALID);
    CHECK(rlla_air_properties(&dry,(rlla_properties*)0)==RLLA_INVALID);
    bad=dry;bad.temperature_ck=29665;
    CHECK(rlla_layer_dry_screen(&dry,&bad,0,1000,&s)==RLLA_OK && s.class_code==1);
    bad=dry;bad.temperature_ck=29135;
    CHECK(rlla_layer_dry_screen(&dry,&bad,0,1000,&s)==RLLA_OK && s.class_code==-1);
    bad=dry;bad.temperature_ck=29335;
    CHECK(rlla_layer_dry_screen(&dry,&bad,0,1000,&s)==RLLA_OK && s.class_code==0);
    CHECK(rlla_layer_dry_screen(&dry,&bad,0,0,&s)==RLLA_INVALID);
    for(i=0;i<40001u;i++){
        bad=base(i);
        CHECK(rlla_air_properties(&bad,&p)==RLLA_OK);
        CHECK(p.rho_moist_mg_m3<=p.rho_dry_mg_m3);
        CHECK(p.virtual_temperature_ck>=bad.temperature_ck);
        CHECK(!p.is_weather_warning);
        if(i) CHECK(p.rho_moist_mg_m3<=d.rho_moist_mg_m3);
    }
    return failures?1:0;
}
