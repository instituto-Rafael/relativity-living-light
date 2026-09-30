# Security Policy

## Supported surface

Security reports are accepted for the current default branch and active maturity
branches: `rll/lab`, `rll/integration`, and `rll/release`.

## Reporting a vulnerability

Do not publish credentials, personal data, exploit details, or live attack
instructions in a public issue.

Use **Security → Report a vulnerability** in this repository when private
vulnerability reporting is available. If that control is unavailable, open a
minimal public issue containing only:

- the affected path or component;
- a non-sensitive impact summary;
- a request for a private communication channel.

Do not attach secrets, tokens, private datasets, or a working exploit.

## Evidence boundary

A workflow pass proves only that the declared checks executed. It does not prove
absence of vulnerabilities, external compliance, scientific validity, or
independent certification.

Private vulnerability reporting, secret scanning, push protection, rulesets, and
required checks are GitHub control-plane settings. Until settings evidence is
recorded, their state is `TOKEN_VAZIO_EXTERNAL_SETTING`.


## Governed development runtime

The promoted Rx validation route is bounded by a deterministic, deny-by-default
development envelope. It is software-development governance, not an autonomous
agent and not a security certification.

Canonical controls:

- `data/governance/RLL_DEVELOPMENT_SECURITY_ENVELOPE_V1.json`
- `data/governance/RLL_DATA_USE_PURPOSE_REGISTRY_V1.json`
- `data/governance/RLL_SECURITY_PRIVACY_RISK_REGISTER_V1.json`
- `internal/governance/development_guard.py`
- `tools/rll_security_surface_audit.py`
- `tools/validate_rll_development_governance.py`
- `docs/governance/RLL_DEVELOPMENT_SECURITY_GOVERNANCE_V1.md`
- `docs/governance/RLL_INCIDENT_RESPONSE_V1.md`

The governed route forbids autonomous goal/scope expansion, free-text shell,
arbitrary network destinations, secret ingestion, personal-data processing,
destructive actions, and arbitrary filesystem writes by default.

Network access is off by default. When explicitly enabled for a declared source
probe, only policy-allowlisted HTTPS hosts and read methods are permitted.

A policy or audit PASS does not prove absence of vulnerabilities, OS sandboxing,
legal compliance, independent security review, or scientific validity.

## Incident handling boundary

If a secret, private/personal dataset, unauthorized network destination, policy
bypass, or unexpected write is observed, stop the affected route before further
processing. Do not reproduce the sensitive value or working exploit in public
issues. Follow `docs/governance/RLL_INCIDENT_RESPONSE_V1.md` and preserve only
the non-sensitive evidence needed for rollback and audit.
