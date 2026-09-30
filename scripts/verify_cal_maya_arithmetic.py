#!/usr/bin/env python3
"""Verify TOKEN_VAZIO H-CAL-01: Mayan 52-year cycle vs astrophysical candidates.

Arithmetic checks [E]:
  - lcm(365, 260) = 18980 days = 51.965 years ≈ 52 years
  - 18980 / 365.25 = 51.961 Julian years

Astrophysical candidates [H] (no ephemeris data — qualitative comparison):
  - Schwabe solar cycle: ~11 years → 5×11 = 55 years (|52-55|=3)
  - Hale solar cycle: ~22 years → 52/22 = 26/11 ≈ 2.36 (non-integer rational ratio)
  - Jupiter-Saturn conjunction: ~19.859 years (sidereal synodic)
    - 2×19.859 = 39.7 (|52-39.7|=12.3)
    - 2.62×19.859 = 52.03 (illustrative decimal multiplier; proximity alone is not a cycle correspondence)
  - Jupiter orbital period: ~11.862 years → 4×11.862 = 47.45 (|52-47.45|=4.55)
  - Venus synodic period: 583.92 days → 65×583.92 = 37955 days = 103.9 years (2×=207.8; too large)
    Actually: 18980/583.92 = 32.50 Venus synodic periods (also rational near-integer)

TOKEN_VAZIO [VAZIO]: actual ephemeris confirmation of which cycle dominates requires
proper astronomical data not available in this run.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO / "results"

# Calendar constants [E] — exact integers
HAAB_DAYS = 365       # solar approximation (Haab)
TZOLKIN_DAYS = 260    # ritual calendar (Tzolkin)

# Julian year for conversion
JULIAN_YEAR_DAYS = 365.25
TROPICAL_YEAR_DAYS = 365.2422


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


def run_maya_calendar_check() -> dict:
    # Arithmetic [E]
    calendar_round_days = lcm(HAAB_DAYS, TZOLKIN_DAYS)
    calendar_round_julian = calendar_round_days / JULIAN_YEAR_DAYS
    calendar_round_tropical = calendar_round_days / TROPICAL_YEAR_DAYS
    calendar_round_haab = calendar_round_days / HAAB_DAYS

    # Verify divisibility [E]
    haab_cycles = calendar_round_days // HAAB_DAYS
    tzolkin_cycles = calendar_round_days // TZOLKIN_DAYS
    assert calendar_round_days % HAAB_DAYS == 0
    assert calendar_round_days % TZOLKIN_DAYS == 0

    # Astrophysical candidates [H] — no ephemeris, purely algebraic
    candidates = []

    # Schwabe solar cycle
    schwabe = 11.0  # years (approximate)
    multiple_schwabe = calendar_round_julian / schwabe
    candidates.append({
        "name": "Schwabe solar cycle",
        "period_years": schwabe,
        "reference": "[H] observed ~1843, Schwabe; mean period ~11yr (range 9-14)",
        "multiple_of_52": round(multiple_schwabe, 4),
        "nearest_integer_multiple": round(multiple_schwabe),
        "residual_years": round(abs(calendar_round_julian - round(multiple_schwabe) * schwabe), 4),
        "note": "5×11=55yr → |52-55|=3yr; not a close match",
    })

    # Jupiter-Saturn conjunction (approximate mean synodic period)
    jup_sat_synodic = 19.859  # years (mean synodic period Jupiter-Saturn)
    multiple_jup_sat = calendar_round_julian / jup_sat_synodic
    residual_closest = min(
        abs(calendar_round_julian - math.floor(multiple_jup_sat) * jup_sat_synodic),
        abs(calendar_round_julian - math.ceil(multiple_jup_sat) * jup_sat_synodic),
    )
    candidates.append({
        "name": "Jupiter-Saturn synodic conjunction",
        "period_years": jup_sat_synodic,
        "reference": "[H] J-S mean synodic ~19.859yr; 2.62×19.859≈52.03",
        "multiple_of_52": round(multiple_jup_sat, 4),
        "nearest_integer_multiple": round(multiple_jup_sat),
        "residual_years": round(residual_closest, 4),
        "note": "2.62 is a rational decimal approximation and a non-integer multiplier; numerical proximity alone is not evidence of a cycle correspondence",
    })

    # Hale solar cycle (double Schwabe)
    hale = 22.0  # years (approximate)
    multiple_hale = calendar_round_julian / hale
    candidates.append({
        "name": "Hale solar cycle (2× Schwabe)",
        "period_years": hale,
        "reference": "[H] Hale 1908 polarity reversal; ~22yr mean",
        "multiple_of_52": round(multiple_hale, 4),
        "nearest_integer_multiple": round(multiple_hale),
        "residual_years": round(abs(calendar_round_julian - round(multiple_hale) * hale), 4),
        "note": "52/22 = 26/11 ≈ 2.3636; rational but non-integer, so it is not a clean integer-cycle match",
    })

    # Venus synodic period (important in Maya astronomy [E])
    venus_synodic_days = 583.92
    venus_in_calendar_round = calendar_round_days / venus_synodic_days
    candidates.append({
        "name": "Venus synodic period",
        "period_days": venus_synodic_days,
        "period_years": round(venus_synodic_days / JULIAN_YEAR_DAYS, 4),
        "reference": "[E] Dresden Codex records 5 Venus synodic periods = 2920 days = 8 haab",
        "count_in_calendar_round": round(venus_in_calendar_round, 4),
        "nearest_integer": round(venus_in_calendar_round),
        "residual_days": round(abs(calendar_round_days - round(venus_in_calendar_round) * venus_synodic_days), 3),
        "note": "18980/583.92 ≈ 32.50; half-integer; 5 synodic periods = 8 Haab is the documented Maya synchrony [E]",
    })

    # Best candidate by residual
    best = min(candidates, key=lambda c: c.get("residual_years", 999))

    return {
        "meta": {
            "script": "verify_cal_maya_arithmetic.py",
            "date": "2026-07-07",
            "token_vazio_id": "H-CAL-01",
            "priority": "P2",
            "description": "Verificação aritmética do ciclo maia de 52 anos e candidatos astrofísicos",
        },
        "arithmetic_verification": {
            "haab_days": HAAB_DAYS,
            "tzolkin_days": TZOLKIN_DAYS,
            "lcm_days": calendar_round_days,
            "lcm_check_passed": calendar_round_days == 18980,
            "haab_cycles_in_round": haab_cycles,
            "tzolkin_cycles_in_round": tzolkin_cycles,
            "julian_years": round(calendar_round_julian, 6),
            "tropical_years": round(calendar_round_tropical, 6),
            "nominal_52_years_days": 52 * JULIAN_YEAR_DAYS,
            "discrepancy_days": round(calendar_round_days - 52 * JULIAN_YEAR_DAYS, 4),
            "epistemic_status": "[E] — aritmética exata, sem ambiguidade",
        },
        "astrophysical_candidates": candidates,
        "best_algebraic_match": {
            "name": best["name"],
            "residual_years": best.get("residual_years"),
            "note": "Melhor correspondência algébrica — requer efemérides para confirmação física",
        },
        "summary": {
            "calendar_round_days": calendar_round_days,
            "calendar_round_years_julian": round(calendar_round_julian, 4),
            "passes_lcm_check": calendar_round_days == 18980,
            "token_vazio_remaining": (
                "Correspondência com efemérides reais (ciclos heliocêntricos precisos, "
                "dados de atividade solar, observações conjunção J-S) — requer dataset externo"
            ),
        },
        "epistemic_classification": {
            "lcm_arithmetic": "[E] — comprovado por aritmética inteira",
            "52_year_approximation": "[E] — 18980/365.25 = 51.961 anos Julianos",
            "astrophysical_candidates": "[H] — candidatos identificados, sem confirmação de efemérides",
            "causal_link_to_rll": "[VAZIO] — modulação periódica de H(z) local não investigada",
        },
    }


def main() -> int:
    result = run_maya_calendar_check()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "cal_maya_arithmetic_check.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    arith = result["arithmetic_verification"]
    print("=== Verificação Aritmética Ciclo Maia ===")
    print(f"lcm(365, 260) = {arith['lcm_days']} dias  [lcm check: {arith['lcm_check_passed']}]")
    print(f"Equivalência: {arith['julian_years']:.4f} anos Julianos ({arith['tropical_years']:.4f} tropicais)")
    print(f"Discrepância vs 52 anos exatos: {arith['discrepancy_days']:.2f} dias")
    print()
    print("=== Candidatos Astrofísicos ===")
    for c in result["astrophysical_candidates"]:
        name = c["name"]
        residual = c.get("residual_years")
        multiple = c.get("multiple_of_52")
        mult_str = f"{multiple:.3f}×" if multiple is not None else "N/A"
        res_str = f"{residual:.3f} anos" if isinstance(residual, (int, float)) else "N/A"
        print(f"  {name}: {mult_str} → residual {res_str}")
    print()
    best = result["best_algebraic_match"]
    print(f"Melhor correspondência algébrica: {best['name']} (residual {best['residual_years']:.3f} anos)")
    print()
    print(f"Output: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
