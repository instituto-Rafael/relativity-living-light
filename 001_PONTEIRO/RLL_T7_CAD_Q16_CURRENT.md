# START HERE — RLL T7 CAD/ENGINEERING Q16 V1

CURRENT_STATE: `SCOPED_2D_TRUSS_PROTOTYPE`, `claim_allowed=false`, `NOT_CERTIFIED`, no cosmology likelihood modification.

SOURCE: `core/lowlevel_runtime/cad_t7_v1/core/lowlevel_runtime/cad_t7_v1/docs/ENGINEERING_CONTRACT.md` and existing RLL `data/governance/RLL_DYNAMIC_STRUCTURAL_GEOMETRY_CONTEXT_V1.json` + `RLL_ADAPTIVE_GEOMETRY_FEATURE_LAYER_V1.json`.
CODE: `core/lowlevel_runtime/cad_t7_v1/core/rll_cad.{h,c}`, `core/lowlevel_runtime/cad_t7_v1/core/rll_cad_svg.c`, optional `core/lowlevel_runtime/cad_t7_v1/core/rll_crc_hw_aarch64.c`.
ROUTE: `core/lowlevel_runtime/cad_t7_v1/spec/architecture.json` -> `core/lowlevel_runtime/cad_t7_v1/build.sh` -> `core/lowlevel_runtime/cad_t7_v1/results/models42.json` -> `core/lowlevel_runtime/cad_t7_v1/svg/design_XX.svg` -> `core/lowlevel_runtime/cad_t7_v1/results/compression_42_compositions.csv` -> tests -> independent review.
FALSIFIERS: no analog passage from T7 to physical 7D; compare 2D FEA, independent numeric reference, SW CRC IEEE, no runtime absent NEON/CRC capability, buffer bounds, 8 threads serial parity.
BOUNDARY: `ANDROID_DEX_NOT_BUILT`, `ARM_HW_NOT_RUN`, `SHEAR_TORSION_BENDING_NOT_RUN`, `L2_HIT_RATE_NOT_MEASURED`, `ENGINEERING_CERTIFICATION=false`.
ROLLBACK: close draft branch/revert additive file set; no changes to source cosmological gates or real observational datasets.
