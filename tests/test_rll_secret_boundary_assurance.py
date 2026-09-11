from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "rll_secret_boundary_assurance.py"
SPEC = importlib.util.spec_from_file_location("rll_secret_boundary_assurance", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _jwt(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return f"header.{encoded}.signature"


def test_jwt_metadata_exposes_expiry_not_identity() -> None:
    token = _jwt({"sub": "SECRET-SUBJECT", "user_id": "SECRET-USER", "jti": "SECRET-JTI", "exp": 2000})
    metadata = MODULE.jwt_metadata(token, now=1000)
    serialized = json.dumps(metadata)
    assert metadata["expiry_observed"] is True
    assert metadata["remaining_seconds"] == 1000
    assert "SECRET-SUBJECT" not in serialized
    assert "SECRET-USER" not in serialized
    assert "SECRET-JTI" not in serialized


def test_classic_scope_observation_detects_delete_repo() -> None:
    absent = MODULE.github_scope_observation("repo, workflow")
    present = MODULE.github_scope_observation("repo, delete_repo, workflow")
    unknown = MODULE.github_scope_observation(None)
    assert absent["delete_repo_scope"] == "OBSERVED_ABSENT"
    assert present["delete_repo_scope"] == "OBSERVED_PRESENT"
    assert unknown["delete_repo_scope"] == "TOKEN_VAZIO"


def test_receipt_never_contains_secret_or_secret_hash(monkeypatch) -> None:
    secret = "github_pat_SUPER_SECRET_MATERIAL"
    monkeypatch.setenv("RLL_GITHUB_PAT", secret)
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(
        MODULE,
        "github_probe",
        lambda token, repository: {
            "secret_present": True,
            "token_kind": MODULE.token_kind(token),
            "http_status": 200,
            "authentication": "PASS_AUTHENTICATED_READ",
            "token_expiration_header": "TOKEN_VAZIO",
            **MODULE.github_scope_observation(None),
            "deletion_probe_performed": False,
        },
    )
    receipt = MODULE.github_receipt()
    serialized = json.dumps(receipt, sort_keys=True)
    assert secret not in serialized
    assert receipt["secret_material_persisted"] is False
    assert receipt["secret_hash_persisted"] is False
