# RLL Ω — Archaeoastronomy clock geometric calibration V1

Status: **GEOMETRIC_REFERENCE_ONLY**, `claim_allowed=false`, `PROMOTION=HOLD`.

User research objects: Xochicalco (not Chichén Itzá), Chichén Itzá/Kukulcán, Stonehenge, Trilha Dólmen da Oração Florianópolis, Inca Twelve-Angled Stone Cusco, Giza Khufu Great Pyramid shaft. Preserve these as distinct cultural and engineering evidence, not derivative claims.

Implemented `scripts/rll_archaeoastronomy_clock_v1.py`: offline stdlib, six documented approximate site positions. Ideal point-source horizon sunrise/sunset from true north: `cos(A) = sin(delta)/cos(latitude)` at horizon h=0°, with delta in {+23.44°,0°,-23.44°}. Horizon=0 is a geometrical ideal, NOT measured terrain or visible solar limb. Results: Stonehenge summer (north solstice) sunrise 50.614°, winter (south solstice) sunset 230.614°; Dólmen Florianópolis north solstice sunrise 63.331°, south solstice sunrise 116.669°. Four mathematical invariants/6 sites x3 solar marks in local run. These are *expected geometric directions*, not monument sightline orientations.

Falsifiers/gaps: no surveyed stone/dolmen shadows, visibility/height/camera, shape of Kukulcán pyramid stairs, interior Xochicalco zenith tube, or 3D Great Pyramid south shaft. Khufu Orion astronomical shaft dating requires orientation, construction chronology, ancient stellar coordinate precession and proper motion; intentional monarch birth/death/succession clock unsupported. Do not confuse orbital perihelion apsidal precession with inward spiral or Earth's axial precession. No stellar alignment claim made.

Calendar Round Maya: 260-day Tzolk'in (13×20), 365-day Haab (18×20+5); same date every 18,980 days = 52 Haab years, not exact solar-system configuration. Mesoamerican documented calendrical structures differ from 12-month Gregorian design; Inca 12-corner stone is not evidence of 12 monthly shadow pointers. Prior RLL 51-year gravitational recurrence research PR #1139 is independent of the 52-Haab calendar and unverified as physical law.

Volcanic eruptions, earthquake times, asteroid crater chronology and atmosphere/ocean thermodynamics: external controls requiring independently dated observations and uncertainties, not inputs used in this geometric calibration. Protect cultural interpretation, authorship and archaeological site integrity.

Sources:
- UNESCO Xochicalco https://whc.unesco.org/en/list/939
- NASA Chichén Itzá https://science.nasa.gov/earth/earth-observatory/chichen-itza-5349/
- Historic England Stonehenge https://historicengland.org.uk/whats-new/research/back-issues/astronomical-research-at-stonehenge/
- Smithsonian NMAI calendar https://maya.nmai.si.edu/calendar/calendar-system
- Florianópolis community site https://arqueoastronomia.com.br/
- Giza scholarship https://doi.org/10.1007/978-1-4614-6141-8_151

F_ok: geometrical solar azimuth reference. F_gap: measured monuments, ancient epochs, celestial and refraction error bars, surviving source provenance, independent field verification. F_next: survey angles and horizon, compute historical Sun/stars with JPL/ERFA, blind compare actual azimuths and negative randomized controls. Rollback: close research draft, original RLL Climate source unchanged.
