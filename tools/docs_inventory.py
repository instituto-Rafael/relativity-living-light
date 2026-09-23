#!/usr/bin/env python3
"""Generate and validate the repository documentation/source inventory.

This tool is intentionally CI-friendly: ``--check`` reports every inventory
contract violation it can find and exits once with a non-zero status, instead of
raising a traceback on the first malformed/missing field.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TABLE_SEPARATOR = "|---|---:|---|---|---:|---|---|"
SUMMARY_SEPARATOR = "|---|---:|"
DEFAULT_OUTPUTS = {
    "markdown_inventory": "docs/DOCUMENTATION_FULL_INVENTORY.md",
    "real_numbers_report": "docs/REAL_NUMBERS_REPORT.md",
    "yml_index": "docs/YML_WORKFLOWS_INDEX.md",
    "json_inventory": "data/results/repo_inventory.json",
    "tsv_inventory": "data/results/repo_inventory.tsv",
    "machine_summary": "data/results/repo_inventory_summary.json",
}
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "data/raw",
    "data/cache",
}
DEFAULT_TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".sh",
    ".yml",
    ".yaml",
    ".json",
    ".csv",
    ".tsv",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".rs",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".toml",
    ".ini",
    ".cfg",
}
REAL_DATA_MARKERS = ("data/results", "data/processed", "scripts", "tests", "docs")


@dataclass(frozen=True)
class InventoryConfig:
    outputs: dict[str, str]
    exclude_dirs: set[str]
    text_extensions: set[str]
    real_data_markers: tuple[str, ...]


@dataclass(frozen=True)
class InventoryItem:
    path: str
    bytes: int
    ext: str
    tipo: str
    linhas: int
    sha256: str
    flags: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "bytes": self.bytes,
            "ext": self.ext,
            "tipo": self.tipo,
            "linhas": self.linhas,
            "sha256": self.sha256,
            "flags": self.flags,
        }


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def load_config(root: Path) -> InventoryConfig:
    config_path = root / "tools" / "inventory_config.json"
    data: dict[str, Any] = {}
    if config_path.exists():
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded

    outputs = dict(DEFAULT_OUTPUTS)
    outputs.update({k: str(v) for k, v in (data.get("outputs") or {}).items() if v})
    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
    exclude_dirs.update(str(v).strip("/") for v in (data.get("exclude_dirs") or []) if v)
    text_extensions = set(DEFAULT_TEXT_EXTENSIONS)
    text_extensions.update(str(v).lower() for v in (data.get("text_extensions") or []) if v)
    markers = tuple(str(v).strip("/") for v in (data.get("real_data_markers") or REAL_DATA_MARKERS) if v)
    return InventoryConfig(outputs=outputs, exclude_dirs=exclude_dirs, text_extensions=text_extensions, real_data_markers=markers)


def git_tracked_files(root: Path) -> list[str]:
    try:
        raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=root, stderr=subprocess.DEVNULL)
        return [p.decode("utf-8", errors="surrogateescape") for p in raw.split(b"\0") if p]
    except Exception:  # noqa: BLE001 - fallback for exported source trees.
        files: list[str] = []
        for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
            if path.is_file() and ".git" not in path.parts:
                files.append(rel_posix(path, root))
        return files


def is_excluded(path: str, config: InventoryConfig) -> bool:
    if path in set(config.outputs.values()):
        return True
    parts = path.split("/")
    prefixes = {"/".join(parts[:idx]) for idx in range(1, len(parts) + 1)}
    return any(excluded in parts or excluded in prefixes for excluded in config.exclude_dirs)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(b"SYMLINK\0")
        digest.update(os.readlink(path).encode("utf-8", errors="surrogateescape"))
        return digest.hexdigest()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_text_lines(data: bytes) -> int:
    if not data:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def read_text_for_flags(path: Path, ext: str, config: InventoryConfig) -> tuple[int, str]:
    if path.is_symlink() or ext not in config.text_extensions:
        return 0, ""
    try:
        data = path.read_bytes()
    except OSError:
        return 0, ""
    text = data[:256 * 1024].decode("utf-8", errors="replace").lower()
    return count_text_lines(data), text


def classify(path: str, ext: str) -> str:
    if path.startswith(".github/workflows/") and ext in {".yml", ".yaml"}:
        return "github_workflow_yml"
    if ext in {".yml", ".yaml", ".toml", ".ini", ".cfg"}:
        return "config_yml" if ext in {".yml", ".yaml"} else "config"
    if ext == ".md":
        return "documentation_md"
    if ext in {".py", ".sh", ".c", ".h", ".cpp", ".hpp", ".rs", ".js", ".ts", ".tsx", ".jsx"}:
        return "source_code"
    if ext in {".csv", ".tsv", ".json"} or path.startswith(("results/", "data/results/", "data/real/")):
        return "data_or_result"
    return "other"


def detect_flags(path: str, text: str, markers: tuple[str, ...], extra_flags: list[str] | None = None) -> str:
    flags: list[str] = list(extra_flags or [])
    if "synthetic" in text or "sintético" in text or "sintetico" in text:
        flags.append("mentions_synthetic")
    if "mock" in text or "placeholder" in text:
        flags.append("mentions_mock_or_placeholder")
    if "token_vazio" in text:
        flags.append("token_vazio_declared")
    if any(path == marker or path.startswith(f"{marker}/") for marker in markers):
        flags.append("cosmology_validation_marker")
    return ",".join(dict.fromkeys(flags))


def collect_inventory(root: Path, config: InventoryConfig) -> tuple[list[InventoryItem], list[dict[str, str]], int]:
    tracked = git_tracked_files(root)
    items: list[InventoryItem] = []
    errors: list[dict[str, str]] = []

    for rel in sorted(tracked):
        if is_excluded(rel, config):
            continue
        path = root / rel
        try:
            stat = path.lstat()
            ext = path.suffix.lower() or "NO_EXT"
            lines, text = read_text_for_flags(path, ext, config)
            extra_flags: list[str] = []
            if path.is_symlink():
                extra_flags.append("symlink")
                if not path.exists():
                    extra_flags.append("broken_symlink")
            items.append(
                InventoryItem(
                    path=rel,
                    bytes=stat.st_size,
                    ext=ext,
                    tipo=classify(rel, ext),
                    linhas=lines,
                    sha256=sha256_file(path),
                    flags=detect_flags(rel, text, config.real_data_markers, extra_flags),
                )
            )
        except Exception as exc:  # noqa: BLE001 - collect all custody gaps.
            errors.append({"path": rel, "error": repr(exc)})
    return items, errors, len(tracked)


def build_summary(items: list[InventoryItem], errors: list[dict[str, str]], tracked_total: int) -> dict[str, int]:
    return {
        "tracked_files_total": tracked_total,
        "cataloged_files": len(items),
        "uncataloged_or_error_files": len(errors),
        "total_bytes": sum(item.bytes for item in items),
        "total_text_lines": sum(item.linhas for item in items),
        "markdown_files": sum(1 for item in items if item.ext == ".md"),
        "yml_yaml_files": sum(1 for item in items if item.ext in {".yml", ".yaml"}),
        "github_workflow_yml_files": sum(1 for item in items if item.tipo == "github_workflow_yml"),
        "data_or_result_files": sum(1 for item in items if item.tipo == "data_or_result"),
    }


def inventory_contract_lines() -> list[str]:
    return [
        "Gerado por: `tools/docs_inventory.py`",
        "Base: arquivos rastreados por `git ls-files`; campos voláteis de data/hora e commit não são materializados para reduzir conflitos entre branches.",
    ]


def render_markdown_inventory(root: Path, items: list[InventoryItem], errors: list[dict[str, str]], summary: dict[str, int]) -> str:
    lines = [
        "# Documentation Full Inventory",
        "",
        *inventory_contract_lines(),
        "",
        "## Resumo",
        "",
        "| Métrica | Valor |",
        SUMMARY_SEPARATOR,
    ]
    for key, value in summary.items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            f"**Total de arquivos catalogados:** {summary['cataloged_files']}",
            "",
            "## Inventário completo",
            "",
            "| Path | Bytes | Ext | Tipo | Linhas | SHA256 | Flags |",
            TABLE_SEPARATOR,
        ]
    )
    for item in items:
        escaped_path = item.path.replace("|", "\\|").replace("`", "'")
        lines.append(
            f"| `{escaped_path}` | {item.bytes} | `{item.ext}` | `{item.tipo}` | {item.linhas} | `{item.sha256}` | `{item.flags}` |"
        )
    lines.extend(["", "## Arquivos com erro/lacuna", ""])
    if errors:
        for error in errors:
            lines.append(f"- `{error['path']}`: `{error['error']}`")
    else:
        lines.append("- Nenhum erro de leitura encontrado na varredura rastreada pelo Git.")
    lines.append("")
    return "\n".join(lines)


def render_real_numbers(summary: dict[str, int], errors: list[dict[str, str]]) -> str:
    lines = ["# Real Numbers Report", "", *inventory_contract_lines(), "", "| Métrica | Valor |", SUMMARY_SEPARATOR]
    for key, value in summary.items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Contrato operacional",
            "",
            "tracked_files_total é a contagem bruta de `git ls-files`. cataloged_files é o que foi lido, medido e hasheado. uncataloged_or_error_files mostra a lacuna real.",
            "",
            "## Lacunas",
            "",
        ]
    )
    if errors:
        lines.extend(f"- `{error['path']}`: `{error['error']}`" for error in errors)
    else:
        lines.append("- Nenhuma lacuna de leitura encontrada.")
    lines.append("")
    return "\n".join(lines)


def render_yml_index(items: list[InventoryItem]) -> str:
    yml_items = [item for item in items if item.ext in {".yml", ".yaml"}]
    lines = [
        "# YML Workflows and Config Index",
        "",
        *inventory_contract_lines(),
        "",
        "| Path | Tipo | Bytes | Linhas | SHA256 |",
        "|---|---|---:|---:|---|",
    ]
    for item in yml_items:
        lines.append(f"| `{item.path}` | `{item.tipo}` | {item.bytes} | {item.linhas} | `{item.sha256}` |")
    lines.append("")
    return "\n".join(lines)


def write_outputs(root: Path, config: InventoryConfig, items: list[InventoryItem], errors: list[dict[str, str]], summary: dict[str, int]) -> None:
    payloads = {
        "markdown_inventory": render_markdown_inventory(root, items, errors, summary),
        "real_numbers_report": render_real_numbers(summary, errors),
        "yml_index": render_yml_index(items),
    }
    for key, content in payloads.items():
        path = root / config.outputs[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    json_path = root / config.outputs["json_inventory"]
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps([item.as_dict() for item in items], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary_path = root / config.outputs["machine_summary"]
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tsv_path = root / config.outputs["tsv_inventory"]
    tsv_path.parent.mkdir(parents=True, exist_ok=True)
    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = list(InventoryItem("", 0, "", "", 0, "", "").as_dict())
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for item in items:
            row = item.as_dict()
            row["flags"] = row["flags"] or "-"
            writer.writerow(row)


def parse_markdown_summary(path: Path) -> dict[str, int]:
    summary: dict[str, int] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw.startswith("| `"):
            continue
        parts = [part.strip() for part in raw.strip("|").split("|")]
        if len(parts) < 2:
            continue
        key = parts[0].strip("`")
        value = parts[1]
        if value.isdigit():
            summary[key] = int(value)
    return summary


def run_check(root: Path, config: InventoryConfig) -> int:
    items, errors, tracked_total = collect_inventory(root, config)
    expected_summary = build_summary(items, errors, tracked_total)
    check_errors: list[str] = []

    for key, rel in config.outputs.items():
        path = root / rel
        if not path.exists():
            check_errors.append(f"output ausente: {rel}")
            continue
        if key == "markdown_inventory":
            text = path.read_text(encoding="utf-8", errors="replace")
            if TABLE_SEPARATOR not in text:
                check_errors.append(f"{rel}: separador da tabela principal ausente ou desalinhado")
            published = parse_markdown_summary(path)
            for metric, expected in expected_summary.items():
                got = published.get(metric)
                if got != expected:
                    check_errors.append(f"{rel}: métrica {metric} divergente -> publicada={got}, real={expected}")
        elif key == "machine_summary":
            try:
                published_json = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001 - collect all parse failures.
                check_errors.append(f"{rel}: JSON inválido: {exc}")
                continue
            for metric, expected in expected_summary.items():
                got = published_json.get(metric)
                if got != expected:
                    check_errors.append(f"{rel}: métrica {metric} divergente -> publicada={got}, real={expected}")

    if errors:
        print("WARN: lacunas rastreadas permanecem documentadas no inventário:")
        for error in errors:
            print(f"- {error['path']}: {error['error']}")

    if check_errors:
        print("Docs inventory check FAILED:")
        for error in check_errors:
            print(f"- {error}")
        print("Hotfix sugerido: execute `python3 tools/docs_inventory.py` e versione os artefatos gerados.")
        return 1

    print(
        "OK: inventário coerente "
        f"(tracked={expected_summary['tracked_files_total']}, cataloged={expected_summary['cataloged_files']}, "
        f"workflows={expected_summary['github_workflow_yml_files']})."
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=None,
        help="Compatibilidade: sobrescreve apenas o caminho do inventário Markdown principal.",
    )
    parser.add_argument("--check", action="store_true", help="Valida artefatos de inventário sem reescrever arquivos.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    config = load_config(root)
    if args.output:
        config.outputs["markdown_inventory"] = args.output

    if args.check:
        return run_check(root, config)

    items, errors, tracked_total = collect_inventory(root, config)
    summary = build_summary(items, errors, tracked_total)
    write_outputs(root, config, items, errors, summary)
    print(
        "Inventário atualizado: "
        f"{config.outputs['markdown_inventory']} ({summary['cataloged_files']} itens, "
        f"{summary['uncataloged_or_error_files']} lacunas)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
