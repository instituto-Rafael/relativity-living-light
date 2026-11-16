# Energy-momentum typed dimensional executor V2 — 2026-09-27

State: `PASS_DIMENSIONAL_SOFTWARE_REPAIR / SCIENTIFIC_SELECTION_OPEN`  
Scientific claim: `BLOCKED`

## Delta

The legacy scalar bridge declares rho-like quantities in `J/m^3` while its historical pressure helper computes `P/c^2` in `kg/m^3`. V2 does not erase that history. Instead, it prevents a nonzero pressure value from entering the scalar bridge unless the caller explicitly supplies a dimensional convention.

Two software-coherent representations are implemented:

- `ENERGY_DENSITY_CONVENTION`: every additive term is represented in `J/m^3`; pressure uses the identity `Pa = J/m^3`.
- `MASS_DENSITY_CONVENTION`: every energy-density term and pressure are divided by `c^2`, producing `kg/m^3`.

For the same scalar proxy inputs the required numerical invariant is:

[
A_E/c^2=A_M.
]

Uncertainties are transformed by the same convention as their corresponding values.

## Fail-closed boundary

Without an explicit convention:

```text
pressure = 0     -> historical energy-density numeric path remains available
pressure != 0    -> BLOCKED / explicit dimensional convention required
```

This closes only the **silent software unit-mixing defect**. It does not choose whether pressure belongs in this scalar proxy, does not select a stress-energy model, and does not establish a GR mechanism.

```text
SELECTED_CONVENTION=TOKEN_VAZIO_SCIENTIFIC_DIMENSIONAL_AUTHORITY
SCALAR_PRESSURE_PHYSICAL_MECHANISM=TOKEN_VAZIO
COVARIANT_T_MUNU_BINDING=TOKEN_VAZIO
claim_allowed=false
```

## Required execution gates

1. focused energy-momentum unit tests;
2. dimensional validator V2;
3. nonzero-pressure fixtures in both conventions;
4. cross-convention c² equivalence;
5. uncertainty conversion parity.

Observed focused execution on head `c81e2a4862f557873315e8ac5be4004be1bc4bec` passed all causal gates in workflow run `36306055734`.

Evidence:

```text
compile_changed_python=PASS
dimensional_contract_tests=PASS_3
nonzero_pressure_typed_fixtures=PASS
cross_convention_c2_equivalence=PASS
dimensional_validator_v2=PASS
artifact_digest=sha256:bdfab7c5ae1e01418708eeefe8c7d59c3af3ed2f38008aeaf3d6d1c3852fee8b
```

The earlier run `36305991310` is retained as `ENVIRONMENT_DEPENDENCY_PREEXECUTION`: package initialization required NumPy before the fixture reached the executor. It is not classified as a dimensional FAIL.

This promotes only the software-dimensional repair. The scientific stress-energy selection remains open.

## R3

F_ok: typed implementation + explicit unit contracts + focused exact-head execution PASS without silently selecting physics.

F_gap: scientific stress-energy semantics and later promotion-layer regression gates remain open.

F_next: merge through WORK→rll/lab, then propagate via rll/integration→rll/release→main; never promote a physical claim from this repair alone.
