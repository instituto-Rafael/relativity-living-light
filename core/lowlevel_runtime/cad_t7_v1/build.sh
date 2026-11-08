#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build results svg
CC=${CC:-clang}
"$CC" -std=c11 -O2 -fPIC -fno-builtin -ffreestanding -fno-stack-protector -shared -nostdlib core/rll_cad.c core/rll_cad_svg.c -o build/librllcad_host.so
"$CC" -std=c11 -O2 core/rll_cad.c core/rll_cad_svg.c host/demo.c -o build/runner
./build/runner svg/bridge.svg results/models42.json
python3 tools/representations.py
python3 -m unittest discover -s qa -p '*_checks.py' -v
"$CC" -O2 -pthread -std=c11 core/rll_cad.c host/parallel8.c -o build/parallel8
./build/parallel8
"$CC" -target armv7a-none-eabi -mcpu=cortex-a7 -mfpu=neon -mfloat-abi=softfp -O2 -std=c11 -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -c core/rll_cad.c -o build/rll_cad_armv7_neon.o
"$CC" -target armv7a-none-eabi -mcpu=cortex-a7 -mfpu=neon -mfloat-abi=softfp -O2 -std=c11 -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -c core/rll_cad_svg.c -o build/rll_cad_svg_armv7.o
"$CC" -target aarch64-none-elf -march=armv8-a+crc -O2 -std=c11 -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -c core/rll_crc_hw_aarch64.c -o build/rll_crc_hw_arm64.o
"$CC" -target aarch64-none-elf -O2 -std=c11 -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -c core/rll_cad.c -o build/rll_cad_arm64.o
readelf -h build/rll_cad_armv7_neon.o | grep -E 'Class:|Machine:'
readelf -h build/rll_cad_arm64.o | grep -E 'Class:|Machine:'

# Android-native ELF loading candidates: no libc dependencies; not an installed APK.
"$CC" -target armv7a-linux-androideabi21 -march=armv7-a -mfpu=neon -mfloat-abi=softfp -ffreestanding -fno-builtin -fPIC -O2 -shared -nostdlib -fuse-ld=lld -Wl,-z,defs -Wl,-z,relro -Wl,-z,now core/rll_cad.c core/rll_cad_svg.c -o build/librllcad_android_armv7.so
"$CC" -target aarch64-linux-android21 -ffreestanding -fno-builtin -fPIC -O2 -shared -nostdlib -fuse-ld=lld -Wl,-z,defs -Wl,-z,relro -Wl,-z,now core/rll_cad.c core/rll_cad_svg.c -o build/librllcad_android_arm64.so
test -z "$(nm -u build/rll_cad_armv7_neon.o)"
test -z "$(nm -u build/rll_cad_svg_armv7.o)"
if command -v javac >/dev/null 2>&1; then mkdir -p build/java; javac -d build/java android/RllCadBridge.java; fi
