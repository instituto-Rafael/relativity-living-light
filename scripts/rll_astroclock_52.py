#!/usr/bin/env python3
"""Geometric annual sun clock only. Modern obliquity, no historic sky reconstruction."""
from __future__ import annotations
import csv, math, json
from pathlib import Path
DEG=math.pi/180.
OBLIQUITY_DEG=23.44
TROPICAL_YEAR_DAYS=365.24219
SITES=(
 ("chichen_itza_candidate",20.684,-88.568,"approximate site, not surveyed stone"),
 ("xochicalco_alternative",18.803,-99.296,"approximate site, not surveyed cave"),
 ("stonehenge",51.179,-1.826,"approximate site, not surveyed Heel Stone"),
 ("cusco_hatun_rumiyoc",-13.517,-71.978,"approximate site, not surveyed wall"),
 ("florianopolis_dolmen_oracao",-27.600,-48.430,"area only, not surveyed dolmen"),
 ("giza_khufu",29.979,31.134,"approximate site, not surveyed shaft"),
)
def declination(lambd_deg):
    return math.degrees(math.asin(math.sin(OBLIQUITY_DEG*DEG)*math.sin(lambd_deg*DEG)))
def solar_geometry(lat_deg,dec_deg):
    phi,dec=lat_deg*DEG,dec_deg*DEG
    noon=90.-abs(lat_deg-dec_deg)
    x=math.sin(dec)/math.cos(phi)
    if not -1.<=x<=1.:
        return (noon,None,None,None)
    az=math.degrees(math.acos(x))
    shadow=1./math.tan(noon*DEG) if 0.<noon<90. else (0. if noon==90. else None)
    return (noon,az,360.-az,shadow)
def rows():
    out=[]
    for name,lat,lon,precision in SITES:
        for sector in range(12):
            lam=sector*30
            dec=declination(lam)
            noon,az1,az2,shadow=solar_geometry(lat,dec)
            out.append({"site":name,"lat_deg":lat,"lon_deg":lon,
                "site_precision":precision,"sector_12":sector,"lambda_deg":lam,
                "declination_deg":round(dec,5),
                "noon_altitude_deg":round(noon,5),
                "sunrise_ideal_azimuth_deg":None if az1 is None else round(az1,5),
                "sunset_ideal_azimuth_deg":None if az2 is None else round(az2,5),
                "noon_shadow_per_1m":None if shadow is None else round(shadow,5),
                "is_historical_survey":False})
    return out
def run(out_path):
    out=Path(out_path);out.mkdir(parents=True,exist_ok=True)
    rr=rows()
    with (out/"solar_12_sectors_ideal_horizon.csv").open("w",newline="",encoding="utf8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rr[0]));writer.writeheader();writer.writerows(rr)
    receipt={
        "schema":"rll.astroclock52.geometry_screen.v1",
        "state":"GEOMETRIC_APPROXIMATION_NOT_ARCHAEOLOGICAL_CALIBRATION",
        "claim_allowed":False,
        "sites":len(SITES),"synthetic_site_sector_rows":len(rr),
        "solar_obliquity_deg":OBLIQUITY_DEG,
        "model":"Mean ecliptic solar longitude at 30-degree intervals, geometric flat horizon",
        "calendar_round_days":18980,
        "solar_52years_days":round(52*TROPICAL_YEAR_DAYS,6),
        "52year_drift_days":round(52*TROPICAL_YEAR_DAYS-18980,6),
        "giza_assumed_south_meridian_shaft_altitude_deg":45.,
        "giza_conditional_target_declination_deg":round(29.979+45.-90.,6),
        "giza_ancient_star_coordinates_calculated":False,
        "archaeological_intent_proven":False,
        "missing":["TOKEN_VAZIO_SITE_SURVEY","TOKEN_VAZIO_LOCAL_HORIZON",
         "TOKEN_VAZIO_DOLMEN_AZIMUTH","TOKEN_VAZIO_STONE_PHOTOGRAMMETRY",
         "TOKEN_VAZIO_GIZA_SHAFT_AZIMUTH_AND_CURVATURE",
         "TOKEN_VAZIO_STAR_PRECESSION_EPOCH","TOKEN_VAZIO_HISTORICAL_INTENT"]
    }
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return receipt
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out",default="artifacts/astroclock52")
    a=p.parse_args();print(json.dumps(run(a.out),sort_keys=True))
