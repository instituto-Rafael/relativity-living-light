# Multilayer Geometry Portable C99 V1

Repository: `instituto-Rafael/relativity-living-light`  
Role: RLL portable C99 consumer alongside the existing 20-scenario / 120-test executable suite  
State: `IMPLEMENTED_PORTABLE_C99 / LOCAL_SOURCE_SELFTEST_35_PASS / REPO_PROVIDER_CI_NOT_RUN`

This directory carries the portable consumer/reference kernel for the multilayer circle–polygon geometry contract.

## Build

```sh
sh tools/multilayer_geometry/build_and_selftest.sh
```

or directly:

```sh
cc -std=c99 -O2 -Wall -Wextra tools/multilayer_geometry/multilayer_geometry.c -lm -o multilayer_geometry
./multilayer_geometry selftest
```

Termux can use `clang` through `CC=clang`.

## Commands

```sh
./multilayer_geometry polygon 8 1 3
./multilayer_geometry layer 2 0.4142135623730951 3
./multilayer_geometry triangle 2
./multilayer_geometry sphere 2.4 1.5707963267948966
```

The kernel covers regular-polygon metrics, chord classes, concentric layer radii/annuli, triangle-circle ratios, rotation, reflection, homothety, radial projection, circle inversion, triangle overlays, classical Snell fixtures, spherical chord/arc/excess relations, K8/K16 combinatorics and symmetry checks.

## Provenance

Publication authority:
`rafaelmeloreisnovo/papers/papers/multilayer_circle_polygon_geometry_v1/paper.md`

RLL executable contract:
`instituto-Rafael/relativity-living-light/data/contracts/rll_multilayer_circle_polygon_geometry_v1.yml`

Expected validated source SHA-256:
`8a254f5ffefae6db246a5ae09b700f21dc3754d884f3b00c3da7142ea2f50388`

Local pre-materialization self-test: `35 PASS / 0 FAIL`.

## Boundary

This is a mathematical geometry kernel. It does not by itself establish a physical, optical, atomic or cosmological mechanism. Geometric projection and Snell refraction are separate operations.

For Android repositories, source presence is not the same as JNI/UI wiring; app-level binding remains `TOKEN_VAZIO_NOT_WIRED` unless separately implemented and tested.
