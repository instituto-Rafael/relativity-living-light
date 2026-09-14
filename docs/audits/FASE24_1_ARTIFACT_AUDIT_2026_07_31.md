# Auditoria técnica — RLL FASE 24.1 e artefato 30647186593

**Data da auditoria:** 31 de julho de 2026  
**Repositório canônico:** `instituto-Rafael/relativity-living-light`  
**Commit auditado:** `dc5fcfb3b786bf59d32ebfa22ad6f4eed15f738e`  
**Workflow:** `RLL FASE 24.1 — Gate Determinístico`  
**Run:** `30647186593`  
**Job:** `91211349808`  
**Estado epistemológico preservado:** `claim_allowed=false`

## 1. Veredito

O artefato é **íntegro como pacote de logs**, porém a execução completa está **operacionalmente bloqueada**. O bloqueio não foi causado pelo conjunto principal de testes: o próprio run registrou **855 testes + 3 subtestes aprovados**. A causa predominante é **desalinhamento entre o orquestrador FASE 24.1 e os contratos executáveis atuais**: caminhos movidos, argumentos de CLI removidos/obrigatórios e um perfil Bayesiano “real” que era chamado sem garantir a materialização de inferência Bayesiana real.

A evidência científica do run **não autoriza promoção do RLL**. Nos blocos que executaram com dados reais, ΛCDM ou CPL permaneceram preferidos; os três falsificadores de `z_t` falharam. O estado correto continua sendo `CLAIM_BLOCKED`.

## 2. Integridade do ZIP

| Controle | Resultado |
|---|---|
| Arquivo | `rll-fase24-1-30647186593-completo.zip` |
| SHA-256 | `b51f1fcdfa8e841a311fac8a9a5d1d64319684319e972cd7d93b870432b5eed1` |
| Arquivos no ZIP | 47 |
| Bytes descompactados | 158,073 |
| Teste estrutural ZIP | PASS |
| Entradas verificadas por `CHECKSUMS.sha256` | 45 |
| Checksums internos | PASS |
| Digest GitHub × digest local | `MATCH` |

**Conclusão de custódia:** não há indicação de corrupção ou adulteração após a publicação. A lacuna era de **proveniência interna**: o pacote antigo não selava adequadamente commit, run, ambiente Python, manifesto completo e arquivos científicos materializados no run.

## 3. Resultado operacional observado

| Estado | Quantidade |
|---|---:|
| OK | 28 |
| FAIL | 7 |
| TOKEN_VAZIO | 4 |
| Gate | `BLOCKED` |
| Claim | `false` |

### Causas-raiz confirmadas

| Step | Estado | Causa | Tratamento aplicado |
|---:|---|---|---|
| 07 | TOKEN_VAZIO | caminho antigo `scripts/build_repo_real_inventory.py` | usar `tools/docs_inventory.py` |
| 08 | FAIL | `pytest -k real_data_contract` não selecionou testes; exit 5 | executar arquivos contratuais explícitos |
| 09 | TOKEN_VAZIO | verificador movido de `scripts/` para `tools/` | usar `tools/verify_real_source_signatures.py` + auditoria de materialização |
| 11 | TOKEN_VAZIO | builder movido | usar `scripts/data_scan/build_raw_data_manifest_status.py` |
| 12 | TOKEN_VAZIO | builder movido | usar `scripts/data_scan/build_real_seed_ingestion_plan.py` |
| 13 | FAIL | import relativo do Pantheon executado a partir da raiz | executar no diretório `scripts/pantheon` |
| 15 | FAIL | argumento inexistente `--desi-only` | usar CLI atual com `--output-dir`, `--real-data-dir`, `--data-source repo` |
| 21 | OK enganoso | job “real” executou `structure_d_default`; no perfil real, `run_all.py` retorna antes do bloco Bayesiano | fixar o perfil real e exigir pós-condição; sem MCMC/nested sampling materializado, registrar `TOKEN_VAZIO` |
| 22 | FAIL | argumento inexistente `--bayes-factor` e ausência de saída Bayes real no ramo real | materializar proxy BIC real explicitamente, sem chamá-lo de inferência |
| 28 | FAIL | faltou `--input` | materializar JSON a partir de `model_comparison_real.csv` |
| 29 | FAIL | faltou `--output` | fornecer saída explícita ao DHA |
| 36 | FAIL | validador exigia nome legado `commit_light_artifacts` | validar controle semântico e aceitar política atual de PR revisado |

## 4. Conferência científica do run

| Bloco | Resultado observado | Leitura conservadora |
|---|---|---|
| DESI DR2 BAO, 13 pontos | χ² ΛCDM = `28.9659`; χ² RLL = `93.8061` | forte piora local do RLL nesta configuração |
| H(z), N=33 | χ² ΛCDM = `25.6541`; χ² RLL = `25.8423` | ΛCDM vence por margem pequena |
| `z_t` | melhor BAO `0.3`; melhor H(z) `2.0`; F_ZT_01/02/03 = FAIL | transição não passa o contrato atual |
| Structure-D real, N=45 | χ² RLL-like `123.5977` vs ΛCDM `123.6811`; AIC `137.5977` vs `131.6811`; BIC `150.2443` vs `138.9078` | ganho mínimo em χ² não compensa complexidade |
| Proxy BIC real | ΔBIC = `11.3365`; ln(B10)≈`-5.6683` | reprova o threshold F-COS-04 (`> -5`); não equivale a MCMC/nested sampling |
| Inferência Bayes real | artefato MCMC/nested-sampling não materializado pelo ramo real | `TOKEN_VAZIO`, sem falso verde |
| Validação real adicional | AIC ΛCDM `45.38` vs RLL `54.89`; BIC `50.80` vs `63.92` | ΛCDM preferido |
| Governança acadêmica | CPL melhor por AICc/BIC; `Os0` do RLL colapsou a zero | `CLAIM_BLOCKED`; publicar apenas auditoria/diagnóstico |

**Invariante científica:** um step pode retornar `OK` porque o programa terminou, enquanto o falsificador científico retorna `FAIL`. A correção faz o gate científico bloquear também por falsificador reprovado, não apenas por arquivo ausente.

## 5. Artefato: avaliação por dimensão

| Dimensão | Estado anterior | Correção |
|---|---|---|
| Integridade binária | PASS | mantida com SHA-256 |
| Proveniência do run | GAP | `PROVENANCE.json` com SHA, run ID, ref, runner e limites |
| Ambiente | GAP | `PYTHON_ENVIRONMENT.txt` |
| Inventário de conteúdo | parcial | `MANIFEST.json` com bytes e SHA-256 por arquivo |
| Verificação independente | manual | `VERIFY_ARTIFACT.py` |
| Evidência científica materializada | insuficiente | cópia dos JSON/CSV do run; pós-condição Bayes real e status `TOKEN_VAZIO` quando ausente |
| Console | fora da cadeia interna | console copiado antes do selo final |
| Fronteira epistemológica | correta, mas incompleta | `claim_allowed=false` preservado e falhas de falsificadores passam a bloquear |

## 6. Implementação aplicada

**Branch:** `fix/fase24-1-orchestrator-artifacts-20260731`

Arquivos tratados:

- `tools/rll_pipeline_fase24_1_runtime.py` — SHA-256 `783afe134b9f26a28ec65e519cffe71ec65938c3fbbf75758f78de0d62095d41`
- `tests/test_rll_pipeline_fase24_1_runtime.py` — SHA-256 `03839cf4d76519743f7d59c4d3560f199ea2c7ffb8244ebb2a79990f7f49be03`
- `tools/validate_six_sigma_real_data_controls.py` — SHA-256 `05023151d6bfda0eab57e46e3543112f6a8a68c94645f3e0b2e021e109b976b1`
- `tests/test_validate_six_sigma_real_data_controls.py` — SHA-256 `720d1c0b6a386261832f33fa5e62349865091eaf7de35fd89cb0be5c04222271`
- `.github/workflows/rll-pipeline-linear-completo.yml` — SHA-256 `ba646d3fd4e37bc52abe336177ef7389079740b71941b5a695295666f4b629ca`

Validações focais executadas localmente sobre a camada alterada:

- `24 passed` em testes do núcleo determinístico, alinhamento FASE 24.1, Bayes auditável e Six Sigma;
- `py_compile`: PASS;
- parse YAML do workflow: PASS;
- contrato arquitetural preservado: 6 steps físicos;
- execução direta `python tools/rll_pipeline_fase24_1_runtime.py --help`: PASS.

Esses testes comprovam a coerência da correção focal. A execução científica completa deve continuar bloqueada sempre que um falsificador reprovar ou uma evidência atual estiver ausente.

## 7. Decisão

```yaml
artifact_integrity: PASS
orchestrator_before_fix: BLOCKED_BY_CONTRACT_DRIFT
remediation: APPLIED_WITH_REAL_BAYES_TOKEN_VAZIO
scientific_claim: BLOCKED
claim_allowed: false
publication_ready: false
next_verifiable_step: run CI on the review branch; inspect the sealed artifact; implement genuine real-data MCMC/nested sampling before closing TOKEN_VAZIO
```

## Retroalimentação R₃

- **F_ok:** ZIP e checksums íntegros; suíte original forte; causas operacionais localizadas e tratadas.
- **F_gap:** o run auditado não continha proveniência completa; o ramo Structure-D real ainda não materializa MCMC/nested sampling; a ciência atual não favorece o RLL.
- **F_next:** validar o PR/CI, auditar o novo artefato selado e manter a inferência Bayes real como `TOKEN_VAZIO` até implementação verificável.
