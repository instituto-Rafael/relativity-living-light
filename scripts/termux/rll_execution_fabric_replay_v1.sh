#!/data/data/com.termux/files/usr/bin/sh
set -eu

PLAN="configs/rll_execution_plan.v1.yml"
OUT_DIR=${1:-artifacts/termux/rll-execution-fabric-v1}

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "BLOCKED_RUNTIME: comando ausente: $1" >&2
    exit 3
  }
}

for cmd in git sha256sum uname getprop awk date cmp cp mkdir rm; do
  require_command "$cmd"
done

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "BLOCKED_RUNTIME: python/python3 ausente" >&2
  exit 3
fi

[ -f "$PLAN" ] || {
  echo "TOKEN_VAZIO_PLAN: $PLAN" >&2
  exit 2
}

CODE_COMMIT=$(git rev-parse HEAD 2>/dev/null || true)
case "$CODE_COMMIT" in
  [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]) ;;
  *)
    echo "BLOCKED_CODE_PROVENANCE: git HEAD inválido: $CODE_COMMIT" >&2
    exit 6
    ;;
esac

if [ -n "$(git status --porcelain)" ]; then
  echo "BLOCKED_CODE_PROVENANCE: working tree precisa estar limpo" >&2
  exit 6
fi

ANDROID=$(getprop ro.build.version.release 2>/dev/null || true)
MODEL=$(getprop ro.product.model 2>/dev/null || true)
ABI=$(getprop ro.product.cpu.abi 2>/dev/null || true)
UNAME=$(uname -a)
PYVER=$($PY --version 2>&1)
STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

[ -n "$ANDROID" ] || { echo "BLOCKED_PHYSICAL_IDENTITY: Android release vazio" >&2; exit 7; }
[ -n "$MODEL" ] || { echo "BLOCKED_PHYSICAL_IDENTITY: device model vazio" >&2; exit 7; }
[ -n "$ABI" ] || { echo "BLOCKED_PHYSICAL_IDENTITY: ABI vazio" >&2; exit 7; }

RUN_ID=$($PY - "$PLAN" <<'PY'
import sys
from rx.yaml_subset import load
plan = load(sys.argv[1])
print(plan["run"]["id"])
PY
)
case "$RUN_ID" in
  *[!A-Za-z0-9._-]*|"")
    echo "BLOCKED_PLAN: run.id inválido: $RUN_ID" >&2
    exit 8
    ;;
esac

CANONICAL_DIR="results/rll-execution/$RUN_ID"
RUN1="$OUT_DIR/run1"
RUN2="$OUT_DIR/run2"

rm -rf "$OUT_DIR"
mkdir -p "$RUN1" "$RUN2"
cp "$PLAN" "$OUT_DIR/execution_plan_source.yml"

{
  echo "timestamp_utc=$STAMP"
  echo "code_commit=$CODE_COMMIT"
  echo "run_id=$RUN_ID"
  echo "uname=$UNAME"
  echo "android_release=$ANDROID"
  echo "device_model=$MODEL"
  echo "abi=$ABI"
  echo "python=$PYVER"

  RLL_AUTHORITY_MODE=explicit_local_command RX_NETWORK_PROBE=0 RLL_LEGACY_NETWORK_PROBE=0     "$PY" -m rx orchestrate --plan "$PLAN"
  [ -d "$CANONICAL_DIR" ] || { echo "BLOCKED_OUTPUT: $CANONICAL_DIR ausente"; exit 9; }
  cp -R "$CANONICAL_DIR"/. "$RUN1"/

  RLL_AUTHORITY_MODE=explicit_local_command RX_NETWORK_PROBE=0 RLL_LEGACY_NETWORK_PROBE=0     "$PY" -m rx orchestrate --plan "$PLAN"
  [ -d "$CANONICAL_DIR" ] || { echo "BLOCKED_OUTPUT: $CANONICAL_DIR ausente"; exit 9; }
  cp -R "$CANONICAL_DIR"/. "$RUN2"/
} > "$OUT_DIR/RUN.log" 2>&1

FILES="execution_plan.json region_classification.json selected_formulas.json rejected_formulas.json covariance_contract.json metrics.json negative_results.json manifest.json"
: > "$OUT_DIR/RUN1_DETERMINISTIC.sha256"
: > "$OUT_DIR/RUN2_DETERMINISTIC.sha256"
for name in $FILES; do
  [ -f "$RUN1/$name" ] || { echo "BLOCKED_OUTPUT: run1/$name ausente" >&2; exit 10; }
  [ -f "$RUN2/$name" ] || { echo "BLOCKED_OUTPUT: run2/$name ausente" >&2; exit 10; }
  h1=$(sha256sum "$RUN1/$name" | awk '{print $1}')
  h2=$(sha256sum "$RUN2/$name" | awk '{print $1}')
  echo "$h1  $name" >> "$OUT_DIR/RUN1_DETERMINISTIC.sha256"
  echo "$h2  $name" >> "$OUT_DIR/RUN2_DETERMINISTIC.sha256"
done

cmp "$OUT_DIR/RUN1_DETERMINISTIC.sha256" "$OUT_DIR/RUN2_DETERMINISTIC.sha256" >/dev/null || {
  echo "BLOCKED_NONDETERMINISTIC: deterministic artifact lists differ" >&2
  exit 11
}

PLAN_SHA=$(sha256sum "$OUT_DIR/execution_plan_source.yml" | awk '{print $1}')
RUN_LIST_SHA=$(sha256sum "$OUT_DIR/RUN1_DETERMINISTIC.sha256" | awk '{print $1}')
RUN_LOG_SHA=$(sha256sum "$OUT_DIR/RUN.log" | awk '{print $1}')

RLL_STAMP="$STAMP" RLL_CODE_COMMIT="$CODE_COMMIT" RLL_RUN_ID="$RUN_ID" RLL_UNAME="$UNAME" RLL_ANDROID="$ANDROID" RLL_MODEL="$MODEL" RLL_ABI="$ABI" RLL_PYVER="$PYVER" RLL_PLAN_SHA="$PLAN_SHA" RLL_RUN_LIST_SHA="$RUN_LIST_SHA" RLL_RUN_LOG_SHA="$RUN_LOG_SHA" "$PY" - "$RUN1/receipt.json" "$OUT_DIR/TERMUX_RECEIPT.json" <<'PY'
import json
import os
import sys
from pathlib import Path

rx_receipt = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
payload = {
    "schema": "rll.rx.termux_execution_fabric_receipt.v1",
    "generated_at": os.environ["RLL_STAMP"],
    "repository": "instituto-Rafael/relativity-living-light",
    "workstream": "WS16",
    "state": "PASS_PHYSICAL_RX_EXECUTION_FABRIC",
    "git": {"code_commit": os.environ["RLL_CODE_COMMIT"]},
    "runtime": {
        "uname": os.environ["RLL_UNAME"],
        "android_release": os.environ["RLL_ANDROID"],
        "device_model": os.environ["RLL_MODEL"],
        "abi": os.environ["RLL_ABI"],
        "python": os.environ["RLL_PYVER"],
    },
    "execution": {
        "run_id": os.environ["RLL_RUN_ID"],
        "physics_contract": rx_receipt["physics_contract"],
        "qualified_regimes": rx_receipt.get("qualified_regimes", []),
        "dispersion_operator": rx_receipt["dispersion_operator"],
        "formula_selection_basis": rx_receipt["formula_selection_basis"],
        "repeat_deterministic_artifacts_identical": True,
        "deterministic_manifest_sha256": os.environ["RLL_RUN_LIST_SHA"],
        "plan_sha256": os.environ["RLL_PLAN_SHA"],
        "run_log_sha256": os.environ["RLL_RUN_LOG_SHA"],
    },
    "actions_comparison_state": "TOKEN_VAZIO_PENDING_ACTIONS_RECEIPT_COMPARISON",
    "training": False,
    "ai_runtime": False,
    "claim_allowed": False,
    "boundary": "Physical execution evidence only; it does not validate the scientific model or promote a claim.",
}
Path(sys.argv[2]).write_text(
    json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

(
  cd "$OUT_DIR"
  sha256sum TERMUX_RECEIPT.json execution_plan_source.yml RUN.log     RUN1_DETERMINISTIC.sha256 RUN2_DETERMINISTIC.sha256 > CHECKSUMS.sha256
)

"$PY" tools/validate_rll_execution_fabric_termux_replay.py "$OUT_DIR"
echo "PASS_PHYSICAL_RX_EXECUTION_FABRIC: $OUT_DIR"
