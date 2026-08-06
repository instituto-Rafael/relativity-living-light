#!/data/data/com.termux/files/usr/bin/sh
set -eu

usage() {
  echo "uso: $0 PANTHEON_ZIP BAYES_ZIP [OUT_DIR]" >&2
  exit 64
}

[ "$#" -ge 2 ] || usage
PANTHEON_ZIP=$1
BAYES_ZIP=$2
OUT_DIR=${3:-artifacts/termux/rll-evidence-replay-v1}

[ -f "$PANTHEON_ZIP" ] || { echo "TOKEN_VAZIO_SOURCE: $PANTHEON_ZIP" >&2; exit 2; }
[ -f "$BAYES_ZIP" ] || { echo "TOKEN_VAZIO_SOURCE: $BAYES_ZIP" >&2; exit 2; }
command -v python >/dev/null 2>&1 || { echo "BLOCKED_RUNTIME: python ausente" >&2; exit 3; }
command -v sha256sum >/dev/null 2>&1 || { echo "BLOCKED_RUNTIME: sha256sum ausente" >&2; exit 3; }

mkdir -p "$OUT_DIR"
STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
COMMON_ARGS="--run-id 31066012098 --source-head-sha 3191a1d289db28b09b155b4b9eba62a32ad90005 --result-commit cfcd8b4915fef664486bc0d93ee2a2bb6d84ec65 --pantheon-sha256 c7b192cfa624dde19d5628781e120ba60d8628c792f3d7037e43c1092094f7e6 --bayes-sha256 6f5e11105d8cdd23586bd9b36238f705bf198f01f8dd662b34ea51cd29127078 --generated-at $STAMP"

# shellcheck disable=SC2086
python tools/rll_evidence_reconcile.py $COMMON_ARGS \
  --pantheon-zip "$PANTHEON_ZIP" --bayes-zip "$BAYES_ZIP" \
  --output "$OUT_DIR/replay-1.json"
# shellcheck disable=SC2086
python tools/rll_evidence_reconcile.py $COMMON_ARGS \
  --pantheon-zip "$PANTHEON_ZIP" --bayes-zip "$BAYES_ZIP" \
  --output "$OUT_DIR/replay-2.json"

H1=$(sha256sum "$OUT_DIR/replay-1.json" | awk '{print $1}')
H2=$(sha256sum "$OUT_DIR/replay-2.json" | awk '{print $1}')
[ "$H1" = "$H2" ] || { echo "BLOCKED_NONDETERMINISTIC: $H1 != $H2" >&2; exit 4; }

UNAME=$(uname -a 2>/dev/null || echo TOKEN_VAZIO_UNAME)
ANDROID=$(getprop ro.build.version.release 2>/dev/null || true)
MODEL=$(getprop ro.product.model 2>/dev/null || true)
PYVER=$(python --version 2>&1)
PANTHEON_SHA=$(sha256sum "$PANTHEON_ZIP" | awk '{print $1}')
BAYES_SHA=$(sha256sum "$BAYES_ZIP" | awk '{print $1}')

RLL_STAMP=$STAMP RLL_UNAME=$UNAME RLL_ANDROID=$ANDROID RLL_MODEL=$MODEL \
RLL_PYVER=$PYVER RLL_PANTHEON_SHA=$PANTHEON_SHA RLL_BAYES_SHA=$BAYES_SHA \
RLL_OUTPUT_SHA=$H1 python - "$OUT_DIR/TERMUX_RECEIPT.json" <<'PY'
import json, os, sys
from pathlib import Path
out = Path(sys.argv[1])
payload = {
    "schema": "rll.termux_receipt.v1",
    "timestamp_utc": os.environ["RLL_STAMP"],
    "execution_class": "E",
    "runtime": {
        "uname": os.environ["RLL_UNAME"],
        "android_release": os.environ["RLL_ANDROID"] or None,
        "device_model": os.environ["RLL_MODEL"] or None,
        "python": os.environ["RLL_PYVER"],
    },
    "inputs": {
        "pantheon_zip_sha256": os.environ["RLL_PANTHEON_SHA"],
        "bayes_zip_sha256": os.environ["RLL_BAYES_SHA"],
    },
    "output": {
        "replay_sha256": os.environ["RLL_OUTPUT_SHA"],
        "repeat_byte_identical": True,
    },
    "claim_allowed": False,
}
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
PY
sha256sum "$OUT_DIR/TERMUX_RECEIPT.json" "$OUT_DIR/replay-1.json" > "$OUT_DIR/CHECKSUMS.sha256"
echo "PASS_PHYSICAL_REPLAY_PENDING_CUSTODY: $OUT_DIR"
