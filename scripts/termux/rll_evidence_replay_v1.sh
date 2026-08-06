#!/data/data/com.termux/files/usr/bin/sh
set -eu

EXPECTED_PANTHEON_SHA=c7b192cfa624dde19d5628781e120ba60d8628c792f3d7037e43c1092094f7e6
EXPECTED_BAYES_SHA=6f5e11105d8cdd23586bd9b36238f705bf198f01f8dd662b34ea51cd29127078
CANONICAL_RUN_ID=31066012098
SOURCE_HEAD_SHA=3191a1d289db28b09b155b4b9eba62a32ad90005
RESULT_COMMIT=cfcd8b4915fef664486bc0d93ee2a2bb6d84ec65

usage() {
  echo "uso: $0 PANTHEON_ZIP BAYES_ZIP [OUT_DIR]" >&2
  exit 64
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "BLOCKED_RUNTIME: comando ausente: $1" >&2
    exit 3
  }
}

[ "$#" -ge 2 ] || usage
PANTHEON_ZIP=$1
BAYES_ZIP=$2
OUT_DIR=${3:-artifacts/termux/rll-evidence-replay-v1}

[ -f "$PANTHEON_ZIP" ] || {
  echo "TOKEN_VAZIO_SOURCE: $PANTHEON_ZIP" >&2
  exit 2
}
[ -f "$BAYES_ZIP" ] || {
  echo "TOKEN_VAZIO_SOURCE: $BAYES_ZIP" >&2
  exit 2
}

for cmd in python sha256sum git uname getprop awk date; do
  require_command "$cmd"
done

PANTHEON_SHA=$(sha256sum "$PANTHEON_ZIP" | awk '{print $1}')
BAYES_SHA=$(sha256sum "$BAYES_ZIP" | awk '{print $1}')
[ "$PANTHEON_SHA" = "$EXPECTED_PANTHEON_SHA" ] || {
  echo "BLOCKED_INPUT_SHA: pantheon $PANTHEON_SHA != $EXPECTED_PANTHEON_SHA" >&2
  exit 5
}
[ "$BAYES_SHA" = "$EXPECTED_BAYES_SHA" ] || {
  echo "BLOCKED_INPUT_SHA: bayes $BAYES_SHA != $EXPECTED_BAYES_SHA" >&2
  exit 5
}

CODE_COMMIT=$(git rev-parse HEAD 2>/dev/null || true)
case "$CODE_COMMIT" in
  [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]) ;;
  *)
    echo "BLOCKED_CODE_PROVENANCE: git HEAD inválido: $CODE_COMMIT" >&2
    exit 6
    ;;
esac

STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
UNAME=$(uname -a)
ANDROID=$(getprop ro.build.version.release 2>/dev/null || true)
MODEL=$(getprop ro.product.model 2>/dev/null || true)
PYVER=$(python --version 2>&1)
[ -n "$ANDROID" ] || {
  echo "BLOCKED_PHYSICAL_IDENTITY: Android release vazio" >&2
  exit 7
}
[ -n "$MODEL" ] || {
  echo "BLOCKED_PHYSICAL_IDENTITY: device model vazio" >&2
  exit 7
}

mkdir -p "$OUT_DIR"
rm -f \
  "$OUT_DIR/replay-1.json" \
  "$OUT_DIR/replay-2.json" \
  "$OUT_DIR/TERMUX_RECEIPT.json" \
  "$OUT_DIR/CHECKSUMS.sha256" \
  "$OUT_DIR/RUN.log"

{
  echo "timestamp_utc=$STAMP"
  echo "code_commit=$CODE_COMMIT"
  echo "uname=$UNAME"
  echo "android_release=$ANDROID"
  echo "device_model=$MODEL"
  echo "python=$PYVER"
  echo "pantheon_sha256=$PANTHEON_SHA"
  echo "bayes_sha256=$BAYES_SHA"

  python tools/rll_evidence_reconcile.py \
    --run-id "$CANONICAL_RUN_ID" \
    --source-head-sha "$SOURCE_HEAD_SHA" \
    --result-commit "$RESULT_COMMIT" \
    --pantheon-sha256 "$EXPECTED_PANTHEON_SHA" \
    --bayes-sha256 "$EXPECTED_BAYES_SHA" \
    --generated-at "$STAMP" \
    --pantheon-zip "$PANTHEON_ZIP" \
    --bayes-zip "$BAYES_ZIP" \
    --output "$OUT_DIR/replay-1.json"

  python tools/rll_evidence_reconcile.py \
    --run-id "$CANONICAL_RUN_ID" \
    --source-head-sha "$SOURCE_HEAD_SHA" \
    --result-commit "$RESULT_COMMIT" \
    --pantheon-sha256 "$EXPECTED_PANTHEON_SHA" \
    --bayes-sha256 "$EXPECTED_BAYES_SHA" \
    --generated-at "$STAMP" \
    --pantheon-zip "$PANTHEON_ZIP" \
    --bayes-zip "$BAYES_ZIP" \
    --output "$OUT_DIR/replay-2.json"
} > "$OUT_DIR/RUN.log" 2>&1

H1=$(sha256sum "$OUT_DIR/replay-1.json" | awk '{print $1}')
H2=$(sha256sum "$OUT_DIR/replay-2.json" | awk '{print $1}')
[ "$H1" = "$H2" ] || {
  echo "BLOCKED_NONDETERMINISTIC: $H1 != $H2" >&2
  exit 4
}
RUN_LOG_SHA=$(sha256sum "$OUT_DIR/RUN.log" | awk '{print $1}')
PANTHEON_SIZE=$(wc -c < "$PANTHEON_ZIP" | awk '{print $1}')
BAYES_SIZE=$(wc -c < "$BAYES_ZIP" | awk '{print $1}')

RLL_STAMP=$STAMP \
RLL_UNAME=$UNAME \
RLL_ANDROID=$ANDROID \
RLL_MODEL=$MODEL \
RLL_PYVER=$PYVER \
RLL_CODE_COMMIT=$CODE_COMMIT \
RLL_PANTHEON_SHA=$PANTHEON_SHA \
RLL_BAYES_SHA=$BAYES_SHA \
RLL_PANTHEON_SIZE=$PANTHEON_SIZE \
RLL_BAYES_SIZE=$BAYES_SIZE \
RLL_OUTPUT_SHA=$H1 \
RLL_RUN_LOG_SHA=$RUN_LOG_SHA \
python - "$OUT_DIR/TERMUX_RECEIPT.json" <<'PY'
import json
import os
import sys
from pathlib import Path

out = Path(sys.argv[1])
payload = {
    "schema": "rll.termux_physical_replay_receipt.v1",
    "generated_at": os.environ["RLL_STAMP"],
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
    "git": {
        "code_commit": os.environ["RLL_CODE_COMMIT"],
    },
    "runtime": {
        "uname": os.environ["RLL_UNAME"],
        "android_release": os.environ["RLL_ANDROID"],
        "device_model": os.environ["RLL_MODEL"],
        "python": os.environ["RLL_PYVER"],
    },
    "inputs": {
        "pantheon_zip_sha256": os.environ["RLL_PANTHEON_SHA"],
        "pantheon_zip_size_bytes": int(os.environ["RLL_PANTHEON_SIZE"]),
        "bayes_zip_sha256": os.environ["RLL_BAYES_SHA"],
        "bayes_zip_size_bytes": int(os.environ["RLL_BAYES_SIZE"]),
    },
    "output": {
        "replay_sha256": os.environ["RLL_OUTPUT_SHA"],
        "repeat_byte_identical": True,
        "run_log_sha256": os.environ["RLL_RUN_LOG_SHA"],
    },
    "claim_allowed": False,
}
out.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

(
  cd "$OUT_DIR"
  sha256sum TERMUX_RECEIPT.json replay-1.json replay-2.json RUN.log > CHECKSUMS.sha256
)

python tools/validate_rll_termux_physical_replay.py "$OUT_DIR"
echo "PASS_PHYSICAL_TERMUX_REPLAY: $OUT_DIR"
