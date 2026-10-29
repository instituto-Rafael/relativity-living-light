# RLL — Giza: oito direções, medianas, geodésia e paleomagnetismo (V3)

**Date:** 2026-10-29 | **Status:** HYPOTHESIS / ADDITIVE / claim_allowed=false | **No cosmological-model changes**

This is an append-only, scientifically gated extension of `docs/complementary_studies/GIZA_ISOSCELES_GEODESIC_GATES_20260906_V1.md`. It does not modify the RLL dynamical cosmology/DESI/MCMC pipeline or imply that ancient pyramids determine modern cosmic parameters.

## 0. Truth boundaries

- **G4:** four approximately cardinal face normals of an ordinary square-base pyramid.
- **G8-compass:** eight reference headings 0°,45°,90°,...,315° at three pyramid centers. Mathematical directions only.
- **G8-subface:** possible eight surface normals due to face-center indentations. These are generally close to the four main normals, NOT separated by 45°. Whether original casing retained such indents is debated.
- **G3D-shafts:** four physical channels in Khufu's pyramid. Without surveyed 3D polylines, their precise 3D pointing and observation epoch are TOKEN_VAZIO.
- **MAG:** isogonic curves connect points of equal magnetic declination **at a fixed epoch**. These are NOT astronomical great circles, celestial star paths or eight-directional architectural edges.

## 1. Observational inputs and authority

Approximate pyramid center coordinates (lat,lon; deg; not geodetic survey control):

| Structure | Latitude | Longitude |
|---|---:|---:|
| Khufu | 29.97917 | 31.13417 |
| Khafre | 29.97611 | 31.13083 |
| Menkaure | 29.97250 | 31.12833 |

Source for approximate centers: https://pyramidenvongizeh.com/en/gps-coordinates/ ; replace with the Glen Dash Foundation's reconstructed corners and centers: https://www.dashfoundation.org/Surveys-at-Giza.htm . Scientific orientation study: Nell & Ruggles (2014), https://doi.org/10.1177/0021828614533065 .

Reference NASA ISS imagery (visual confirmation, not precise polygon vertices): https://science.nasa.gov/earth/earth-observatory/pyramids-at-giza-egypt-79253/ (ISS 2012); https://science.nasa.gov/earth/earth-observatory/space-station-view-of-the-pyramids-at-giza-1842/ (ISS 2001).

## 2. Mathematical construction

For a spherical approximation `R=6371.0088km`, initial **true geographic** azimuth `A`, start `phi,lambda` (radians), distance `s`, and `d=s/R`:

`sin(phi2)=sin(phi)*cos(d)+cos(phi)*sin(d)*cos(A)`

`lambda2=lambda+atan2(sin(A)*sin(d)*cos(phi), cos(d)-sin(phi)*sin(phi2))`

Endpoints must be normalised to +/-180° longitude. A geodesic does NOT generally hold a constant compass heading along its full course. Paths beyond the antipode are rejected in the included demonstration code. Input centers are approximate, so high precision outputs are not justified.

Using the approximate centers, computed *initial* bearings: Khufu→Khafre ~223.4°, Khufu→Menkaure ~217.2°, Khafre→Menkaure ~211.0°. These are not face azimuths or evidence of stellar matching. Treat `3 centers × 8 bearings × 3 distances = 72` as **computed demonstration points**, not discovered geographical monuments.

For the idealised Great Pyramid `B=440` cubits, `H=280` cubits, face side edge `L=sqrt(H²+B²/2)=418.569` cubits and triangular face apex angle is `2 asin(B/(2L))≈63.417°`, not 60°. An equilateral face with the same base would require 311.127 cubits of pyramid altitude. Thus the two-equilateral-pyramids interpretation is not the measured geometry.

Illustrative face-center indent `r=0.5m`, side `B=230.34m`: angular shift of a half-face normal is `atan(2r/B)≈0.249°`, not 22.5°. This shift is a geometrical example, not a physical observation. Interpret cautiously: some published research attributes exposed concavity to loss of original casing rather than to an intended eight-faced exterior. See https://journals.univie.ac.at/index.php/integ/article/view/6413 and https://doi.org/10.4236/ad.2023.112004 .

## 3. Astronomical control

At geographic latitude `phi`, initial true azimuth `A`, elevation `h`, direction has geometric celestial declination `sin(dec)=sin(phi)sin(h)+cos(phi)cos(h)cos(A)`. This alone does not identify an actual ancient star. Giza horizon declinations for A=N/E/S/W and h=0 are approximately +60°/0°/-60°/0°; they depend on the chosen latitude and obstruction horizon. To claim a link to Sirius, Orion, Thuban or Kochab: obtain measured shaft 3D segments, observer location, stellar position/precession, proper motion, ancient chronology, horizon model and a complete comparison-star catalog with look-elsewhere control.

## 4. Magnetic control

Present WMM2025 validity is 2025–2029: https://www.ncei.noaa.gov/products/world-magnetic-model . **Never extrapolate WMM2025 to Khufu's construction period.** IGRF is modern historical-era, not automatically a 2500 BCE calculator. Archaeomagnetic models such as GFZ CALS10k.2: https://www.gfz.de/en/section/geomagnetism/data-products-services/mag-models/calsxk-10000-3000-years-bp can model antiquity only with uncertainty and regional data coverage. For declination east-positive: `true_bearing = magnetic_bearing + declination`; define and verify convention. No ancient paleodeclination numeric value was calculated here: TOKEN_VAZIO_PALEOMAG_EPOCH_GRID.

## 5. Global projection and falsifiers

Great-circle rays on a globe make a mathematical projection, not evidence of a planet-sized pyramid. Test vs: (i) H0 cardinal construction; (ii) random sites with same eight-headings grid; (iii) other ancient monuments; (iv) ellipsoid-vs-sphere sensitivity; (v) 3D corner/median error propagation; (vi) actual archaeological inscriptions and separately dated constructions; (vii) compare one stellar epoch vs multiple independent epochs with complexity penalty; (viii) compare true-north and model-specific magnetic-north only at dated epochs. A concentration of apparent alignments under unrestricted selection is expected; correct for multiple hypotheses.

## 6. Code, gates, handoff

Companion minimal offline Python: `scripts/giza_eight_geodesic_v3.py` (stdlib). Its checks establish elementary sphere geometry only. Neither software tests nor NASA photography validate an intentional design. The original Giza package's `data_manifest.md` explicitly lacks authoritative, uncertainty-annotated shaft 3D polylines.

- `F_ok`: scoped construction and source links; three centers, eight directions, mathematical model, magnetic/astronomical separation.
- `F_gap`: TOKEN_VAZIO_3D_SHAFTS; TOKEN_VAZIO_SUBFACE_NORMALS; TOKEN_VAZIO_SURVEY_CORNERS; TOKEN_VAZIO_PALEOMAG_EPOCH_GRID; TOKEN_VAZIO_STAR_CATALOG_CONTROL; TOKEN_VAZIO_HISTORICAL_INTENT.
- `F_next`: retrieve Glen Dash control points and primary shaft polylines, propagate angular uncertainty; reconstruct sky and paleomagnetic field with period-appropriate models; perform randomized geographic null tests. **claim_allowed=false** throughout.
