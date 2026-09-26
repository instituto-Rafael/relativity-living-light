# RLL Operator Lab V1

State: IMPLEMENTED / FAIL-CLOSED / claim_allowed=false

RLL Operator Lab is an isolated mathematical execution surface for typed operator paths. It is not part of canonical Rx formula selection and cannot close a scientific gate.

## Runtime boundary

- Python standard library only.
- 16 explicitly supported operators.
- unsupported operator -> BLOCKED_UNSUPPORTED.
- no dynamic eval/exec.
- no arbitrary shell.
- no network.
- no physics binding.

## Negative-first suite

The canonical suite contains 10 invalid fixtures followed by 10 valid fixtures. Positive fixtures run only after the negative gate closes.

## Evidence route

Operator Lab -> receipt.json -> manifest.json -> evidence_envelope.json.

A PASS receipt means the declared deterministic fixtures behaved as expected. It does not imply physical truth, cosmological likelihood validation, SCI_GATE closure, cryptographic security or independent reproduction.

Papers precursor: rafaelmeloreisnovo/papers@03efd335ee7b1bfd7e77c6fa61873c19b0ee437f
RLL pre-paper: cd7d42efee21855f4c6c17ccb67a83df5e26b965
