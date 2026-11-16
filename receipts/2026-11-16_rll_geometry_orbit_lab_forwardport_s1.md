# RLL Geometry/orbit/field reference adapter — scoped producer transfer S1 (2026-11-16)

- mu_id: MU-RLL-GEOMETRY-ORBIT-LAB-20261116-S1
- source: https://github.com/instituto-Rafael/relativity-living-light/pull/1214
- source_head: dcfffaab2ec72347174215be83b19b7ffa6369bf
- target_lab_parent: 8b51fc2c1f4bec15b5d38c422a0007a01640b497
- target_review_branch: work/rll-lab-geometry-orbit-fields-forwardport-20261116-v1
- exact_source_blobs:
  - data/contracts/rll_geometry_orbit_fields.v1.json: 2ea93899054a4532d98425e12fd074b8354a9227
  - docs/science/RLL_GEOMETRY_ORBIT_FIELDS_DIAGNOSTIC_V1.md: e7a866a141758c708c054bba0b6ff94ec1efd02d
  - scripts/validation/rll_geometry_orbit_fields_v1.py: ca1e4533b8d80844fc102e34740bef166c77c910
  - tests/test_rll_geometry_orbit_fields_v1.py: 7947778e20aeae879cd0981b119ba926d1522aed
- scope: 4 new files only, no replacements; reference geometry, Newtonian local two-body orbit, ideal magnetic dipole with explicit units; no cosmological likelihood binding.
- assertions: claim_allowed=false; likelihood_binding.direct=false; physical_validation=NOT_RUN; standalone stdlib module, no network in source.
- tests: 17 deterministic unit tests declared in source; new exact-head CI must run to establish execution, none inferred from file existence.
- controls: no H(z) edits, no BAO, no DESI covariance replacements, no secret transfer, no new automation or source overwrite.
- status: REFERENCE_ADAPTER_IMPLEMENTED_UNTESTED; claim_allowed=false.
- rollback: reviewed revert/successor, preserve provenance of upstream PR #1214.
