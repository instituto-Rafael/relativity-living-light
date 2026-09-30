#!/usr/bin/env python3
"""Build an auditable METAR-derived Earth surface field.

SOURCE != DERIVED FIELD != CFD != ASSIMILATION != CLAIM

The script retrieves a bounded set of METAR observations (or a synthetic fixture),
normalizes wind/temperature/pressure, performs inverse-distance interpolation,
computes finite-difference diagnostics, and emits JSON/CSV/SVG plus a hash receipt.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "data/contracts/rll_metar_earth_field.v1.json"
KNOT_TO_MPS = 0.514444
INHG_TO_HPA = 33.8638866667
EARTH_RADIUS_M = 6_371_008.8
MAX_RESPONSE_BYTES = 4 * 1024 * 1024


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_station_ids(text: str) -> list[str]:
    ids: list[str] = []
    for raw in text.split(","):
        station = raw.strip().upper()
        if not station:
            continue
        if not (3 <= len(station) <= 5 and station.isalnum()):
            raise ValueError(f"invalid station identifier: {station!r}")
        if station not in ids:
            ids.append(station)
    if not 3 <= len(ids) <= 40:
        raise ValueError("station list must contain between 3 and 40 unique identifiers")
    return ids


def build_metar_url(base_url: str, allowed_host: str, station_ids: list[str], hours: int) -> str:
    if not 1 <= hours <= 24:
        raise ValueError("hours must be between 1 and 24 for this bounded workflow")
    query = urlencode({"ids": ",".join(station_ids), "format": "json", "hours": str(hours)})
    url = f"{base_url}?{query}"
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != allowed_host:
        raise ValueError("METAR provider URL failed allowlist validation")
    return url


def fetch_metar_json(url: str, allowed_host: str, timeout: int = 30) -> tuple[list[dict[str, Any]], bytes]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != allowed_host:
        raise ValueError("METAR provider URL failed allowlist validation")
    request = Request(
        url,
        headers={
            "User-Agent": "RLL-METAR-Earth-Field/1.0",
            "Accept": "application/json",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
        status = getattr(response, "status", 200)
        final_url = response.geturl()
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("METAR response exceeded byte cap")
    final = urlparse(final_url)
    if final.scheme != "https" or final.hostname != allowed_host:
        raise ValueError("METAR response redirected outside allowlisted host")
    if status == 204 or not body:
        raise ValueError("METAR provider returned no observations")
    if status != 200:
        raise ValueError(f"METAR provider returned HTTP {status}")
    parsed_body = json.loads(body.decode("utf-8"))
    if not isinstance(parsed_body, list):
        raise ValueError("METAR JSON response must be a list")
    return parsed_body, body


def observation_time_key(row: dict[str, Any]) -> float:
    value = row.get("obsTime")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return 0.0
    return 0.0


def latest_per_station(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    newest: dict[str, dict[str, Any]] = {}
    for row in rows:
        station = str(row.get("icaoId") or row.get("stationId") or "").strip().upper()
        if not station:
            continue
        previous = newest.get(station)
        if previous is None or observation_time_key(row) >= observation_time_key(previous):
            newest[station] = row
    return [newest[key] for key in sorted(newest)]


def pressure_hpa(row: dict[str, Any]) -> tuple[float | None, str]:
    slp = as_float(row.get("slp"))
    if slp is not None and 800.0 <= slp <= 1100.0:
        return slp, "slp_hpa"
    altim = as_float(row.get("altim"))
    if altim is None:
        return None, "TOKEN_VAZIO_PRESSURE"
    if 800.0 <= altim <= 1100.0:
        return altim, "altim_hpa"
    if 20.0 <= altim <= 35.0:
        return altim * INHG_TO_HPA, "altim_inHg_converted_to_hpa"
    return None, "TOKEN_VAZIO_PRESSURE_UNRECOGNIZED_UNIT"


def wind_components(wdir_deg: Any, wspd_knots: Any) -> tuple[float | None, float | None, float | None]:
    direction = as_float(wdir_deg)
    speed_knots = as_float(wspd_knots)
    if direction is None or speed_knots is None:
        return None, None, None
    speed = speed_knots * KNOT_TO_MPS
    theta = math.radians(direction % 360.0)
    # Meteorological direction indicates where wind comes FROM.
    u = -speed * math.sin(theta)
    v = -speed * math.cos(theta)
    return u, v, speed


def normalize_observation(row: dict[str, Any]) -> dict[str, Any] | None:
    lat = as_float(row.get("lat"))
    lon = as_float(row.get("lon"))
    if lat is None or lon is None:
        return None
    station = str(row.get("icaoId") or row.get("stationId") or "").strip().upper()
    if not station:
        return None
    u, v, speed = wind_components(row.get("wdir"), row.get("wspd"))
    pressure, pressure_source = pressure_hpa(row)
    return {
        "station": station,
        "obs_time": row.get("obsTime") or row.get("reportTime"),
        "lat": lat,
        "lon": lon,
        "elevation_m": as_float(row.get("elev")),
        "temperature_c": as_float(row.get("temp")),
        "dewpoint_c": as_float(row.get("dewp")),
        "wind_direction_deg": as_float(row.get("wdir")),
        "wind_speed_knots": as_float(row.get("wspd")),
        "wind_speed_m_s": speed,
        "u_m_s": u,
        "v_m_s": v,
        "pressure_hpa": pressure,
        "pressure_source": pressure_source,
        "flight_category": row.get("fltCat"),
        "raw_metar": row.get("rawOb"),
    }


def local_xy_m(lat: float, lon: float, ref_lat: float, ref_lon: float) -> tuple[float, float]:
    x = EARTH_RADIUS_M * math.radians(lon - ref_lon) * math.cos(math.radians(ref_lat))
    y = EARTH_RADIUS_M * math.radians(lat - ref_lat)
    return x, y


def idw_value(
    lat: float,
    lon: float,
    observations: list[dict[str, Any]],
    field: str,
    power: float = 2.0,
) -> float | None:
    usable = [row for row in observations if isinstance(row.get(field), (int, float))]
    if not usable:
        return None
    ref_lat = sum(row["lat"] for row in usable) / len(usable)
    ref_lon = sum(row["lon"] for row in usable) / len(usable)
    px, py = local_xy_m(lat, lon, ref_lat, ref_lon)
    numerator = 0.0
    denominator = 0.0
    for row in usable:
        x, y = local_xy_m(row["lat"], row["lon"], ref_lat, ref_lon)
        d2 = (px - x) ** 2 + (py - y) ** 2
        if d2 < 1.0:
            return float(row[field])
        weight = 1.0 / (d2 ** (power / 2.0))
        numerator += weight * float(row[field])
        denominator += weight
    return numerator / denominator if denominator else None


def field_bounds(observations: list[dict[str, Any]]) -> tuple[float, float, float, float]:
    lats = [row["lat"] for row in observations]
    lons = [row["lon"] for row in observations]
    lat_span = max(max(lats) - min(lats), 0.10)
    lon_span = max(max(lons) - min(lons), 0.10)
    return (
        min(lats) - 0.08 * lat_span,
        max(lats) + 0.08 * lat_span,
        min(lons) - 0.08 * lon_span,
        max(lons) + 0.08 * lon_span,
    )


def finite_diff(
    grid: list[list[dict[str, Any]]],
    iy: int,
    ix: int,
    field: str,
    axis: str,
    spacing_m: float,
) -> float | None:
    ny = len(grid)
    nx = len(grid[0])
    if axis == "x":
        a = max(ix - 1, 0)
        b = min(ix + 1, nx - 1)
        va = grid[iy][a].get(field)
        vb = grid[iy][b].get(field)
        steps = b - a
    else:
        a = max(iy - 1, 0)
        b = min(iy + 1, ny - 1)
        va = grid[a][ix].get(field)
        vb = grid[b][ix].get(field)
        steps = b - a
    if steps == 0 or va is None or vb is None or spacing_m <= 0:
        return None
    return (float(vb) - float(va)) / (steps * spacing_m)


def build_grid(
    observations: list[dict[str, Any]],
    nx: int,
    ny: int,
) -> dict[str, Any]:
    if not 4 <= nx <= 120 or not 4 <= ny <= 120:
        raise ValueError("grid dimensions must each be between 4 and 120")
    if len(observations) < 3:
        raise ValueError("at least three geolocated METAR observations are required")
    lat_min, lat_max, lon_min, lon_max = field_bounds(observations)
    dlat = (lat_max - lat_min) / (ny - 1)
    dlon = (lon_max - lon_min) / (nx - 1)
    ref_lat = (lat_min + lat_max) / 2.0
    dx_m = EARTH_RADIUS_M * math.radians(dlon) * math.cos(math.radians(ref_lat))
    dy_m = EARTH_RADIUS_M * math.radians(dlat)

    rows: list[list[dict[str, Any]]] = []
    for iy in range(ny):
        lat = lat_min + iy * dlat
        row_cells: list[dict[str, Any]] = []
        for ix in range(nx):
            lon = lon_min + ix * dlon
            u = idw_value(lat, lon, observations, "u_m_s")
            v = idw_value(lat, lon, observations, "v_m_s")
            temp = idw_value(lat, lon, observations, "temperature_c")
            pressure = idw_value(lat, lon, observations, "pressure_hpa")
            speed = math.hypot(u, v) if u is not None and v is not None else None
            row_cells.append({
                "ix": ix,
                "iy": iy,
                "lat": lat,
                "lon": lon,
                "u_m_s": u,
                "v_m_s": v,
                "wind_speed_m_s": speed,
                "temperature_c": temp,
                "pressure_hpa": pressure,
            })
        rows.append(row_cells)

    for iy in range(ny):
        for ix in range(nx):
            cell = rows[iy][ix]
            du_dx = finite_diff(rows, iy, ix, "u_m_s", "x", dx_m)
            dv_dy = finite_diff(rows, iy, ix, "v_m_s", "y", dy_m)
            dv_dx = finite_diff(rows, iy, ix, "v_m_s", "x", dx_m)
            du_dy = finite_diff(rows, iy, ix, "u_m_s", "y", dy_m)
            dp_dx_hpa = finite_diff(rows, iy, ix, "pressure_hpa", "x", dx_m)
            dp_dy_hpa = finite_diff(rows, iy, ix, "pressure_hpa", "y", dy_m)
            cell["divergence_s_1"] = (
                du_dx + dv_dy if du_dx is not None and dv_dy is not None else None
            )
            cell["vertical_vorticity_s_1"] = (
                dv_dx - du_dy if dv_dx is not None and du_dy is not None else None
            )
            cell["pressure_gradient_x_pa_m"] = dp_dx_hpa * 100.0 if dp_dx_hpa is not None else None
            cell["pressure_gradient_y_pa_m"] = dp_dy_hpa * 100.0 if dp_dy_hpa is not None else None

    return {
        "nx": nx,
        "ny": ny,
        "bounds": {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lon_min": lon_min,
            "lon_max": lon_max,
        },
        "spacing_m": {"dx": dx_m, "dy": dy_m},
        "cells": [cell for row in rows for cell in row],
    }


def write_csv(path: Path, cells: list[dict[str, Any]]) -> None:
    columns = [
        "ix", "iy", "lat", "lon", "u_m_s", "v_m_s", "wind_speed_m_s",
        "temperature_c", "pressure_hpa", "divergence_s_1",
        "vertical_vorticity_s_1", "pressure_gradient_x_pa_m",
        "pressure_gradient_y_pa_m",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for cell in cells:
            writer.writerow({key: cell.get(key) for key in columns})


def svg_escape(text: Any) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_svg(
    path: Path,
    grid: dict[str, Any],
    observations: list[dict[str, Any]],
    source_mode: str,
) -> None:
    width, height = 1200, 800
    margin = 70
    b = grid["bounds"]

    def sx(lon: float) -> float:
        return margin + (lon - b["lon_min"]) / (b["lon_max"] - b["lon_min"]) * (width - 2 * margin)

    def sy(lat: float) -> float:
        return height - margin - (lat - b["lat_min"]) / (b["lat_max"] - b["lat_min"]) * (height - 2 * margin)

    cells = grid["cells"]
    nx, ny = grid["nx"], grid["ny"]
    step_x = max(1, nx // 10)
    step_y = max(1, ny // 7)
    speeds = [c["wind_speed_m_s"] for c in cells if c.get("wind_speed_m_s") is not None]
    max_speed = max(speeds) if speeds else 1.0

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="70" y="35" font-size="24" font-family="sans-serif">RLL METAR Earth diagnostic field</text>',
        f'<text x="70" y="58" font-size="14" font-family="sans-serif">source={svg_escape(source_mode)} · IDW diagnostic, not CFD/assimilation</text>',
        f'<rect x="{margin}" y="{margin}" width="{width-2*margin}" height="{height-2*margin}" fill="none" stroke="black" stroke-width="1"/>',
    ]

    for cell in cells:
        if cell["ix"] % step_x or cell["iy"] % step_y:
            continue
        u = cell.get("u_m_s")
        v = cell.get("v_m_s")
        speed = cell.get("wind_speed_m_s")
        if u is None or v is None or speed is None:
            continue
        x0, y0 = sx(cell["lon"]), sy(cell["lat"])
        scale = 32.0 / max(max_speed, 0.1)
        dx, dy = u * scale, -v * scale
        x1, y1 = x0 + dx, y0 + dy
        angle = math.atan2(y1 - y0, x1 - x0)
        head = 6.0
        a1, a2 = angle + 2.6, angle - 2.6
        hx1, hy1 = x1 + head * math.cos(a1), y1 + head * math.sin(a1)
        hx2, hy2 = x1 + head * math.cos(a2), y1 + head * math.sin(a2)
        parts.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="black" stroke-width="1.2"/>')
        parts.append(f'<path d="M{x1:.1f},{y1:.1f} L{hx1:.1f},{hy1:.1f} M{x1:.1f},{y1:.1f} L{hx2:.1f},{hy2:.1f}" stroke="black" fill="none" stroke-width="1.2"/>')

    for obs in observations:
        x, y = sx(obs["lon"]), sy(obs["lat"])
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="black"/>')
        label = f'{obs["station"]} {obs.get("temperature_c")}°C {obs.get("pressure_hpa")}hPa'
        parts.append(f'<text x="{x+7:.1f}" y="{y-7:.1f}" font-size="12" font-family="sans-serif">{svg_escape(label)}</text>')

    parts.append(
        f'<text x="70" y="{height-20}" font-size="12" font-family="sans-serif">'
        'Wind arrows: interpolated u/v from METAR point observations; derivatives are finite-difference diagnostics.'
        '</text>'
    )
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def observation_time_range(observations: list[dict[str, Any]]) -> dict[str, Any]:
    values = [observation_time_key({"obsTime": x.get("obs_time")}) for x in observations]
    values = [v for v in values if v > 0]
    if not values:
        return {"min_utc": None, "max_utc": None}
    return {
        "min_utc": datetime.fromtimestamp(min(values), tz=timezone.utc).isoformat(),
        "max_utc": datetime.fromtimestamp(max(values), tz=timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stations", default="SBGR,SBSP,SBKP,SBSJ")
    parser.add_argument("--hours", type=int, default=2)
    parser.add_argument("--nx", type=int, default=24)
    parser.add_argument("--ny", type=int, default=18)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/science/earth_metar_field"))
    args = parser.parse_args()

    contract = load_json(CONTRACT_PATH)
    provider = contract["provider"]
    station_ids = parse_station_ids(args.stations)
    request_url = build_metar_url(provider["base_url"], provider["allowed_host"], station_ids, args.hours)

    if args.fixture:
        raw_rows = load_json(args.fixture)
        raw_bytes = json.dumps(raw_rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
        source_mode = "SYNTHETIC_FIXTURE_NOT_OBSERVATION"
        source_locator = str(args.fixture)
    else:
        raw_rows, raw_bytes = fetch_metar_json(request_url, provider["allowed_host"])
        source_mode = "NOAA_NWS_AWC_METAR_OBSERVATION"
        source_locator = request_url

    selected = latest_per_station(raw_rows)
    observations = [x for x in (normalize_observation(row) for row in selected) if x is not None]
    usable_wind = [x for x in observations if x.get("u_m_s") is not None and x.get("v_m_s") is not None]
    if len(usable_wind) < 3:
        raise ValueError("fewer than three stations contain usable wind vectors")

    grid = build_grid(observations, args.nx, args.ny)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    obs_path = out / "metar_observations.normalized.json"
    grid_path = out / "earth_surface_field.json"
    csv_path = out / "earth_surface_field.csv"
    svg_path = out / "earth_surface_field.svg"
    receipt_path = out / "receipt.json"

    obs_path.write_text(json.dumps(observations, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    grid_payload = {
        "schema": "rll.metar_earth_field.v1",
        "source_mode": source_mode,
        "method": contract["method"],
        "units": contract["derived_units"],
        "grid": grid,
        "claim_allowed": False,
    }
    grid_path.write_text(json.dumps(grid_payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(csv_path, grid["cells"])
    write_svg(svg_path, grid, observations, source_mode)

    receipt = {
        "schema": "rll.metar_earth_field.receipt.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_authority": provider["authority"],
        "source_mode": source_mode,
        "source_locator": source_locator,
        "request_url": request_url if not args.fixture else "NOT_EXECUTED_FIXTURE_MODE",
        "upstream_response_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "station_ids_requested": station_ids,
        "station_count_normalized": len(observations),
        "wind_station_count": len(usable_wind),
        "observation_time_range": observation_time_range(observations),
        "grid": {"nx": grid["nx"], "ny": grid["ny"], "bounds": grid["bounds"], "spacing_m": grid["spacing_m"]},
        "derivation": contract["method"],
        "epistemic_boundary": contract["boundaries"],
        "artifacts": {
            str(obs_path): sha256_file(obs_path),
            str(grid_path): sha256_file(grid_path),
            str(csv_path): sha256_file(csv_path),
            str(svg_path): sha256_file(svg_path),
        },
        "gate_status": "FIXTURE_FIELD_READY" if args.fixture else "OBSERVED_FIELD_READY",
        "claim_allowed": False,
        "F_ok": "bounded METAR observations transformed into an auditable diagnostic surface field",
        "F_gap": "sparse point sampling and IDW interpolation do not constitute CFD, assimilation, or a complete atmospheric state",
        "F_next": "co-register Climate Engine fields by source/unit/time and compare only declared diagnostics before any cross-source or cross-planet inference",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate_status": receipt["gate_status"],
        "source_mode": source_mode,
        "stations": len(observations),
        "output_dir": str(out),
        "claim_allowed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
