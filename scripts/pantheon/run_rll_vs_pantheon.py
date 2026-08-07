"""Comparação diagnóstica LCDM/CPL/RLL contra Pantheon+SH0ES.

Evidence class: C (calculado). Esta rota usa incerteza diagonal e não substitui
a likelihood canônica full-covariance do Evidence Runner.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

from load_pantheon import load_pantheon
from models_pantheon import fit_model


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="caminho explícito do catálogo Pantheon")
    parser.add_argument(
        "--output",
        default=os.environ.get("RLL_PANTHEON_RESULT_PATH", "RESULTADO_REAL.txt"),
        help="arquivo textual de saída (default: RESULTADO_REAL.txt)",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    dataset = load_pantheon(args.data)
    z = dataset["z"]
    mu = dataset["mu"]
    mu_err = dataset["mu_err"]
    n = len(z)

    print(f"F_ok: N={n} SNe reais (Pantheon+SH0ES, calibradores excluídos)")
    print(f"source={dataset['source_path']}")
    print(f"z range: [{z.min():.4f}, {z.max():.4f}]\n")

    results: dict[str, tuple[np.ndarray, float, int]] = {}
    specs = [
        ("lcdm", [70.0, 0.3], 2, {}),
        ("cpl", [70.0, 0.3, -1.0, 0.0], 4, {}),
        ("rll_original", [70.0, 0.3, -1.0, 0.0], 4, {"z_t": 0.5, "sharpness": 5.0}),
        ("rll_optionA", [70.0, 0.3, -1.0, 0.0], 4, {"z_t": 0.5, "sharpness": 5.0}),
    ]
    for index, (name, x0, k, fixed) in enumerate(specs, start=1):
        print(f"=== Fit {index}/4: {name} ===")
        fit = fit_model(z, mu, mu_err, name, x0=x0, **fixed)
        chi2 = float(fit.fun)
        results[name] = (fit.x, chi2, k)
        print(f"  params={list(np.round(fit.x, 6))} chi2={chi2:.6f} chi2/dof={chi2/(n-k):.6f}")

    print("\n" + "=" * 72)
    print("DIAGNÓSTICO CALCULADO — INCERTEZA DIAGONAL, NÃO FULL-COVARIANCE")
    print("=" * 72)
    print(f"{'Modelo':<16} {'chi2':>12} {'k':>3} {'chi2/dof':>12} {'AIC':>12}")
    for name, (_, chi2, k) in results.items():
        print(f"{name:<16} {chi2:>12.6f} {k:>3} {chi2/(n-k):>12.6f} {chi2+2*k:>12.6f}")

    delta_aic = (results["rll_original"][1] + 8) - (results["lcdm"][1] + 4)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "evidence_class": "C",
        "method": "Pantheon diagonal diagnostic; Nelder-Mead; no full covariance",
        "source_path": dataset["source_path"],
        "n_sne": n,
        "delta_aic_rll_minus_lcdm": delta_aic,
        "claim_allowed": False,
    }
    output.write_text(
        "RESULTADO CALCULADO — RLL vs Pantheon+SH0ES\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"\nΔAIC(RLL original−LCDM)={delta_aic:.6f}")
    print(f"Arquivo salvo: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
