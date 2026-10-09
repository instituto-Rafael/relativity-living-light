# RAFAELIA Ω — CI canônica 555 / C freestanding / evidência antes do claim

**Data:** 2026-10-09  
**Estado:** IMPLEMENTED_UNTESTED_PROVIDER (até comprovante de execução).  
**Autoridade:** `instituto-Rafael/relativity-living-light`.  
**Workflow novo:** `.github/workflows/555_00_10_20_30_90_rll_omega_freestanding_canonical.yml`.  
**Executor local reprodutível:** `sh tools/ci/rll_omega_canonical_freestanding_gate.sh`.  
**Princípio:** SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM; TOKEN_VAZIO ≠ 0.

## O significado de freestanding neste contrato
- O **núcleo de produção** auditado é `core/lowlevel_runtime/c/rll_canonical_coupling.c` junto ao cabeçalho autoral. Objetos são compilados com `-ffreestanding -fno-builtin -nostdlib`, sem malloc/libc/heap, e o gate rejeita símbolos indefinidos por alvo.
- `tests/c/rll_canonical_coupling_vectors.c` é **harness hospedado**, executado em Linux só para validar observações, unidades, tipos, evidência sintética, TOKEN_VAZIO e `claim_allowed=0`. Seu exit code **não demonstra execução ARM física**.
- **GitHub Actions, runners ubuntu-24.04, checkout, upload-artifact, POSIX sh, clang, nm, readelf, sha256sum e Python WS01 são todos fronteira hospedada**. Não são parte do núcleo freestanding. Nenhum `apt`, `pip` ou `npm` é instalado.
- O gate cria objetos ELF relocáveis: isso **não prova** link estático ou boot real ARMv7/AArch64. `execution_armv7=NOT_RUN_PHYSICAL`, `execution_aarch64=NOT_RUN_PHYSICAL` e `claim_allowed=false` são invariantes.
- Fontes e licenças originais permanecem intactas. O registro `LICENSE.md` é lido, não reescrito; direitos de terceiros e subárvores exigem inspeção separada.

## Rota manual e automática
O gatilho `pull_request` é limitado aos arquivos do núcleo, workflow, script e contrato. `workflow_dispatch` disponibiliza investigação WS01 opcional; não é ligada automaticamente por PR, porque o runtime Python é hosted e o falsificador histórico pode falhar. Se o provedor não materializar Actions, estado = `TOKEN_VAZIO_PROVIDER_EXECUTION`; PR existente não prova execução.

**Etapas canônicas, cada uma fail closed:**
- **00**: identidade canônica/exact event HEAD, arquivos e licença, checagem estática anti-libc/OS.
- **10**: compilação cruzada do núcleo C para x86_64 host, ARMv7 e AArch64, usando o toolchain presente no runner.
- **20**: zero símbolos externos por objeto; auditoria classe/máquina ELF. Um `__aeabi_*` indefinido é FAIL_SOURCE_SIDE, não PASS.
- **30**: execução de vetores existentes do módulo C com harness hospedado e `claim_allowed=0`.
- **90**: recibos e SHA-256 por artefato, inclusive quando FAIL; `PASS_SCOPED` só prova este domínio.
- **WS01 opcional**: `python3 tools/rll_ws01_distance_integration_tolerance.py --write` em processo hospedado, preservando o contrato original `data/contracts/rll_ws01_distance_integration_tolerance.v1.json`. RC=2/FAIL não é suavizado. Relatório completo das linhas é anexado quando gerado. `PASS_WS01 != PHYSICAL_RLL_VALIDATION`.

## Matriz de falsificadores e classificação das lacunas
| Eixo | Falsificador objetivo | Ausência tipada | Rota |
| --- | --- | --- | --- |
| SOURCE | include libc, alocação ou chamada de SO | `FAIL_HOSTED_DEPENDENCY` | rever source-side após linha verificável |
| TOOLCHAIN | ausência de clang/nm/readelf ou target | `TOKEN_VAZIO_TOOLCHAIN` | preservar erro por alvo; não alterar física |
| ABI | objeto com `nm -u` não vazio, por ex. helper ARM32 | `FAIL_SOURCE_SIDE_UNDEFINED_SYMBOL` | reproduzir em target e corrigir dependência mínima |
| HARNESS | vetor esperado não retorna zero | `FAIL_DETERMINISTIC_VECTOR` | contraexemplo e contrato |
| RUNTIME | ARM/AArch64 objeto não foi executado no dispositivo | `MISSING_OBSERVATION_PHYSICAL_EXECUTION` | receipt físico separado |
| WS01 | `|Da-Db| > 0.001 Mpc + 1e-6|Db|` em uma linha | `FAIL_PREREGISTERED_DISTANCE_TOLERANCE` | exibir todas as linhas e método sem mudar limiar |
| ESTATÍSTICA | ausência de baseline e previsão física nova | `NOT_APPLICABLE_PROMOTION` | holdout e reprodução independente |
| PROVIDER | Actions não executou ou regras externas desconhecidas | `TOKEN_VAZIO_PROVIDER_ENFORCEMENT` | consulta de provider + run id |
| DIREITOS | licença aplicável não confirmada no artefato | `TOKEN_VAZIO_LICENSE_AUTHORITY` | titular, texto, escopo, atribuição |

Subtipos adicionais do corpus (`EMPTY_SET`, `NULL_VALUE`, `NUMERIC_ZERO`, `RESIDUE_ZERO`, `UNDEFINED`, `APPROX_ZERO`, `NO_REAL_SOLUTION`, `NOT_APPLICABLE`, `MISSING_OBSERVATION`) não são reduzidos a enums runtime novos por esta CI. O registro transversal tipado está em Papers, como **ponte de referência**, sem inclusão ou duplicação de código externo.

## Como reproduzir / evidências
```sh
# Executar na raiz de um checkout exato da branch/HEAD, em Linux com clang, nm e readelf.
sh tools/ci/rll_omega_canonical_freestanding_gate.sh
# Recibos efêmeros: artifacts/ci/rll-omega-freestanding/
# source_checksums.sha256 + object_checksums.sha256 + objetos + receipt.txt
```

Recibo só é evidência quando a execução realmente ocorre. O artefato Actions é upload da execução específica, não arquivo canônico que sobrescreve evidence histórica. Se o provider estiver desabilitado, compilar fora dele e anexar um recibo de execução independente sem declarar check GitHub verde.

**Rollback:** reverter somente os arquivos adicionais desta CI. Proibido alterar source, licenças, tolerâncias do WS01, dados reais, artefatos científicos ou workflows preexistentes para forçar verde.

## R3
- **F_ok da implementação:** contrato e gate canônico aditivos, fontes explicitadas, falsificadores definíveis, `claim_allowed=false`.
- **F_gap:** execução real do job, status de proteção/enforcement, eventual símbolo ARM32, WS01, dispositivo físico e validação científica independente permanecem condicionados aos recibos.
- **F_next:** primeira execução com exato HEAD e download dos artefatos. Se houver falha de compilação/símbolo, reproduzir o problema no source e propor hotfix mínimo em PR separado, sem afrouxar os testes.
