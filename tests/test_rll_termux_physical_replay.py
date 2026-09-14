from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/validate_rll_termux_physical_replay.py"
EFFECTIVE_PATH = ROOT / "tools/rll_execution_queue_effective.py"
QUEUE_PATH = ROOT / "data/governance/RLL_EXECUTION_QUEUE_20260806_V1.json"
PRIOR_RECEIPT_PATH = ROOT / "results/governance/RLL_POSTMERGE_CI_RECEIPT_20260806_V1.json"
SCHEMA_PATH = ROOT / "schemas/rll_termux_physical_replay_receipt_v1.schema.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_module(VALIDATOR_PATH, "rll_termux_physical_replay")
effective = load_module(EFFECTIVE_PATH, "rll_execution_queue_effective_for_termux")


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_checksums(root: Path) -> None:
    names = ["TERMUX_RECEIPT.json", "replay-1.json", "replay-2.json", "RUN.log"]
    (root / "CHECKSUMS.sha256").write_text(
        "".join(f"{sha(root / name)}  {name}\n" for name in names),
        encoding="utf-8",
    )


def replay_payload() -> dict:
    return {
        "schema": "rll.evidence_reconciliation.v1",
        "generated_at": "2026-08-06T11:40:00Z",
        "repository": "instituto-Rafael/relativity-living-light",
        "canonical_run": {
            "run_id": 31066012098,
            "source_head_sha": "3191a1d289db28b09b155b4b9eba62a32ad90005",
            "result_commit": "cfcd8b4915fef664486bc0d93ee2a2bb6d84ec65",
        },
        "results": {},
        "closure": {"claim_allowed": False},
        "claim_allowed": False,
    }


def receipt_payload(replay_sha: str, log_sha: str) -> dict:
    return {
        "schema": "rll.termux_physical_replay_receipt.v1",
        "generated_at": "2026-08-06T11:40:00Z",
        "repository": "instituto-Rafael/relativity-living-light",
        "supersedes_queue_item": "RLL-P0-TERMUX-PHYSICAL-REPLAY",
        "evidence_class": "E",
        "state": "PASS_PHYSICAL_TERMUX_REPLAY",
        "promotion": {
            "from": {
                "evidence_class": "P",
                "state": "TOKEN_VAZIO_PHYSICAL_EXECUTION",
            },
            "to": {
                "evidence_class": "E",
                "state": "PASS_PHYSICAL_TERMUX_REPLAY",
            },
        },
        "next_gate": "RLL-P0-PANTHEON-SUCCESSOR-RUN",
        "git": {"code_commit": "1" * 40},
        "runtime": {
            "uname": "Linux localhost 5.10 Android aarch64",
            "android_release": "14",
            "device_model": "physical-test-device",
            "python": "Python 3.12.11",
        },
        "inputs": {
            "pantheon_zip_sha256": validator.EXPECTED_PANTHEON_SHA,
            "pantheon_zip_size_bytes": 123,
            "bayes_zip_sha256": validator.EXPECTED_BAYES_SHA,
            "bayes_zip_size_bytes": 456,
        },
        "output": {
            "replay_sha256": replay_sha,
            "repeat_byte_identical": True,
            "run_log_sha256": log_sha,
        },
        "claim_allowed": False,
    }


def capsule(tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path / "capsule"
    root.mkdir()
    replay = replay_payload()
    dump_json(root / "replay-1.json", replay)
    dump_json(root / "replay-2.json", replay)
    (root / "RUN.log").write_text("physical replay test log\n", encoding="utf-8")
    receipt = receipt_payload(sha(root / "replay-1.json"), sha(root / "RUN.log"))
    dump_json(root / "TERMUX_RECEIPT.json", receipt)
    write_checksums(root)
    return root, receipt


def test_valid_physical_capsule_passes(tmp_path: Path) -> None:
    root, receipt = capsule(tmp_path)
    assert validator.validate_directory(root) == receipt


def test_schema_accepts_canonical_receipt(tmp_path: Path) -> None:
    _, receipt = capsule(tmp_path)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(receipt)


def test_changed_replay_is_blocked(tmp_path: Path) -> None:
    root, _ = capsule(tmp_path)
    (root / "replay-2.json").write_text("{}\n", encoding="utf-8")
    write_checksums(root)
    try:
        validator.validate_directory(root)
    except validator.PhysicalReplayError as exc:
        assert "not byte-identical" in str(exc)
    else:
        raise AssertionError("changed replay was accepted")


def test_wrong_input_hash_is_blocked(tmp_path: Path) -> None:
    root, receipt = capsule(tmp_path)
    changed = copy.deepcopy(receipt)
    changed["inputs"]["pantheon_zip_sha256"] = "0" * 64
    dump_json(root / "TERMUX_RECEIPT.json", changed)
    write_checksums(root)
    try:
        validator.validate_directory(root)
    except validator.PhysicalReplayError as exc:
        assert "Pantheon input SHA mismatch" in str(exc)
    else:
        raise AssertionError("wrong input hash was accepted")


def test_empty_device_identity_is_blocked(tmp_path: Path) -> None:
    root, receipt = capsule(tmp_path)
    changed = copy.deepcopy(receipt)
    changed["runtime"]["device_model"] = ""
    dump_json(root / "TERMUX_RECEIPT.json", changed)
    write_checksums(root)
    try:
        validator.validate_directory(root)
    except validator.PhysicalReplayError as exc:
        assert "device_model" in str(exc)
    else:
        raise AssertionError("empty device identity was accepted")


def test_claim_promotion_is_blocked(tmp_path: Path) -> None:
    root, receipt = capsule(tmp_path)
    changed = copy.deepcopy(receipt)
    changed["claim_allowed"] = True
    dump_json(root / "TERMUX_RECEIPT.json", changed)
    write_checksums(root)
    try:
        validator.validate_directory(root)
    except validator.PhysicalReplayError as exc:
        assert "claim_allowed" in str(exc)
    else:
        raise AssertionError("claim promotion was accepted")


def test_promotion_mismatch_is_blocked(tmp_path: Path) -> None:
    root, receipt = capsule(tmp_path)
    changed = copy.deepcopy(receipt)
    changed["promotion"]["from"]["state"] = "TOKEN_VAZIO_WRONG"
    dump_json(root / "TERMUX_RECEIPT.json", changed)
    write_checksums(root)
    try:
        validator.validate_directory(root)
    except validator.PhysicalReplayError as exc:
        assert "promotion boundary mismatch" in str(exc)
    else:
        raise AssertionError("promotion mismatch was accepted")


def test_checksum_tampering_is_blocked(tmp_path: Path) -> None:
    root, _ = capsule(tmp_path)
    text = (root / "CHECKSUMS.sha256").read_text(encoding="utf-8")
    (root / "CHECKSUMS.sha256").write_text(text.replace(text[:64], "0" * 64, 1), encoding="utf-8")
    try:
        validator.validate_directory(root)
    except validator.PhysicalReplayError as exc:
        assert "checksum mismatch" in str(exc)
    else:
        raise AssertionError("checksum tampering was accepted")


def test_receipt_advances_effective_queue_to_pantheon(tmp_path: Path) -> None:
    _, receipt = capsule(tmp_path)
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR_RECEIPT_PATH.read_text(encoding="utf-8"))
    compiled = effective.build_effective_queue(queue, [prior, receipt])
    resolved = {item["id"] for item in compiled["resolved"]}
    assert "RLL-P0-TERMUX-PHYSICAL-REPLAY" in resolved
    assert compiled["closure"]["F_next"] == "RLL-P0-PANTHEON-SUCCESSOR-RUN"
