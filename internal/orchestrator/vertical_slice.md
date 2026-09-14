# Vertical Slice v1 (readonly)

Fluxo implementado:

1. conversation/chunks e contexto são representados por contratos em `docs/contracts`.
2. `intent_ir` tipado é validado contra `docs/contracts/intent_ir.schema.json`.
3. governance gate aplica `internal/governance/capabilities.json` + `internal/governance/policy.json`.
4. execution_plan compilado permite apenas comandos read-only explícitos:
   - `git status`
   - `git diff --stat`
5. execução local read-only captura stdout/stderr/exit code.
6. hashes SHA-256 completos de stdout/stderr são calculados.
7. `execution_result.json` auditável é gerado com estado final e referências de origem.

Lacunas explícitas:
- commits/hashes privados dos repositórios externos permanecem `TOKEN_VAZIO` em `runtime-lock.json` até auditoria autorizada.
