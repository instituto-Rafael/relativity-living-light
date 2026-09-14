"""Tests for tools/check_rll_report_claim_language.py — claim-language gate."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "tools" / "check_rll_report_claim_language.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_rll_report_claim_language", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_scan(path: Path, claim_status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"claim_status": claim_status, "blocking_reasons": [], "warnings": []}),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def test_checker_module_loads() -> None:
    checker = load_checker()
    assert hasattr(checker, "check_report")
    assert hasattr(checker, "UNSAFE_WHEN_BLOCKED")


# ---------------------------------------------------------------------------
# CLAIM_BLOCKED: unsafe wording must be flagged
# ---------------------------------------------------------------------------


def test_claim_blocked_flags_rll_vence(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "CLAIM_BLOCKED"}
    report = tmp_path / "report.md"
    report.write_text("O resultado mostra que RLL vence em todos os testes.\n", encoding="utf-8")

    hits = checker.check_report(scan, report)

    assert hits, "Expected unsafe wording to be detected"


def test_claim_blocked_flags_rll_faz_melhor(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "CLAIM_BLOCKED"}
    report = tmp_path / "report.md"
    report.write_text("Observa-se que RLL faz melhor aos dados observados.\n", encoding="utf-8")

    hits = checker.check_report(scan, report)

    assert hits


def test_claim_blocked_flags_rll_prova(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "CLAIM_BLOCKED"}
    report = tmp_path / "report.md"
    report.write_text("RLL prova a aceleração cósmica.\n", encoding="utf-8")

    hits = checker.check_report(scan, report)

    assert hits


def test_claim_blocked_flags_rll_e_favorecido(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "CLAIM_BLOCKED"}
    report = tmp_path / "report.md"
    report.write_text("Portanto RLL é favorecido pelos dados.\n", encoding="utf-8")

    hits = checker.check_report(scan, report)

    assert hits


def test_claim_blocked_flags_rll_wins_english(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "CLAIM_BLOCKED"}
    report = tmp_path / "report.md"
    report.write_text("In summary, RLL wins the model comparison.\n", encoding="utf-8")

    hits = checker.check_report(scan, report)

    assert hits


def test_claim_blocked_flags_rll_supera_cpl(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "CLAIM_BLOCKED"}
    report = tmp_path / "report.md"
    report.write_text("O RLL supera CPL em todos os critérios.\n", encoding="utf-8")

    hits = checker.check_report(scan, report)

    assert hits


# ---------------------------------------------------------------------------
# CLAIM_BLOCKED: safe wording must NOT be flagged
# ---------------------------------------------------------------------------


def test_claim_blocked_allows_safe_wording(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "CLAIM_BLOCKED"}
    report = tmp_path / "report.md"
    report.write_text(
        "Nesta rodada, o scanner bloqueia claim positivo; o resultado favorece outro baseline "
        "ou há lacunas de covariância/metadata.\n",
        encoding="utf-8",
    )

    hits = checker.check_report(scan, report)

    assert not hits


def test_claim_blocked_allows_diagnostic_only_wording(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "CLAIM_BLOCKED"}
    report = tmp_path / "report.md"
    report.write_text(
        "O claim positivo está bloqueado. Delta AICc RLL-CPL = +33. Os0 colapsou para zero.\n",
        encoding="utf-8",
    )

    hits = checker.check_report(scan, report)

    assert not hits


# ---------------------------------------------------------------------------
# Non-CLAIM_BLOCKED status: unsafe phrases are allowed
# ---------------------------------------------------------------------------


def test_pass_limited_allows_positive_wording(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "PASS_LIMITED"}
    report = tmp_path / "report.md"
    # Even "strong" language should not be flagged when status is not CLAIM_BLOCKED
    report.write_text("RLL vence em termos de AICc nesta rodada.\n", encoding="utf-8")

    hits = checker.check_report(scan, report)

    assert not hits, "Unsafe wording should only be flagged when claim_status is CLAIM_BLOCKED"


def test_token_vazio_status_allows_any_wording(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "TOKEN_VAZIO"}
    report = tmp_path / "report.md"
    report.write_text("RLL is favoured by the data.\n", encoding="utf-8")

    hits = checker.check_report(scan, report)

    assert not hits


# ---------------------------------------------------------------------------
# Code blocks are stripped before checking
# ---------------------------------------------------------------------------


def test_claim_blocked_ignores_unsafe_wording_inside_code_blocks(tmp_path: Path) -> None:
    checker = load_checker()
    scan = {"claim_status": "CLAIM_BLOCKED"}
    report = tmp_path / "report.md"
    # The phrase appears only inside a fenced code block
    report.write_text(
        "## Section\n\n```\nExemplo de frase proibida: RLL vence\n```\n\nTexto limpo aqui.\n",
        encoding="utf-8",
    )

    hits = checker.check_report(scan, report)

    assert not hits, "Phrases inside code blocks must not trigger the language checker"
