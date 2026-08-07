"""[COD] Loader Pantheon+SH0ES com custódia de caminho explícita.

A presença de um caminho no catálogo não implica a presença dos bytes. O loader
resolve apenas arquivos realmente existentes e falha com diagnóstico enumerado.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

REQUIRED_COLUMNS = ("zHD", "MU_SH0ES", "MU_SH0ES_ERR_DIAG", "IS_CALIBRATOR")


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def candidate_paths(explicit_path: str | os.PathLike[str] | None = None) -> list[Path]:
    root = repository_root()
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(Path(explicit_path).expanduser())
    env_path = os.environ.get("RLL_PANTHEON_PATH")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(
        [
            root / "data/real/cosmology/pantheon_plus/Pantheon+SH0ES.dat",
            root / "data/real/cosmology/pantheon_plus/pantheon_data.dat",
            Path("/home/claude/rll_pantheon/pantheon_data.dat"),
        ]
    )
    unique: list[Path] = []
    seen: set[str] = set()
    for item in candidates:
        normalized = item.resolve(strict=False)
        key = str(normalized)
        if key not in seen:
            seen.add(key)
            unique.append(normalized)
    return unique


def resolve_pantheon_path(explicit_path: str | os.PathLike[str] | None = None) -> Path:
    candidates = candidate_paths(explicit_path)
    for path in candidates:
        if path.is_file():
            return path
    rendered = "\n".join(f"- {path}" for path in candidates)
    raise FileNotFoundError(
        "TOKEN_VAZIO_SOURCE_BYTES: nenhum arquivo Pantheon materializado foi encontrado.\n"
        f"Candidatos verificados:\n{rendered}"
    )


def _header_index(path: Path) -> dict[str, int]:
    with path.open("r", encoding="utf-8") as handle:
        header = handle.readline().split()
    missing = [name for name in REQUIRED_COLUMNS if name not in header]
    if missing:
        raise ValueError(f"BLOCKED_SCHEMA: colunas ausentes em {path}: {missing}")
    return {name: header.index(name) for name in REQUIRED_COLUMNS}


def load_pantheon(path: str | os.PathLike[str] | None = None) -> dict[str, np.ndarray | int | str]:
    resolved = resolve_pantheon_path(path)
    idx = _header_index(resolved)
    data = np.genfromtxt(resolved, skip_header=1, dtype=str)
    if data.ndim != 2 or data.shape[0] == 0:
        raise ValueError(f"BLOCKED_DATA: tabela Pantheon vazia ou inválida: {resolved}")

    z_hd = data[:, idx["zHD"]].astype(float)
    mu = data[:, idx["MU_SH0ES"]].astype(float)
    mu_err = data[:, idx["MU_SH0ES_ERR_DIAG"]].astype(float)
    is_calib = data[:, idx["IS_CALIBRATOR"]].astype(float)

    if not np.all(np.isfinite(z_hd)) or not np.all(np.isfinite(mu)):
        raise ValueError("BLOCKED_NONFINITE: zHD/MU_SH0ES contém NaN ou Inf")
    if not np.all(np.isfinite(mu_err)) or np.any(mu_err <= 0):
        raise ValueError("BLOCKED_UNCERTAINTY: MU_SH0ES_ERR_DIAG deve ser finito e positivo")
    if not np.all(np.isin(is_calib, [0.0, 1.0])):
        raise ValueError("BLOCKED_CALIBRATOR_DOMAIN: IS_CALIBRATOR deve pertencer a {0,1}")

    mask_cosmo = is_calib == 0
    return {
        "source_path": str(resolved),
        "z_all": z_hd,
        "mu_all": mu,
        "mu_err_all": mu_err,
        "is_calib": is_calib,
        "z": z_hd[mask_cosmo],
        "mu": mu[mask_cosmo],
        "mu_err": mu_err[mask_cosmo],
        "n_total": len(z_hd),
        "n_cosmo": int(mask_cosmo.sum()),
        "n_calib": int((~mask_cosmo).sum()),
    }


if __name__ == "__main__":
    dataset = load_pantheon()
    print(f"source={dataset['source_path']}")
    print(
        f"F_ok: total={dataset['n_total']} cosmo={dataset['n_cosmo']} "
        f"calibradores_excluidos={dataset['n_calib']}"
    )
    z = dataset["z"]
    mu = dataset["mu"]
    print(f"z range: [{z.min():.5f}, {z.max():.5f}]")
    print(f"mu range: [{mu.min():.3f}, {mu.max():.3f}]")
