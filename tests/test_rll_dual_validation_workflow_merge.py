"""Two-route semantic merge of main's governed Rx and lab's legacy validation.

The normal Rx route is strict stdlib/no-pip; lab's graphical route remains
available independently and only explicit agent/work refs may opt into commits.
"""
from pathlib import Path

import yaml

ROOT=Path(__file__).resolve().parents[1]
CANON=ROOT/".github/workflows/validacao_real.yml"
LEGACY=ROOT/".github/workflows/validacao-real-legacy.yml"


def test_governed_rx_workflow_main_and_lab_continuity() -> None:
    raw=CANON.read_text(encoding="utf-8")
    doc=yaml.safe_load(raw)
    assert "pip install" not in raw
    assert "python3 -m validacao_real.run_rx_pipeline" in raw
    for name in (
        "Validate development security guard",
        "Enforce Rx operation contract",
        "Validate governance bundle consistency",
        "Rx zero-dependency validation pipeline",
    ):
        assert name in {x["name"] for x in doc["jobs"]["validate"]["steps"]}
    assert "RLL_AUTHORITY_MODE: reviewed_ci_workflow" in raw
    assert 'RX_NETWORK_PROBE: "0"' in raw
    assert "agent/*|work/*)" in raw
    assert "main|rll/release)" not in raw
    assert "git push" in raw
    assert "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9" in raw


def test_legacy_lab_visual_validation_is_retained_independently() -> None:
    raw=LEGACY.read_text(encoding="utf-8")
    doc=yaml.safe_load(raw)
    assert "legacy" in str(doc["name"]).lower()
    names={x["name"] for x in doc["jobs"]["validate"]["steps"]}
    for name in (
        "Fetch/materialize declared data anchors with explicit fallback boundary",
        "Check fallback provenance boundary",
        "Compute validation (chi2 / AIC / BIC / falsifiability)",
        "Generate figures",
        "Render documentation from artifacts",
        "Upload artifacts",
    ):
        assert name in names
    assert "pip install pyyaml matplotlib" in raw
    assert "agent/*|work/*)" in raw
    assert "git push" in raw
    assert "main|rll/release)" not in raw
    assert "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9" in raw
    assert "commit-results" in doc["jobs"]


def test_branch_write_authority_is_explicit_on_both_routes() -> None:
    for path in (CANON,LEGACY):
        src=path.read_text(encoding="utf-8")
        assert "case \"${GITHUB_REF_NAME}\" in" in src
        assert "agent/*|work/*)" in src
        assert "exit 1" in src
        assert "if: ${{ " in src


def test_dual_source_files_cannot_replace_each_other() -> None:
    for name in ("fetch_real_data.py","compute_validation.py","make_figures.py","render_report.py"):
        canonical=(ROOT/"validacao_real"/name)
        legacy=(ROOT/"validacao_real"/("legacy_"+name))
        assert canonical.is_file() and legacy.is_file(), name
        assert canonical.read_bytes()!=legacy.read_bytes(), name
    for script in ("fetch_real_data.py","compute_validation.py","make_figures.py"):
        assert "import yaml" not in (ROOT/"validacao_real"/script).read_text(encoding="utf-8")
    assert "import matplotlib" not in (ROOT/"validacao_real/make_figures.py").read_text(encoding="utf-8")
    figures=(ROOT/"validacao_real/legacy_make_figures.py").read_text(encoding="utf-8")
    assert 'HERE / "legacy_compute_validation.py"' in figures
    legacy=LEGACY.read_text(encoding="utf-8")
    for name in ("fetch_real_data.py","compute_validation.py","make_figures.py","render_report.py"):
        assert "python3 legacy_"+name in legacy, name
    assert "github.ref" not in legacy or "workflow_dispatch" in legacy


def test_plot_generator_preserves_png_legacy_and_rx_svg_stdlib() -> None:
    canonical=(ROOT/"scripts/generate_rll_plots.py").read_text(encoding="utf-8")
    legacy=(ROOT/"scripts/legacy_generate_rll_plots.py").read_text(encoding="utf-8")
    assert "from rx import read_csv" in canonical
    assert "import pandas" not in canonical
    assert "import matplotlib" not in canonical
    assert "import pandas as pd" in legacy
    assert "import matplotlib.pyplot as plt" in legacy
    assert "Hz_curve.svg" in canonical and "Hz_curve.png" in legacy


def test_rx_http_data_stdlib_surfaces_preserve_lab_legacy_variants() -> None:
    for name in (
        "import_data.py",
        "fetch_real_sources.py",
        "fetch_public_astronomy_catalog_samples.py",
        "calc_data.py",
    ):
        modern=(ROOT/"scripts"/name)
        legacy=(ROOT/"scripts"/("legacy_"+name))
        assert modern.is_file() and legacy.is_file()
        assert modern.read_bytes()!=legacy.read_bytes(), name
    assert "import pandas" not in (ROOT/"scripts/import_data.py").read_text(encoding="utf-8")
    assert "import requests" not in (ROOT/"scripts/fetch_real_sources.py").read_text(encoding="utf-8")
    assert "import requests" not in (ROOT/"scripts/fetch_public_astronomy_catalog_samples.py").read_text(encoding="utf-8")
    assert "import numpy" not in (ROOT/"scripts/calc_data.py").read_text(encoding="utf-8")
