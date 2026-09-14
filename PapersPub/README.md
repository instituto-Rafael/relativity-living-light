# PapersPub — Índice Padronizado de Papers Publicáveis

`PapersPub/` organiza trilhas de manuscritos para cosmologia, geofísica, heliosfera e métodos formais sem mover documentos legados. A migração de conteúdo existente só deve ocorrer depois de registrada em `data_manifest.md`, `reproducibility.md` e, quando aplicável, no índice desta pasta.

## Escopo

- Consolidar propostas de papers em diretórios numerados e auditáveis.
- Separar hipóteses conceituais, dados sintéticos, dados reais parciais e resultados prontos para revisão.
- Preservar rastreabilidade para materiais em `RAFAELIA_COSMO_STRUCTURE_D/paper/`, `newadd/` e `docs/`.
- Manter cosmologia, geofísica, heliosfera e métodos formais em trilhas distintas para evitar extrapolações entre domínios.

## Critérios de inclusão

Um paper entra em `PapersPub/` somente se tiver:

1. `draft.md` com objetivo, escopo, claims permitidas e claims proibidas.
2. `references.bib` ou `references.md` com referências externas e internas rastreáveis.
3. `figures/` para figuras geradas ou planejadas, com origem documentada.
4. `data_manifest.md` com datasets, artefatos, caminhos existentes e lacunas.
5. `reproducibility.md` com comandos, ambiente, testes, fail-safe, failover e rollback.

## Status científico

Use um dos status abaixo em cada trilha:

| Status | Significado |
|---|---|
| `planned` | Ideia estruturada; dados e análise ainda não executados no pacote do paper. |
| `data_ingested` | Dados ou artefatos foram identificados/ingeridos com rastreabilidade. |
| `analysis_run` | Análise executada; resultados ainda em auditoria. |
| `review_ready` | Manuscrito e evidências prontos para revisão interna. |
| `submitted` | Submetido a periódico, preprint server ou conferência. |

## Regra de claims e superioridade

Não declarar superioridade científica, técnica ou estatística sobre ΛCDM, modelos geofísicos, heliosféricos, computacionais ou qualquer baseline sem métricas reais, comparáveis e reprodutíveis. Claims devem indicar explicitamente se são conceituais, exatas, convencionais, hipotéticas, parabólicas, sintéticas, parciais reais ou reais validadas. Sempre reportar métricas negativas, limitações, falhas, vieses, critérios de falsificação e penalizações por complexidade quando existirem.

## Regra de migração sem duplicação

- Não mover nem copiar documentos legados antes de registrar a migração.
- Referenciar caminhos existentes quando bastar rastreabilidade.
- Se duplicação for inevitável, registrar origem, motivo, data, diferença esperada e plano de reconciliação.
- Materiais existentes em `RAFAELIA_COSMO_STRUCTURE_D/paper/`, `newadd/` e `docs/` são fontes, não substitutos automáticos do paper final.
- Papers canônicos devem permanecer em uma única trilha; repositórios irmãos recebem somente pontes de escopo/proveniência quando necessário.

## Índice resumido

| Nº | Diretório | Tema | Status |
|---:|---|---|---|
| 01 | [`01_cosmology_pantheon_desi/`](01_cosmology_pantheon_desi/) | Cosmologia Pantheon+/DESI | `planned` |
| 02 | [`02_cosmology_growth_structure_d/`](02_cosmology_growth_structure_d/) | Crescimento Estrutural e Structure D | `planned` |
| 03 | [`03_cosmology_magnetic_plasma/`](03_cosmology_magnetic_plasma/) | Magnetismo, Plasma e Radiação Cosmológica | `planned` |
| 04 | [`04_geophysics_geomagnetic_anomaly/`](04_geophysics_geomagnetic_anomaly/) | Geofísica: Anomalias Geomagnéticas | `planned` |
| 05 | [`05_geophysics_earth_observation/`](05_geophysics_earth_observation/) | Geofísica: Observação Terrestre e Resiliência | `planned` |
| 06 | [`06_heliosphere_solar_wind/`](06_heliosphere_solar_wind/) | Heliosfera: Vento Solar e Plasma | `planned` |
| 07 | [`07_heliosphere_radiation_transmission/`](07_heliosphere_radiation_transmission/) | Heliosfera: Transmissão de Radiação | `planned` |
| 08 | [`08_multiscale_validation_methods/`](08_multiscale_validation_methods/) | Formalismo epistemológico-computacional 7D, 42 hiperformas, tensores, grafos e validação | `analysis_run` |
| 09 | [`09_language_entropy_formalism/`](09_language_entropy_formalism/) | Formalismo de Linguagem, Entropia e Metáforas | `planned` |
| 10 | [`10_lowlevel_reproducibility_kernels/`](10_lowlevel_reproducibility_kernels/) | Kernels e Reprodutibilidade Low-Level | `planned` |

A trilha 08 contém 44 verificações exatas reproduzidas e preserva `claim_allowed=false` para alegações físicas, causais e criptográficas.

Consulte `INDEX.md` para o índice expandido com links de rastreabilidade por trilha.
