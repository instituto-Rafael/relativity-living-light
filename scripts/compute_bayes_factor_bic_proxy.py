#!/usr/bin/env python3
"""BIC-proxy para Fator de Bayes RLL/ΛCDM — fecha TOKEN_VAZIO F-COS-04 com resultado honesto.

Base: resultado do joint likelihood (64 pontos Pantheon+ + DESI DR2 BAO) onde
RLL colapsou para ΛCDM (Ωs0→0). Nesse limite, χ²_RLL ≈ χ²_ΛCDM mas RLL
tem 3 parâmetros extras (Ωs0, z_t, w_t) penalizados pelo BIC.

Aproximação usada:
  BIC = χ² + k·ln(n)
  ln(B₁₀) ≈ −ΔBIC/2   (aproximação de Laplace; válida quando posterior é gaussiana)

Limitação epistêmica [C]:
  Esta é uma aproximação BIC, não um Fator de Bayes por amostragem aninhada (dynesty/MultiNest).
  O resultado é conservador (subestima B₁₀) mas honestamente documentado.
  O valor real de ln(B₁₀) aguarda pipeline G2 (MCMC joint + dynesty).

Output: results/bayes_factor_bic_proxy.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "results" / "bayes_factor_bic_proxy.json"

N_JOINT = 64
K_LCDM = 5
K_RLL = 8

CHI2_LCDM_JOINT = 27.03
CHI2_RLL_JOINT_COLLAPSED = 27.03

F_COS_04_THRESHOLD = -5.0


def bic(chi2: float, k: int, n: int) -> float:
    return chi2 + k * math.log(n)


def bic_proxy_ln_b10(delta_bic: float) -> float:
    return -delta_bic / 2.0


def jeffreys_scale(ln_b: float) -> str:
    if ln_b > 5:
        return "Forte evidência PARA RLL"
    if ln_b > 2.5:
        return "Moderada evidência PARA RLL"
    if ln_b > 1:
        return "Fraca evidência PARA RLL"
    if ln_b >= -1:
        return "Inconclusivo"
    if ln_b >= -2.5:
        return "Fraca evidência CONTRA RLL"
    if ln_b >= -5:
        return "Moderada evidência CONTRA RLL"
    return "Forte evidência CONTRA RLL"


def main() -> int:
    bic_lcdm = bic(CHI2_LCDM_JOINT, K_LCDM, N_JOINT)
    bic_rll = bic(CHI2_RLL_JOINT_COLLAPSED, K_RLL, N_JOINT)
    delta_bic = bic_rll - bic_lcdm
    ln_b10 = bic_proxy_ln_b10(delta_bic)
    scale = jeffreys_scale(ln_b10)
    passes_f_cos_04 = ln_b10 > F_COS_04_THRESHOLD

    result = {
        "meta": {
            "script": "compute_bayes_factor_bic_proxy.py",
            "method": "BIC proxy — aproximação de Laplace (ln B₁₀ ≈ −ΔBIC/2)",
            "limitation": "Aproximação conservadora; valor exato aguarda pipeline G2 (dynesty/MultiNest)",
            "source_chi2": "joint likelihood 64 pontos (Pantheon+ + DESI DR2 BAO) — RLL colapsou para Ωs0=0",
            "reference": "08_ARVORE_CONCEITUAL_RLL.md §Nível 3 + §SÍNTESE",
        },
        "inputs": {
            "n_points": N_JOINT,
            "k_lcdm": K_LCDM,
            "k_rll": K_RLL,
            "chi2_lcdm": CHI2_LCDM_JOINT,
            "chi2_rll": CHI2_RLL_JOINT_COLLAPSED,
            "note_rll": "Ωs0→0 no otimizador joint → χ²_RLL ≈ χ²_ΛCDM (pior caso para RLL)",
        },
        "bic": {
            "bic_lcdm": round(bic_lcdm, 4),
            "bic_rll": round(bic_rll, 4),
            "delta_bic_rll_minus_lcdm": round(delta_bic, 4),
            "formula": "ΔBIC = (k_RLL − k_ΛCDM) × ln(n) = 3 × ln(64) = 3 × 4.1589 = 12.4767",
        },
        "bayes_factor": {
            "ln_B10_proxy": round(ln_b10, 4),
            "jeffreys_scale": scale,
            "threshold_f_cos_04": F_COS_04_THRESHOLD,
            "passes_f_cos_04": passes_f_cos_04,
        },
        "falsifier": {
            "F-COS-04": {
                "claim": "ln(B₁₀) RLL/ΛCDM > −5 — escala Jeffreys",
                "threshold": "ln(B₁₀) > −5",
                "result_proxy": round(ln_b10, 4),
                "outcome": (
                    f"FAIL (proxy) — ln(B₁₀)_proxy = {ln_b10:.2f} < −5 [C] "
                    "— aproximação BIC com Ωs0→0. Resultado definitivo aguarda G2 pipeline."
                ),
            }
        },
        "epistemic_status": (
            "[C] resultado de aproximação BIC com χ²_RLL = χ²_ΛCDM (Ωs0 colapsado). "
            "Este é o pior caso para RLL — se a otimização livre com MCMC encontrar Ωs0 > 0 "
            "com χ² significativamente menor, ln(B₁₀) pode melhorar. "
            "[VAZIO P0] resultado definitivo aguarda pipeline G2 (dynesty)."
        ),
        "interpretation": (
            "O colapso Ωs0→0 indica que com parâmetros nominais, "
            "o setor RLL não contribui significativamente para os dados combinados. "
            "O BIC penaliza os 3 parâmetros extras (Ωs0, z_t, w_t) sem ganho em χ², "
            "resultando em ΔBIC = +12.47 e ln(B₁₀) ≈ −6.24. "
            "Esse é o mesmo resultado que sustenta a conclusão de F-COS-03 FAIL "
            "e confirma que claim_allowed = false até MCMC joint G1+G2."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== BIC-Proxy Fator de Bayes RLL/ΛCDM ===")
    print(f"n = {N_JOINT} pontos (joint Pantheon+ + DESI DR2 BAO)")
    print(f"k_ΛCDM = {K_LCDM}  →  BIC_ΛCDM = {bic_lcdm:.4f}")
    print(f"k_RLL  = {K_RLL}  →  BIC_RLL  = {bic_rll:.4f}")
    print(f"ΔBIC(RLL−ΛCDM) = {delta_bic:+.4f}")
    print(f"ln(B₁₀)_proxy  = {ln_b10:.4f}")
    print(f"Escala Jeffreys: {scale}")
    print(f"F-COS-04 (threshold > −5): {'PASS' if passes_f_cos_04 else 'FAIL (proxy)'}")
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
