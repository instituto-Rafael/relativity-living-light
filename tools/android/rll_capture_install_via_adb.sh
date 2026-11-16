#!/bin/sh
# External, read-only Android installation receipt; NEVER installs/uninstalls.
# This is an ADB host observation, not a hardware attestation.
set -eu
umask 077
export LC_ALL=C

PKG='org.rafaelia.rll.debug'
if [ "$#" -gt 2 ]; then
  printf 'Usage: %s OUTPUT_DIR EXPECTED_APK_SHA256\n' "$0" >&2
  exit 2
fi
OUT="${1:-./rll_install_capture_$(date -u +%Y%m%dT%H%M%SZ)}"
EXPECTED="${2:-}"
if [ -n "$EXPECTED" ]; then
  case "$EXPECTED" in
    *[!0123456789abcdef]* )
      printf 'ERROR: EXPECTED_APK_SHA256 must be lowercase hexadecimal\n' >&2
      exit 2
      ;;
  esac
  if [ "${#EXPECTED}" -ne 64 ]; then
    printf 'ERROR: EXPECTED_APK_SHA256 must contain 64 hexadecimal characters\n' >&2
    exit 2
  fi
fi

# Do not accidentally overwrite earlier forensic evidence.
if [ -e "$OUT" ]; then
  printf 'ERROR: output path already exists, preserving predecessor: %s\n' "$OUT" >&2
  exit 2
fi
mkdir -p "$OUT"
printf 'schema=rll.android.external_install_witness.v2\n' > "$OUT/receipt.txt"
printf 'source=ADB_HOST_OUTSIDE_APP\npackage=%s\n' "$PKG" >> "$OUT/receipt.txt"
printf 'scope=EXTERNAL_ADB_OBSERVATION_NOT_HARDWARE_ATTESTATION\n' >> "$OUT/receipt.txt"
printf 'device_mutation=NONE\n' >> "$OUT/receipt.txt"

fail() {
  printf 'ROUTE_STATE=BLOCKED %s\n' "$1" > "$OUT/STATUS.txt"
  printf 'installation=TOKEN_VAZIO_%s\n' "$1" >> "$OUT/receipt.txt"
  exit 3
}

# Input gate precedes all device access: no digest, no ADB observations.
if [ -z "$EXPECTED" ]; then
  printf 'apk_identity=TOKEN_VAZIO_EXPECTED_HASH_NOT_SUPPLIED\n' >> "$OUT/receipt.txt"
  printf 'ROUTE_STATE=HOLD_EXPECTED_HASH_NOT_SUPPLIED\n' > "$OUT/STATUS.txt"
  exit 4
fi

command -v adb >/dev/null 2>&1 || fail MISSING_ADB
command -v sha256sum >/dev/null 2>&1 || fail MISSING_SHA256SUM
adb devices > "$OUT/adb_devices.txt" || fail ADB_DEVICES_FAILED
# Do not guess which device is authoritative if more than one is connected.
N=$(awk '$2=="device" {n++} END {print n+0}' "$OUT/adb_devices.txt")
[ "$N" = 1 ] || fail EXPECT_ONE_AUTHORIZED_DEVICE

adb shell getprop ro.build.version.sdk > "$OUT/sdk.raw" || fail SDK_QUERY_FAILED
adb shell getprop ro.product.cpu.abi > "$OUT/abi.raw" || fail ABI_QUERY_FAILED
tr -d '\r' < "$OUT/sdk.raw" | sed 's/^/sdk=/' >> "$OUT/receipt.txt"
tr -d '\r' < "$OUT/abi.raw" | sed 's/^/abi=/' >> "$OUT/receipt.txt"
adb shell pm path "$PKG" > "$OUT/pm_path.raw" || fail PM_PATH_FAILED
tr -d '\r' < "$OUT/pm_path.raw" > "$OUT/pm_path.txt"
# Byte identity of base.apk cannot attest the complete installed package if
# splits exist. Fail before any pull rather than silently reporting partial PASS.
PM_PATH_LINES=$(awk 'NF {n++} END {print n+0}' "$OUT/pm_path.txt")
PM_APKS=$(awk '/^package:\// {n++} END {print n+0}' "$OUT/pm_path.txt")
[ "$PM_PATH_LINES" = "$PM_APKS" ] || fail PM_PATH_UNEXPECTED_FORMAT
[ "$PM_APKS" -le 1 ] || fail SPLIT_APKS_REQUIRE_FULL_MANIFEST
# An Android split-package may list multiple APKs; require a single base.apk.
BASE_MATCHES=$(sed -n 's/^package:\(.*\/base[.]apk\)$/\1/p' "$OUT/pm_path.txt")
[ -n "$BASE_MATCHES" ] || fail PM_BASE_APK_ABSENT
case "$BASE_MATCHES" in
  *'
'* ) fail PM_AMBIGUOUS_BASE_APK ;;
esac
# Prevent option injection through untrusted device output.
case "$BASE_MATCHES" in
  /* ) : ;;
  * ) fail PM_BASE_PATH_NOT_ABSOLUTE ;;
esac
adb pull "$BASE_MATCHES" "$OUT/installed_base.apk" > "$OUT/adb_pull.log" 2>&1 || fail APK_PULL_DENIED
[ -s "$OUT/installed_base.apk" ] || fail APK_PULL_EMPTY
H=$(sha256sum "$OUT/installed_base.apk" | awk '{print $1}')
printf 'installed_base_apk_sha256=%s\n' "$H" >> "$OUT/receipt.txt"

printf 'expected_apk_sha256=%s\n' "$EXPECTED" >> "$OUT/receipt.txt"
if [ "$H" != "$EXPECTED" ]; then
  printf 'apk_identity=MISMATCH_EXPECTED_APK\n' >> "$OUT/receipt.txt"
  printf 'ROUTE_STATE=FAIL_APK_HASH_MISMATCH\n' > "$OUT/STATUS.txt"
  exit 5
fi
printf 'apk_identity=MATCH_EXPECTED_APK\n' >> "$OUT/receipt.txt"
printf 'ROUTE_STATE=PASS_SCOPED_EXTERNAL_ADB_APK_HASH\n' > "$OUT/STATUS.txt"
printf 'DONE: %s\n' "$OUT"
