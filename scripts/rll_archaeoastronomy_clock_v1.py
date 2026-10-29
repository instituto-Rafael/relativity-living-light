"""RLL archaeoastronomy offline geometric solar alignment reference; not epoch-corrected."""
import math,json
from pathlib import Path
OBLIQUITY=23.44
SITES=[
 ("xochicalco",18.804,-99.296,"https://whc.unesco.org/document/217489"),
 ("chichen_itza",20+40/60,-(88+32/60),"https://science.gsfc.nasa.gov/attic/sunearthday.nasa.gov/2005/locations/chichen_itza.htm"),
 ("stonehenge",51.178869,-1.826162,"https://historicengland.org.uk/listing/heritage-gateway/results/record/5079bd59-b1b8-4237-b20f-3bc281dbc435/MWI12442"),
 ("dolmen_oracao",-27.590699,-48.429141,"https://buscacomercio.com/cidades/florianopolis/patrimonio-historico/dolmen-da-oracao/"),
 ("pedra_doze_angulos",-13.51601,-71.97625,"https://www.outdooractive.com/es/poi/provincia-de-cusco/piedra-de-los-doce-angulos/807790683/"),
 ("giza_khufu",29.9792,31.1342,"https://www.openstreetmap.org/search?query=Great%20Pyramid%20of%20Giza")
]
def azimuth(latitude, declination, horizon_altitude=0.0):
    p,d,h=map(math.radians,(latitude,declination,horizon_altitude))
    c=(math.sin(d)-math.sin(p)*math.sin(h))/(math.cos(p)*math.cos(h))
    return None if c<-1 or c>1 else math.degrees(math.acos(c))
def calibration():
    rows=[]
    for name,lat,lon,url in SITES:
        event={}
        for key,decl in [("north_solstice",OBLIQUITY),("equinox",0),("south_solstice",-OBLIQUITY)]:
            a=azimuth(lat,decl)
            event[key]=None if a is None else {"sunrise_deg":round(a,3),"sunset_deg":round(360-a,3)}
        rows.append({"id":name,"lat":lat,"lon":lon,"source":url,"events":event})
    return {"schema":"rll.archaeoastronomy.geometric_calibration.v1","claim_allowed":False,"sky_reconstruction":False,"assumption":"ideal horizontal horizon, delta +-23.44deg, no epoch/horizon/refraction/shadow geometry correction","sites":rows,"gaps":["TOKEN_VAZIO_ACTUAL_STONE_AXES","TOKEN_VAZIO_LOCAL_HORIZON","TOKEN_VAZIO_ANCIENT_EPOCH","TOKEN_VAZIO_GIZA_SHAFT_AXIS","TOKEN_VAZIO_CULTURAL_INTENTION"]}
if __name__=="__main__":print(json.dumps(calibration(),indent=2))
