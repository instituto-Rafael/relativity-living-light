#!/bin/sh
# RLL identity capture outside the app: only on a user-authorized ADB device.
# Does not install/update the app, change system state, or assert hardware attestation.
set -eu
PKG=org.rafaelia.rll.debug
OUT="${1:-./rll_install_capture_$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUT"
if ! command -v adb >/dev/null 2>&1; then
  printf 'ROUTE_STATE=BLOCKED MISSING_ADB\n' > "$OUT/STATUS.txt"
  exit 2
fi
N=$(adb devices | awk '$2=="device" {n++} END{print n+0}')
if [ "$N" != "1" ]; then
  printf 'ROUTE_STATE=BLOCKED EXPECT_ONE_AUTHORIZED_DEVICE\n' > "$OUT/STATUS.txt"
  exit 2
fi
printf 'schema=rll.android.external_install_witness.v1\nsource=ADB_HOST_OUTSIDE_APP\npackage=%s\n' "$PKG" > "$OUT/receipt.txt"
adb shell getprop ro.build.version.sdk | tr -d '\r' | sed 's/^/sdk=/' >> "$OUT/receipt.txt"
adb shell getprop ro.product.cpu.abi | tr -d '\r' | sed 's/^/abi=/' >> "$OUT/receipt.txt"
adb shell dumpsys package "$PKG" > "$OUT/dumpsys_package.txt" || :
adb shell pm path "$PKG" | tr -d '\r' > "$OUT/pm_path.txt"
REMOTE=$(sed -n 's/^package://p' "$OUT/pm_path.txt" | grep '/base\\.apk$' | head -n 1)
if [ -z "$REMOTE" ]; then
  printf 'installation=TOKEN_VAZIO_PM_PATH\n' >> "$OUT/receipt.txt"
  exit 3
fi
if ! adb pull "$REMOTE" "$OUT/installed_base.apk" >/dev/null 2>&1; then
  printf 'installation=TOKEN_VAZIO_APK_PULL_DENIED\n' >> "$OUT/receipt.txt"
  exit 4
fi
H=$(sha256sum "$OUT/installed_base.apk" | awk '{print $1}')
printf 'installed_base_apk_sha256=%s\n' "$H" >> "$OUT/receipt.txt"
if [ "$H" = 'f10aa018ecabb941a13fe0c1c09ac35fa266029cd4fc9c982e52874bcda4b8b5' ]; then
  printf 'apk_identity=MATCH_UPLOADED_DEBUG\n' >> "$OUT/receipt.txt"
else
  printf 'apk_identity=DIFFERENT_OR_UPDATED_APK_REQUIRES_PROVENANCE\n' >> "$OUT/receipt.txt"
fi
printf 'scope=EXTERNAL_ADB_WITNESS_NOT_HARDWARE_ATTESTATION\n' >> "$OUT/receipt.txt"
printf 'DONE: %s\n' "$OUT"
