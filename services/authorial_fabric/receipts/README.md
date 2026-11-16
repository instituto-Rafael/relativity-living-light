# Authorial Fabric receipt custody

This directory is for small reviewed successor receipts that describe durable state transitions of the Authorial Science Fabric.

Raw downloaded source bytes, network logs and per-run hash inventories belong in GitHub Actions artifacts, not in the repository by default.

A durable receipt may be committed only when it adds a material state delta and preserves:

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`

Required durable fields: source or run reference, exact repository HEAD, decision, evidence class, gaps/TOKEN_VAZIO, next action and rollback/supersedes reference when applicable.

Secret values, lengths, hashes, authorization headers and equivalence between secret names are forbidden receipt material.
