#!/usr/bin/env python3
"""Giza 8-bearing spherical geodesic model. Offline, no archaeological claim."""
import argparse
import csv
import json
import math

R_KM = 6371.0088
CENTERS = {
    "Khufu": (29.97917, 31.13417),
    "Khafre": (29.97611, 31.13083),
    "Menkaure": (29.97250, 31.12833),
}
BEARINGS = tuple(range(0, 360, 45))
LABELS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")

def forward(lat, lon, az, km):
    """Great-circle direct formula on a sphere; az is initial TRUE bearing."""
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("invalid geographic origin")
    if not (0 <= az < 360) or not (0 <= km <= math.pi * R_KM):
        raise ValueError("bearing or distance out of supported bounds")
    p, l, a = map(math.radians, (lat, lon, az))
    d = km / R_KM
    p2 = math.asin(max(-1, min(1, math.sin(p)*math.cos(d)
                           + math.cos(p)*math.sin(d)*math.cos(a))))
    l2 = l + math.atan2(math.sin(a)*math.sin(d)*math.cos(p),
                       math.cos(d)-math.sin(p)*math.sin(p2))
    return math.degrees(p2), (math.degrees(l2)+180) % 360-180

def sky_declination(lat, az, elevation=0):
    """Sky direction declination; not a star catalog or magnetic declination."""
    p, a, h = map(math.radians, (lat, az, elevation))
    return math.degrees(math.asin(max(-1, min(1,
        math.sin(p)*math.sin(h)+math.cos(p)*math.cos(h)*math.cos(a)))))

def records(distances=(100, 1000, 10000)):
    for name, (lat, lon) in CENTERS.items():
        for ix, az in enumerate(BEARINGS):
            for km in distances:
                dest_lat, dest_lon = forward(lat, lon, az, km)
                yield {
                    "pyramid": name, "origin_lat": lat, "origin_lon": lon,
                    "true_azimuth_deg": az, "sector": LABELS[ix],
                    "km": km, "lat2": round(dest_lat, 6),
                    "lon2": round(dest_lon, 6),
                    "horizon_declination_deg": round(sky_declination(lat, az), 6),
                    "magnetic_declination_deg": "TOKEN_VAZIO_NO_EPOCH_MODEL",
                    "historical_alignment": "TOKEN_VAZIO",
                }

def self_test():
    assert len(BEARINGS) == 8 and len(set(BEARINGS)) == 8
    assert abs(forward(0, 0, 90, math.pi * R_KM/2)[1]-90) < 1e-8
    assert abs(forward(0, 0, 0, math.pi * R_KM/2)[0]-90) < 1e-8
    assert abs(sky_declination(30, 90)) < 1e-10
    assert abs(sky_declination(30, 0)-60) < 1e-10
    assert abs(sky_declination(30, 180)+60) < 1e-10
    assert len(list(records())) == 72
    try: forward(91, 0, 45, 100)
    except ValueError: pass
    else: raise AssertionError("invalid lat accepted")
    try: forward(0, 0, 45, 21000)
    except ValueError: pass
    else: raise AssertionError("beyond antipode accepted")
    assert all(-180 <= r["lon2"] < 180 for r in records())
    return 10

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default=None, help="optional CSV output path")
    args = parser.parse_args()
    n = self_test()
    rows = list(records())
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps({"structural_tests_passed": n, "rows": len(rows),
                      "claim_allowed": False, "magnetic_ancient_date": None,
                      "shaft_3d_data": None}, sort_keys=True))

if __name__ == "__main__":
    main()
