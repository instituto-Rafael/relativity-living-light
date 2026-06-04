#!/usr/bin/env python3
"""Render a Markdown validation report from the computed artifacts.

The repository documentation consumes this file directly. It contains no
invented numbers: every value is read back from results/validation_summary.json
produced by compute_validation.py. Stdlib only.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def main() -> int:
    summary = json.loads((RESULTS / "validation_summary.json").read_text(encoding="utf-8"))
    s = summary["summary"]
    v = summary.get("verdict", {})
    roi = summary["region_of_validity"]

    lines = []
    lines.append("# Validacao Real RLL vs LCDM — relatorio automatico\n")
    lines.append(f"_Gerado em {summary['generated_utc']} UTC. "
                 f"Todos os numeros sao lidos dos artefatos; nenhum e inventado._\n")
    lines.append(f"**Regiao de validade:** z in [{roi['z_min']}, {roi['z_max']}] "
                 f"(onde DESI DR2 + cronometros cosmicos existem).\n")

    lines.append("## Comparacao de modelos\n")
    lines.append("| modelo | chi2 | chi2/dof | AIC | BIC | falsificado (BAO/Hz) |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for m, d in s.items():
        lines.append(f"| {m} | {d['chi2_total']} | {d['chi2_per_dof']} | "
                     f"{d['aic']} | {d['bic']} | {d['falsified_bao']}/{d['falsified_hz']} |")
    lines.append("")

    if v:
        lines.append("## Veredito\n")
        lines.append(f"- Delta chi2 ({v['compared']}): **{v['delta_chi2']}**")
        lines.append(f"- Preferido por AIC: **{v['preferred_by_aic']}**")
        lines.append(f"- Preferido por BIC: **{v['preferred_by_bic']}**")
        lines.append(f"- Limiar de falsificabilidade: {v['reject_sigma']} sigma (media de |pull|)\n")

    lines.append("## Leitura honesta\n")
    pref = v.get("preferred_by_bic", "LCDM")
    any_fals = any(d["falsified_bao"] or d["falsified_hz"] for d in s.values())
    lines.append(f"- Modelo preferido pelos dados atuais: **{pref}**.")
    lines.append(f"- Algum modelo falsificado na regiao de validade: **{'sim' if any_fals else 'nao'}**.")
    lines.append("- RLL permanece testavel: a amplitude do setor de superposicao (Os) e o ponto/largura")
    lines.append("  de transicao (zt, wt) podem ser ajustados e re-testados sem mudar o pipeline.\n")

    lines.append("## Figuras\n")
    for fn, cap in [("hubble_diagram.png", "H(z): modelos vs cronometros cosmicos reais"),
                    ("bao_distances.png", "Distancias BAO: DESI DR2 vs modelos"),
                    ("residual_pulls.png", "Pulls residuais por ponto"),
                    ("model_comparison_bars.png", "Comparacao chi2 / AIC / BIC")]:
        lines.append(f"### {cap}")
        lines.append(f"![{cap}](figures/{fn})\n")

    lines.append("## Artefatos\n")
    lines.append("- `results/validation_summary.json` — resumo completo + parametros")
    lines.append("- `results/model_comparison.csv` — uma linha por modelo")
    lines.append("- `results/per_point_predictions.csv` — predicao e pull por ponto")
    lines.append("- `results/figures/*.png` — figuras\n")

    out = RESULTS / "RELATORIO_VALIDACAO.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"report -> {out.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
