#!/usr/bin/env bash
# Shared GitHub Actions helpers for real-data auxiliary workflows.
# Canonical policy: .github/workflows/real-data-complete-execution.yml
set -euo pipefail

: "${CANONICAL_REAL_DATA_WORKFLOW:=.github/workflows/real-data-complete-execution.yml}"
: "${CLAIM_BOUNDARY:=Real-data auxiliary workflow only; outputs cannot validate RLL, cosmology, superiority, or non-synthetic status beyond the explicit checks in this run.}"

rll_real_data_write_claim_boundary() {
  local out_dir="${1:?output directory required}"
  mkdir -p "$out_dir"
  cat > "$out_dir/CLAIM_BOUNDARY.md" <<BOUNDARY
# Claim Boundary

- Canonical workflow policy: \`$CANONICAL_REAL_DATA_WORKFLOW\`
- Boundary: $CLAIM_BOUNDARY
- Synthetic boundary: mock, synthetic, demo, fixture, example, placeholder, and generated test payloads must not be promoted as real observational evidence.
BOUNDARY
}

rll_real_data_write_checksums() {
  local target_dir="${1:?target directory required}"
  mkdir -p "$target_dir"
  find "$target_dir" -type f ! -name CHECKSUMS.sha256 -print0 | sort -z | xargs -0 -r sha256sum > "$target_dir/CHECKSUMS.sha256"
}

rll_real_data_assert_boundary_file() {
  local boundary_file="${1:?boundary file required}"
  test -s "$boundary_file"
  grep -Eiq 'synthetic|mock|fixture|placeholder|demo|example' "$boundary_file"
  grep -Eiq 'claim|boundary|fronteira' "$boundary_file"
}
