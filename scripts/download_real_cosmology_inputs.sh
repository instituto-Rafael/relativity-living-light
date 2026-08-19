#!/usr/bin/env bash
set -euo pipefail

# RLL real-data materializer
# Policy: primary public source only; exact bytes; pinned provenance; fail closed.
# Usage:
#   bash scripts/download_real_cosmology_inputs.sh
#
# This script writes Pantheon+ into the SAME canonical directory consumed by
# scripts/verify_pantheon_inputs.py. Legacy data/pantheon paths are compatibility
# hardlinks/copies only and never the scientific authority.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANONICAL_PANTHEON_DIR="$ROOT_DIR/data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR"
LEGACY_PANTHEON_DIR="$ROOT_DIR/data/pantheon"
REAL_DIR="$ROOT_DIR/data/real"
mkdir -p "$CANONICAL_PANTHEON_DIR" "$LEGACY_PANTHEON_DIR" "$REAL_DIR"

PANTHEON_SOURCE_REPO="PantheonPlusSH0ES/DataRelease"
PANTHEON_SOURCE_COMMIT="c447f0fea703fcd0fff57de5000947b5ca81286b"
PANTHEON_DAT_GIT_BLOB="cce857db0c15e9ce7a0e0ce77452b6ff62af969a"
PANTHEON_COV_GIT_BLOB="d1a1498154e7ba826df14bdbef35ebcb7f5efba1"
PANTHEON_DAT_SHA256="1cb0fc379ef066afdc2ffd1857681cc478024570d8a3eba284fb645775198cf8"
PANTHEON_COV_SHA256="abf806d966485e64afdb359c87bffc0ecc00d05eff0a31ced66f247385df0fdc"
PANTHEON_DAT_BYTES=579283
PANTHEON_COV_BYTES=33284960

PANTHEON_DAT_URL="https://raw.githubusercontent.com/${PANTHEON_SOURCE_REPO}/${PANTHEON_SOURCE_COMMIT}/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES.dat"
PANTHEON_COV_URL="https://raw.githubusercontent.com/${PANTHEON_SOURCE_REPO}/${PANTHEON_SOURCE_COMMIT}/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES_STAT%2BSYS.cov"

fetch() {
  local url="$1"
  local out="$2"
  local tmp="${out}.part"
  rm -f "$tmp"
  echo "[rll-materialize] fetching $url"
  if command -v curl >/dev/null 2>&1; then
    curl -fL --retry 3 --retry-all-errors --connect-timeout 30 "$url" -o "$tmp"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$tmp" "$url"
  else
    echo "[rll-materialize] ERROR: curl or wget is required" >&2
    exit 2
  fi
  test -s "$tmp"
  mv "$tmp" "$out"
}

sha256_hex() {
  local path="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$path" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$path" | awk '{print $1}'
  else
    python3 - "$path" <<'PY'
import hashlib, pathlib, sys
p = pathlib.Path(sys.argv[1])
h = hashlib.sha256()
with p.open('rb') as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b''):
        h.update(chunk)
print(h.hexdigest())
PY
  fi
}

size_bytes() {
  local path="$1"
  if command -v stat >/dev/null 2>&1; then
    if stat -c %s "$path" >/dev/null 2>&1; then
      stat -c %s "$path"
      return
    fi
  fi
  python3 - "$path" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).stat().st_size)
PY
}

verify_exact() {
  local path="$1"
  local expected_sha="$2"
  local expected_bytes="$3"
  local label="$4"
  local actual_sha actual_bytes
  actual_sha="$(sha256_hex "$path")"
  actual_bytes="$(size_bytes "$path")"
  if [ "$actual_sha" != "$expected_sha" ]; then
    echo "[rll-materialize] BLOCKED_${label}_SHA256 expected=$expected_sha actual=$actual_sha" >&2
    exit 20
  fi
  if [ "$actual_bytes" != "$expected_bytes" ]; then
    echo "[rll-materialize] BLOCKED_${label}_SIZE expected=$expected_bytes actual=$actual_bytes" >&2
    exit 21
  fi
  printf '%s  %s\n' "$actual_sha" "$(basename "$path")" > "${path}.sha256"
}

compat_link_or_copy() {
  local source="$1"
  local destination="$2"
  rm -f "$destination"
  if ln "$source" "$destination" 2>/dev/null; then
    return
  fi
  cp "$source" "$destination"
}

DAT_PATH="$CANONICAL_PANTHEON_DIR/Pantheon+SH0ES.dat"
COV_PATH="$CANONICAL_PANTHEON_DIR/Pantheon+SH0ES_STAT+SYS.cov"

fetch "$PANTHEON_DAT_URL" "$DAT_PATH"
fetch "$PANTHEON_COV_URL" "$COV_PATH"
verify_exact "$DAT_PATH" "$PANTHEON_DAT_SHA256" "$PANTHEON_DAT_BYTES" "PANTHEON_CATALOG"
verify_exact "$COV_PATH" "$PANTHEON_COV_SHA256" "$PANTHEON_COV_BYTES" "PANTHEON_STAT_SYS"

# Backward-compatible paths for older consumers. The canonical path above is
# authoritative. Hardlink avoids duplicate bytes when possible; copy is fallback.
compat_link_or_copy "$DAT_PATH" "$LEGACY_PANTHEON_DIR/Pantheon+SH0ES.dat"
compat_link_or_copy "$COV_PATH" "$LEGACY_PANTHEON_DIR/Pantheon+SH0ES_STAT+SYS.cov"
compat_link_or_copy "$DAT_PATH" "$LEGACY_PANTHEON_DIR/lcparam_full_long_zhel.txt"
printf '%s  %s\n' "$PANTHEON_COV_SHA256" "Pantheon+SH0ES_STAT+SYS.cov" > "$LEGACY_PANTHEON_DIR/Pantheon+SH0ES_STAT+SYS.cov.sha256"

READINESS="$REAL_DIR/pantheon_full_covariance_readiness.json"
python3 "$ROOT_DIR/scripts/verify_pantheon_inputs.py" \
  --data-dir "$CANONICAL_PANTHEON_DIR" \
  --require-full-covariance \
  --json > "$READINESS"

RECEIPT="$REAL_DIR/pantheon_full_covariance_materialization_receipt.json"
python3 - "$RECEIPT" "$DAT_PATH" "$COV_PATH" "$READINESS" <<PY
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

receipt_path, dat_path, cov_path, readiness_path = map(Path, sys.argv[1:])

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

readiness = json.loads(readiness_path.read_text(encoding='utf-8'))
payload = {
    'schema': 'rll.pantheon_full_covariance_materialization_receipt.v1',
    'observed_at_utc': datetime.now(timezone.utc).isoformat(),
    'provider': '${PANTHEON_SOURCE_REPO}',
    'source_commit': '${PANTHEON_SOURCE_COMMIT}',
    'source_git_blobs': {
        'Pantheon+SH0ES.dat': '${PANTHEON_DAT_GIT_BLOB}',
        'Pantheon+SH0ES_STAT+SYS.cov': '${PANTHEON_COV_GIT_BLOB}',
    },
    'canonical_directory': str(dat_path.parent.relative_to(Path('${ROOT_DIR}'))),
    'files': {
        dat_path.name: {'bytes': dat_path.stat().st_size, 'sha256': digest(dat_path)},
        cov_path.name: {'bytes': cov_path.stat().st_size, 'sha256': digest(cov_path)},
    },
    'readiness': readiness,
    'f_ok': readiness.get('full_covariance_likelihood_ready') is True,
    'f_gap': [] if readiness.get('full_covariance_likelihood_ready') else ['TOKEN_VAZIO_OR_BLOCKED_FULL_COVARIANCE'],
    'claim_allowed': False,
    'scientific_confirmation': False,
    'boundary': 'materialized_verified_input != model_validation',
}
receipt_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
PY

echo "[rll-materialize] canonical Pantheon+ full covariance READY"
echo "[rll-materialize] readiness=$READINESS"
echo "[rll-materialize] receipt=$RECEIPT"
echo "[rll-materialize] claim_allowed=false"
