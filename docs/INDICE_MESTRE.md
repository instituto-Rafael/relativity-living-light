# INDICE MESTRE - Documentacao Oficial
## Relativity Living Light

**Atualizado em:** 2026-06-20
**Atualizado em:** 2026-06-26
**Atualizado em:** 2026-08-08
**Regra:** secao principal lista apenas caminhos canonicos oficiais.

---

## Escopo deste arquivo

Este arquivo e a **navegacao canonica** da documentacao do repositorio.

- Lista os caminhos oficiais por trilha tematica.
- Atua como referencia de navegacao para leitura e manutencao.
- Nao substitui o README (porta de entrada) e nao tenta reproduzir o inventario bruto.

Encaminhamentos complementares:
- Porta de entrada: [`README.md`](../README.md)
- Mapa central de rastreabilidade: [`docs/RLL_TRACEABILITY_MAP.md`](RLL_TRACEABILITY_MAP.md)
- Inventario bruto (`.md` e `.zip`): [`docs/DOCUMENTATION_FULL_INVENTORY.md`](DOCUMENTATION_FULL_INVENTORY.md)
- Mapa Dark Matter/RLL: [`docs/DARKMATTER_RLL_LINK_MAP.md`](DARKMATTER_RLL_LINK_MAP.md)
- Nota Dark Matter/nome/inventario: [`docs/DARKMATTER_NAMING_AND_INVENTORY_NOTE.md`](DARKMATTER_NAMING_AND_INVENTORY_NOTE.md)
- Normatizacao de nomes: [`docs/NORMATIZACAO_NOMES_ARQUIVOS_RLL.md`](NORMATIZACAO_NOMES_ARQUIVOS_RLL.md)
- Procedimento de atualizacao: `python3 tools/docs_inventory.py` e validacao `python3 tools/docs_inventory.py --check`.

---

## Procedimento de atualizacao do inventario documental

1. Regenerar inventario completo publicado:

   ```bash
   python3 tools/docs_inventory.py
   ```

2. Validar contagem publicada vs. varredura real:

   ```bash
   python3 tools/docs_inventory.py --check
   ```

3. Confirmar no cabecalho do inventario: data/hora, commit de referencia e total.

---

## 1) Nucleo cientifico oficial

- [`README.md`](../README.md)
- [`darkmatter.md`](../darkmatter.md) - pacote de validacao cosmologica real RLL, normalizado sem espaco inicial no nome
- [`docs/Relativity_Living_Light.md`](Relativity_Living_Light.md)
- [`docs/DARKMATTER_RLL_LINK_MAP.md`](DARKMATTER_RLL_LINK_MAP.md) - mapa de links entre `darkmatter.md`, dados reais, workflows, IML, DESI/Pantheon e documentacao
- [`docs/BOOSTERS.md`](BOOSTERS.md)
- [`docs/Results.md`](Results.md)
- [`docs/RESULTADOS_CORRIGIDOS.md`](RESULTADOS_CORRIGIDOS.md)
- [`docs/COMPARACAO_DESI_2025.md`](COMPARACAO_DESI_2025.md)
- [`docs/ROADMAP_VALIDACAO.md`](ROADMAP_VALIDACAO.md)
- [`docs/PLANO_ABCD_JWST_AGN_SMBH.md`](PLANO_ABCD_JWST_AGN_SMBH.md)
- [`docs/ARQUITETURA_DUAS_RADIACOES_IMPLEMENTACAO.md`](ARQUITETURA_DUAS_RADIACOES_IMPLEMENTACAO.md)
- [`docs/MODELO_COSMOLOGICO_UNIFICADO_MAGNETISMO_RADIACAO_PLASMA.md`](MODELO_COSMOLOGICO_UNIFICADO_MAGNETISMO_RADIACAO_PLASMA.md)
- [`docs/REFERENCES.md`](REFERENCES.md)
- [`docs/FORMULAS_CANONICAS_INDEX.md`](FORMULAS_CANONICAS_INDEX.md) - referencia oficial de formulas
- [`docs/RLL_RESPONSE_MEDIUM_EQUATIONS.md`](RLL_RESPONSE_MEDIUM_EQUATIONS.md)
- [`docs/RLL_STATISTICAL_FINANCIAL_METRICS.md`](RLL_STATISTICAL_FINANCIAL_METRICS.md)
- [`docs/rll_latentes/README.md`](rll_latentes/README.md) - formalismo RLL-LATENTES para triagem falsificável de sementes ignoradas
- [`docs/rll_latentes/RAW_TEXT_FIRST.md`](rll_latentes/RAW_TEXT_FIRST.md) - protocolo canônico para preservar texto bruto antes de claims, vetores, métricas, inferência e prova
- [`docs/rll_latentes/FUTURE_STEPS.md`](rll_latentes/FUTURE_STEPS.md) - sete passos futuros integrados para pipeline, failover, rollback, validação e release
- [`data/rll_latentes/observations.yml`](../data/rll_latentes/observations.yml) - catálogo YAML de fontes recentes, caminhos de pipeline e controles de rollback
- [`schemas/rll_latentes_observations.schema.json`](../schemas/rll_latentes_observations.schema.json) - schema estrutural do catálogo RLL-LATENTES
- [`src/rll/latentes.py`](../src/rll/latentes.py) - implementação determinística da validação, score, dry-run, Merkle e relatórios RLL-LATENTES
- [`docs/RLL_CLAIM_BOUNDARIES.md`](RLL_CLAIM_BOUNDARIES.md)
- [`docs/CONVERGENCIAS_INDEPENDENTES_RAFAELIA_RLL.md`](CONVERGENCIAS_INDEPENDENTES_RAFAELIA_RLL.md) - registro mestre 3->8->9 de convergências independentes, com matriz e claim gate
- [`docs/CONVERGENCIA_ETH_HLS_TRANSICOES_FASE.md`](CONVERGENCIA_ETH_HLS_TRANSICOES_FASE.md) - convergência independente ETH/HLS para ruído-dissipação como variável de estado, sem promoção automática de claim
- [`docs/C09_TRANSMUTACAO_NUCLEAR_CHRYSOPOEIA_MAPA_ROTAS.md`](C09_TRANSMUTACAO_NUCLEAR_CHRYSOPOEIA_MAPA_ROTAS.md) - C09 candidata: transmutação nuclear/chrysopoeia via nêutrons de fusão, mapa de rotas e pendências
- [`docs/RLL_PRE_MOVEMENT_SCALE_BRIDGE.md`](RLL_PRE_MOVEMENT_SCALE_BRIDGE.md) - ponte de escala para pre-movimento, impactos vetoriais, memoria dinamica e limites de promocao cosmologica
- [`rll_equation_registry.yml`](../rll_equation_registry.yml)

## 1.1) Casos observacionais

- [`docs/cases/OBSERVATIONAL_ASTROPHYSICAL_CASES_INDEX.md`](cases/OBSERVATIONAL_ASTROPHYSICAL_CASES_INDEX.md)
- [`docs/cases/AMAS_SOUTH_ATLANTIC_MAGNETIC_ANOMALY_RLL.md`](cases/AMAS_SOUTH_ATLANTIC_MAGNETIC_ANOMALY_RLL.md)
- [`docs/cases/SN2017egm_SUPERLUMINOUS_SUPERNOVA_MAGNETAR_ENGINE_RLL.md`](cases/SN2017egm_SUPERLUMINOUS_SUPERNOVA_MAGNETAR_ENGINE_RLL.md)

## 2) Governanca, organizacao e auditoria

- [`docs/DOCUMENTATION_ORGANIZATION_MASTER.md`](DOCUMENTATION_ORGANIZATION_MASTER.md)
- [`docs/RLL_TRACEABILITY_MAP.md`](RLL_TRACEABILITY_MAP.md) - mapa central: cada claim/artifacto aponta para seu documento, status e proxima prova
- [`docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md`](RLL_V1_TAG_ANCESTRALITY_AUDIT.md) - auditoria da tag `v1.0.0`, anterioridade da formula e observaveis
- [`docs/RLL_MOBILE_TERMUX_PROVENANCE_LEDGER.md`](RLL_MOBILE_TERMUX_PROVENANCE_LEDGER.md) - ledger de proveniencia celular/Termux e estados VERIFIED/DECLARED/TOKEN_VAZIO
- [`docs/RLL_NEXT_WORK_DOCUMENTATION_PLAN.md`](RLL_NEXT_WORK_DOCUMENTATION_PLAN.md) - plano operacional para inventario da tag, imagens, CSVs, estacoes de dados e non-post-hoc
- [`docs/RLL_1234_CHUNK_TEXT_AUDIT.md`](RLL_1234_CHUNK_TEXT_AUDIT.md) - auditoria textual dos chunks do `1234.zip`
- [`docs/governance/OPERATIONAL_EXCELLENCE_EXECUTION_FRAMEWORK.md`](governance/OPERATIONAL_EXCELLENCE_EXECUTION_FRAMEWORK.md) - framework de execucao para excelencia operacional, governanca continua, auditoria e pipelines
- [`docs/governance/RLL_OBSERVATIONAL_TOPOLOGY_20260808_V1.md`](governance/RLL_OBSERVATIONAL_TOPOLOGY_20260808_V1.md) - topologia append-only, fail-closed e de dependencias para dados cosmologicos/propagacao
- [`docs/governance/RLL_VECTRAS_SQRT3_2_GOVERNANCE_MATRIX.md`](governance/RLL_VECTRAS_SQRT3_2_GOVERNANCE_MATRIX.md) - matriz de governanca RLL ↔ Vectras ↔ sqrt3_2: separacao de responsabilidades, fricoes, guardas epistemologicas e criterios de decisao para PRs
- [`docs/CANONICAL_SOURCES.md`](CANONICAL_SOURCES.md)
- [`docs/POLITICA_REPOSITORIO_TEXTO_E_ARTEFATOS.md`](POLITICA_REPOSITORIO_TEXTO_E_ARTEFATOS.md) **(fonte oficial para formatos no core e publicacao de artefatos externos)**
- [`docs/RAFAELIA_REGIME_INDEX.md`](RAFAELIA_REGIME_INDEX.md) **(classificacao de regimes: formula, hipotese, dado, validacao, legado e simbolico)**
- [`docs/RELEASE_NOTES_HISTORY.md`](RELEASE_NOTES_HISTORY.md)
- [`docs/DOCUMENTATION_FULL_INVENTORY.md`](DOCUMENTATION_FULL_INVENTORY.md)
- [`docs/ZIP_CONTENT_INDEX.md`](ZIP_CONTENT_INDEX.md) *(inventario historico; nao normativo para armazenamento no core)*
- [`docs/DATA_INTEGRITY_CHECKLIST.md`](DATA_INTEGRITY_CHECKLIST.md)
- [`docs/AVALIACAO_HONESTA_ESTADO_ATUAL.md`](AVALIACAO_HONESTA_ESTADO_ATUAL.md) - avaliação honesta do estado atual: o que é forte, o que não está forte, próximos saltos necessários (issue #484)
- [`docs/ADMIN.md`](ADMIN.md)
- [`docs/AUDITORIA_DOCUMENTAL_E_DIRETORIOS_2026-03-05.md`](AUDITORIA_DOCUMENTAL_E_DIRETORIOS_2026-03-05.md)
- [`docs/NORMATIZACAO_NOMES_ARQUIVOS_RLL.md`](NORMATIZACAO_NOMES_ARQUIVOS_RLL.md) - regras para nomes de arquivos, normalizacao e contagens
- [`docs/DARKMATTER_NAMING_AND_INVENTORY_NOTE.md`](DARKMATTER_NAMING_AND_INVENTORY_NOTE.md) - explicacao do caso `darkmatter.md`, divergencias 308/335/368/388 e caminho canonico

## 3) Serie canonica consolidada (`docs/canonicos/`)

- [`docs/canonicos/00_COMO_LER.md`](canonicos/00_COMO_LER.md)
- [`docs/canonicos/06_COMPARACOES_DETALHADAS.md`](canonicos/06_COMPARACOES_DETALHADAS.md)
- [`docs/canonicos/09_GLOSSARIO_COMPLETO.md`](canonicos/09_GLOSSARIO_COMPLETO.md)
- [`docs/canonicos/10_FAQ_COMPLETO.md`](canonicos/10_FAQ_COMPLETO.md)
- [`docs/canonicos/11_DOCUMENTO_PRIORIDADE.md`](canonicos/11_DOCUMENTO_PRIORIDADE.md)
- [`docs/canonicos/12_DOCUMENTO_CANONICO_RLL_PREPRINT_PTBR.md`](canonicos/12_DOCUMENTO_CANONICO_RLL_PREPRINT_PTBR.md)

### 3.1) Pacote RAFAELIA/RLL de conhecimento, publicacao e validacao

- [`docs/canonicos/BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md`](canonicos/BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md) - documento-mae consolidado
- [`docs/canonicos/13_EPISTEMOLOGIA_RAFAELIA_RLL.md`](canonicos/13_EPISTEMOLOGIA_RAFAELIA_RLL.md) - sistema [E]/[C]/[H]/[VAZIO], RAW_TEXT_FIRST e integridade epistemica
- [`docs/canonicos/14_MODELO_COSMOLOGICO_RLL.md`](canonicos/14_MODELO_COSMOLOGICO_RLL.md) - equacao-mae, limite nulo, EoS efetiva, adversario w0waCDM e falsificadores
- [`docs/canonicos/15_DADOS_EXTERNOS_REAIS_RLL.md`](canonicos/15_DADOS_EXTERNOS_REAIS_RLL.md) - DESI, CMB, H(z), fσ8, metricas e pendencias
- [`docs/canonicos/16_PIPELINE_VALIDACAO_RLL.md`](canonicos/16_PIPELINE_VALIDACAO_RLL.md) - estrutura executavel, funcoes-nucleo e reprodutibilidade
- [`docs/canonicos/17_ONDA_VERBO_FISICA_NEURO_LINGUAGEM.md`](canonicos/17_ONDA_VERBO_FISICA_NEURO_LINGUAGEM.md) - som, onda, neuro, linguagem, metafora e limites
- [`docs/canonicos/18_ORQUESTRADOR_ASCII_UTF_RAFAELIA.md`](canonicos/18_ORQUESTRADOR_ASCII_UTF_RAFAELIA.md) - matriz ASCII/UTF, hashes, C_eff e TOKEN_VAZIO
- [`docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md`](canonicos/19_ROADMAP_FALSIFICADORES_RLL.md) - roadmap de testes e criterios de falsificacao
- [`docs/canonicos/20_CHECKLIST_PUBLICACAO_RAFAELIA_RLL.md`](canonicos/20_CHECKLIST_PUBLICACAO_RAFAELIA_RLL.md) - checklist publico de documentos, governanca, seguranca e citabilidade
- [`docs/canonicos/21_LIMITE_NULO_AION_E_CANCELAMENTO_DIFERENCIAL_RLL.md`](canonicos/21_LIMITE_NULO_AION_E_CANCELAMENTO_DIFERENCIAL_RLL.md) - limite nulo `Ωs0=0`, degenerescencia com ΛCDM e analogia metodologica com AION
- [`docs/canonicos/21_MODELO_VETORIAL_INFORMACIONAL.md`](canonicos/21_MODELO_VETORIAL_INFORMACIONAL.md) - vetor V_info tipado, equacao de observacao (F_prop/F_med/T), FSM com falsificadores Popper, Fisher/Shannon, integracao claim_state

---

## 4) Validacao observacional e matriz de dados reais

- [`docs/DARKMATTER_RLL_LINK_MAP.md`](DARKMATTER_RLL_LINK_MAP.md) - links de validacao cosmologica real: DESI, Pantheon, CMB, H(z), fσ8, ZML e workflows
- [`docs/VALIDATION_DATA_MATRIX_RLL_MCRP.md`](VALIDATION_DATA_MATRIX_RLL_MCRP.md)
- [`data/governance/RLL_OBSERVATIONAL_TOPOLOGY_20260808_V1.json`](../data/governance/RLL_OBSERVATIONAL_TOPOLOGY_20260808_V1.json) - registro executavel da topologia e dos gates de promocao
- [`docs/cases/OBSERVATIONAL_ASTROPHYSICAL_CASES_INDEX.md`](cases/OBSERVATIONAL_ASTROPHYSICAL_CASES_INDEX.md)
- [`docs/cases/AMAS_SOUTH_ATLANTIC_MAGNETIC_ANOMALY_RLL.md`](cases/AMAS_SOUTH_ATLANTIC_MAGNETIC_ANOMALY_RLL.md)
- [`docs/cases/SN2017egm_SUPERLUMINOUS_SUPERNOVA_MAGNETAR_ENGINE_RLL.md`](cases/SN2017egm_SUPERLUMINOUS_SUPERNOVA_MAGNETAR_ENGINE_RLL.md)
- [`docs/pipelines/GEOMAGNETIC_VALIDATION_PIPELINE.md`](pipelines/GEOMAGNETIC_VALIDATION_PIPELINE.md)
- [`docs/pipelines/RADIATION_TRANSMISSION_VALIDATION.md`](pipelines/RADIATION_TRANSMISSION_VALIDATION.md)
- [`docs/pipelines/COSMOLOGY_VALIDATION_STACK.md`](pipelines/COSMOLOGY_VALIDATION_STACK.md)

---

## Arquivo/Legacy

> Materiais abaixo sao preservados por historico/rastreabilidade e **nao** sao a fonte oficial.

### Duplicatas historicas da serie canonica
- Duplicatas historicas mantidas para rastreabilidade (raiz, `RMR/` e `news/archive_legacy/`).
- Fonte official unica para consulta e citacao:
  - [`docs/canonicos/00_COMO_LER.md`](canonicos/00_COMO_LER.md)
  - [`docs/canonicos/06_COMPARACOES_DETALHADAS.md`](canonicos/06_COMPARACOES_DETALHADAS.md)

- `docs/canonicos/23_LOBO_DETECCAO_IMPERFEITA_E_ESTADOS_DE_PROVA.md` — detecção imperfeita, fadiga, falsificação e estados de prova.
