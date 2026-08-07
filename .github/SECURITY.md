# Security Policy

## Supported surface

Security reports are accepted for the current default branch and active maturity branches: `rll/lab`, `rll/integration`, and `rll/release`.

## Reporting a vulnerability

Do not publish credentials, personal data, exploit details, or live attack instructions in a public issue. Use **Security → Report a vulnerability** when private vulnerability reporting is available. If that control is unavailable, open a minimal public issue containing only the affected path/component, a non-sensitive impact summary, and a request for a private channel.

Do not attach secrets, tokens, private datasets, or a working exploit.

## Evidence boundary

A workflow pass proves only that declared checks executed. It does not prove absence of vulnerabilities, compliance, scientific validity, or independent certification.

Private vulnerability reporting, secret scanning, push protection, rulesets, required checks and protected environments are GitHub control-plane settings. Until fresh settings evidence is recorded, their state is `TOKEN_VAZIO_EXTERNAL_SETTING`.
