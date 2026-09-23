#!/usr/bin/env sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CC=${CC:-cc}
OUT=${OUT:-"$HERE/multilayer_geometry"}
"$CC" -std=c99 -O2 -Wall -Wextra "$HERE/multilayer_geometry.c" -lm -o "$OUT"
"$OUT" selftest
