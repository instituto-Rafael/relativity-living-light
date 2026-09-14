#!/usr/bin/env python3
"""
rll_balance_report.py

Livro Vivo RAFAELIA — Gerador do Relatório da Balança RLL.

Parábola operacional:
    A balança falou.
    O escrivão não escolhe o prato vencedor.
    Ele registra peso, métrica, limite e próximo teste.

Objetivo:
    Ler um arquivo JSON com métricas de modelos cosmológicos e gerar
    relatório Markdown + JSON com decisão auditável.

Exemplo:
    python scripts/rll_balance_report.py \
      --input artifacts/joint_real_likelihood.json \
      --output-md artifacts/rll_balance_report.md \
      --output-json artifacts/rll_balance_report.json \
      --metric bic

Compatibilidade:
    - Python 3.8+
    - Somente biblioteca padrão

Status epistemológico:
    RESULTADO_COMPUTACIONAL quando executado com JSON real.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import pathlib
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

LOWER_IS_BETTER = {"chi2", "chisq", "chi_square", "aic", "aicc", "bic"}
HIGHER_IS_BETTER = {"evidence", "log_evidence", "bayes_factor", "bf"}
DEFAULT_BASELINES = ("LCDM", "ΛCDM", "wCDM", "CPL")
DEFAULT_RLL_NAMES = ("RLL", "RelativityLivingLight", "relativity_living_light")

MetricMap = Dict[str, Optional[float]]
ModelRow = Dict[str, Any]


def _now_id() -> str:
    return _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S-utc")


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if math.isfinite(float(value)):
            return float(value)
        return None
    if isinstance(value, str):
        text = value.strip().replace(",", ".")
        if text.upper() in {"", "NA", "N/A", "NONE", "NULL", "TOKEN_VAZIO"}:
            return None
        try:
            out = float(text)
        except ValueError:
            return None
        if math.isfinite(out):
            return out
    return None


def _norm_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def _norm_model_name(name: str) -> str:
    return name.strip().replace("Λ", "L").lower()


def _extract_metrics(obj: Dict[str, Any]) -> MetricMap:
    aliases = {
        "chi2": ("chi2", "chisq", "chi_square", "chi²", "χ²"),
        "aic": ("aic",),
        "aicc": ("aicc", "aic_c", "aic corrected", "aic_corrected"),
        "bic": ("bic",),
        "evidence": ("evidence", "log_evidence", "logevidence", "lnz", "logz"),
        "bayes_factor": ("bayes_factor", "bf", "bayesfactor"),
    }
    normalized = {_norm_key(str(k)): v for k, v in obj.items()}
    result: MetricMap = {}
    for canonical, keys in aliases.items():
        value = None
        for key in keys:
            value = _to_float(normalized.get(_norm_key(key)))
            if value is not None:
                break
        result[canonical] = value
    return result


def _model_entry(name: str, obj: Dict[str, Any]) -> ModelRow:
    row: ModelRow = {
        "name": str(name),
        "metrics": _extract_metrics(obj),
        "raw": obj,
    }
    params = obj.get("params") or obj.get("parameters") or obj.get("fit") or {}
    if isinstance(params, dict):
        row["params"] = params
    return row


def _iter_candidate_model_dicts(data: Any) -> Iterable[Tuple[str, Dict[str, Any]]]:
    """Yield model-like dictionaries from common JSON shapes."""
    if isinstance(data, list):
        for idx, item in enumerate(data):
            if isinstance(item, dict):
                name = item.get("model") or item.get("name") or item.get("label") or f"model_{idx}"
                yield str(name), item
        return

    if not isinstance(data, dict):
        return

    # Shape: {"models": [{...}, {...}]}
    for list_key in ("models", "results", "fits", "comparisons"):
        value = data.get(list_key)
        if isinstance(value, list):
            for idx, item in enumerate(value):
                if isinstance(item, dict):
                    name = item.get("model") or item.get("name") or item.get("label") or f"{list_key}_{idx}"
                    yield str(name), item

    # Shape: {"LCDM": {chi2: ...}, "RLL": {...}}
    for key, value in data.items():
        if isinstance(value, dict):
            metrics = _extract_metrics(value)
            if any(v is not None for v in metrics.values()):
                yield str(key), value

    # Shape: flat single model dict with field model/name and metrics
    metrics = _extract_metrics(data)
    if any(v is not None for v in metrics.values()):
        name = data.get("model") or data.get("name") or "single_model"
        yield str(name), data


def load_models(path: pathlib.Path) -> List[ModelRow]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    seen = set()
    rows: List[ModelRow] = []
    for name, obj in _iter_candidate_model_dicts(data):
        key = (name, json.dumps(obj, sort_keys=True, default=str))
        if key in seen:
            continue
        seen.add(key)
        rows.append(_model_entry(name, obj))
    return rows


def metric_direction(metric: str) -> str:
    m = _norm_key(metric)
    if m in HIGHER_IS_BETTER:
        return "higher"
    return "lower"


def get_metric(row: ModelRow, metric: str) -> Optional[float]:
    return row.get("metrics", {}).get(_norm_key(metric))


def is_rll(row: ModelRow, names: Iterable[str] = DEFAULT_RLL_NAMES) -> bool:
    n = _norm_model_name(row["name"])
    return any(_norm_model_name(x) == n or "rll" == n or n.endswith("rll") for x in names)


def is_baseline(row: ModelRow, names: Iterable[str] = DEFAULT_BASELINES) -> bool:
    n = _norm_model_name(row["name"])
    return any(_norm_model_name(x) == n for x in names) or not is_rll(row)


def choose_winner(rows: List[ModelRow], metric: str) -> Tuple[Optional[ModelRow], List[ModelRow]]:
    candidates = [row for row in rows if get_metric(row, metric) is not None]
    direction = metric_direction(metric)
    if not candidates:
        return None, []
    reverse = direction == "higher"
    ranked = sorted(candidates, key=lambda r: get_metric(r, metric), reverse=reverse)  # type: ignore[arg-type]
    return ranked[0], ranked


def nearly_equal(a: Optional[float], b: Optional[float], tol: float) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= tol


def decide(rows: List[ModelRow], metric: str, tolerance: float) -> Dict[str, Any]:
    winner, ranked = choose_winner(rows, metric)
    rll_rows = [r for r in rows if is_rll(r)]
    baseline_rows = [r for r in rows if is_baseline(r)]

    if not rows:
        return {
            "state": "EXECUCAO_INVALIDA",
            "winner": None,
            "reason": "Nenhum modelo foi extraído do JSON.",
        }
    if winner is None:
        return {
            "state": "DADOS_INSUFICIENTES",
            "winner": None,
            "reason": f"Nenhum modelo possui a métrica '{metric}'.",
        }
    if not rll_rows:
        return {
            "state": "DADOS_INSUFICIENTES",
            "winner": winner["name"],
            "reason": "Nenhuma linha RLL foi identificada.",
        }

    rll_best, _ = choose_winner(rll_rows, metric)
    base_best, _ = choose_winner(baseline_rows, metric)

    if rll_best is None:
        return {
            "state": "DADOS_INSUFICIENTES",
            "winner": winner["name"],
            "reason": f"RLL não possui a métrica '{metric}'.",
        }

    rll_value = get_metric(rll_best, metric)
    base_value = get_metric(base_best, metric) if base_best else None

    if base_best and nearly_equal(rll_value, base_value, tolerance):
        return {
            "state": "RLL_COLAPSA_BASELINE",
            "winner": "empate/degenerescencia",
            "reason": (
                f"RLL e baseline '{base_best['name']}' têm valores equivalentes "
                f"em '{metric}' dentro da tolerância {tolerance}."
            ),
        }

    if is_rll(winner):
        return {
            "state": "RLL_VENCE",
            "winner": winner["name"],
            "reason": f"RLL obteve o melhor valor declarado para '{metric}'.",
        }

    if base_best is not None and winner["name"] == base_best["name"]:
        return {
            "state": "RLL_PERDE",
            "winner": winner["name"],
            "reason": f"Baseline '{winner['name']}' superou RLL em '{metric}'.",
        }

    return {
        "state": "RLL_EMPATA",
        "winner": winner["name"],
        "reason": "Resultado comparativo não separou claramente RLL dos baselines.",
    }


def format_value(value: Optional[float]) -> str:
    if value is None:
        return "TOKEN_VAZIO"
    return f"{value:.10g}"


def table_md(rows: List[ModelRow], metric: str) -> str:
    headers = ["Modelo", "χ²", "AIC", "AICc", "BIC", "Evidência", "Bayes factor", "Papel"]
    lines = ["| " + " | ".join(headers) + " |", "|---|---:|---:|---:|---:|---:|---:|---|"]
    winner, ranked = choose_winner(rows, metric)
    winner_name = winner["name"] if winner else None
    for row in rows:
        m = row["metrics"]
        role = "RLL" if is_rll(row) else "BASELINE"
        name = row["name"]
        if name == winner_name:
            name = f"**{name}**"
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    format_value(m.get("chi2")),
                    format_value(m.get("aic")),
                    format_value(m.get("aicc")),
                    format_value(m.get("bic")),
                    format_value(m.get("evidence")),
                    format_value(m.get("bayes_factor")),
                    role,
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def build_report(input_path: pathlib.Path, rows: List[ModelRow], metric: str, tolerance: float) -> Dict[str, Any]:
    decision = decide(rows, metric, tolerance)
    return {
        "report_id": f"{_now_id()}-rll-balance",
        "input": str(input_path),
        "metric": metric,
        "metric_direction": metric_direction(metric),
        "tolerance": tolerance,
        "decision": decision,
        "models": [
            {
                "name": row["name"],
                "role": "RLL" if is_rll(row) else "BASELINE",
                "metrics": row["metrics"],
                "params": row.get("params", {}),
            }
            for row in rows
        ],
        "status_epistemologico": "RESULTADO_COMPUTACIONAL",
        "limitations": [
            "Este relatório compara somente métricas presentes no JSON de entrada.",
            "Vitória local em métrica não equivale a prova científica universal.",
            "Bayes factor/evidência dependem dos priors e do método de integração usados.",
            "Se o JSON de entrada mistura dados reais e sintéticos, a decisão deve declarar essa limitação.",
        ],
        "next_test": "Repetir com dados, priors, seeds e tolerâncias declarados; gerar artefatos versionados.",
    }


def render_markdown(report: Dict[str, Any]) -> str:
    rows = [
        {"name": m["name"], "metrics": m["metrics"]}
        for m in report["models"]
    ]
    decision = report["decision"]
    metric = report["metric"]
    return f"""# Relatório da Balança RLL

> Gerado por `scripts/rll_balance_report.py`  
> Status epistemológico: `{report['status_epistemologico']}`  
> Regra: uma hipótese que não aceita perder ainda não entrou na ciência.

## Parábola do escrivão

A balança falou.

O escrivão não escolheu o prato vencedor.

Ele apenas escreveu:

```text
resultado bruto → métrica comparada → decisão → limite → próximo teste
```

Assim, amanhã ninguém precisa lembrar de cabeça o que a balança já disse.

## Entrada

```text
{report['input']}
```

## Métrica decisória

```text
{metric} ({report['metric_direction']}_is_better)
```

Tolerância:

```text
{report['tolerance']}
```

## Tabela de modelos

{table_md(rows, metric)}

## Decisão

```yaml
state: {decision.get('state')}
winner: {decision.get('winner')}
reason: {decision.get('reason')}
```

## Limites

""" + "\n".join(f"- {item}" for item in report["limitations"]) + f"""

## Próximo teste

```text
{report['next_test']}
```

## Retroalimentar[3]

- **F_ok:** a execução transformou JSON de métricas em decisão auditável.
- **F_gap:** a decisão depende da qualidade do JSON, dos dados e das métricas disponíveis.
- **F_next:** ligar este script ao workflow para publicar `rll_balance_report.md` como artefato.
"""


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an auditable RLL balance report from model metrics JSON.")
    parser.add_argument("--input", required=True, help="Input JSON containing model metrics.")
    parser.add_argument("--output-md", default="rll_balance_report.md", help="Output Markdown report path.")
    parser.add_argument("--output-json", default="rll_balance_report.json", help="Output normalized JSON report path.")
    parser.add_argument("--metric", default="bic", help="Decision metric: bic, aicc, aic, chi2, evidence, bayes_factor.")
    parser.add_argument("--tolerance", type=float, default=1e-9, help="Tolerance for declaring collapse/equivalence.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    input_path = pathlib.Path(args.input)
    output_md = pathlib.Path(args.output_md)
    output_json = pathlib.Path(args.output_json)

    try:
        rows = load_models(input_path)
        report = build_report(input_path, rows, args.metric, args.tolerance)
    except Exception as exc:  # keep CLI useful in CI
        report = {
            "report_id": f"{_now_id()}-rll-balance",
            "input": str(input_path),
            "metric": args.metric,
            "decision": {
                "state": "EXECUCAO_INVALIDA",
                "winner": None,
                "reason": f"Falha ao processar JSON: {exc}",
            },
            "models": [],
            "status_epistemologico": "RESULTADO_COMPUTACIONAL",
            "limitations": ["A execução falhou antes da comparação de modelos."],
            "next_test": "Corrigir o JSON de entrada e repetir.",
        }

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(report), encoding="utf-8")
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    state = report.get("decision", {}).get("state", "TOKEN_VAZIO")
    print(f"RLL_BALANCE_STATE={state}")
    print(f"RLL_BALANCE_MARKDOWN={output_md}")
    print(f"RLL_BALANCE_JSON={output_json}")
    return 0 if state != "EXECUCAO_INVALIDA" else 2


if __name__ == "__main__":
    raise SystemExit(main())
