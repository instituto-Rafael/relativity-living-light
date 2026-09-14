# Relativity Living Light (RLL/MCRP)

**Estado:** `REFERENCE`  
**Proprietário lógico:** `research-governance`  
**Repositório:** [`instituto-rafael/relativity-living-light`](https://github.com/instituto-rafael/relativity-living-light)

[![DOI](https://zenodo.org/badge/1046495816.svg)](https://doi.org/10.5281/zenodo.17188137)
[![License](https://img.shields.io/github/license/instituto-Rafael/relativity-living-light)](./LICENSE.md)
[![Last Commit](https://img.shields.io/github/last-commit/instituto-Rafael/relativity-living-light)](https://github.com/instituto-Rafael/relativity-living-light/commits)
[![Open Issues](https://img.shields.io/github/issues/instituto-Rafael/relativity-living-light)](https://github.com/instituto-Rafael/relativity-living-light/issues)
[![Open PRs](https://img.shields.io/github/issues-pr/instituto-Rafael/relativity-living-light)](https://github.com/instituto-Rafael/relativity-living-light/pulls)
[![Repo Size](https://img.shields.io/github/repo-size/instituto-Rafael/relativity-living-light)](https://github.com/instituto-Rafael/relativity-living-light)

> **Edição profissional (2026):** organização formal para leitura acadêmica, rastreabilidade metodológica e elegaância editorial, **sem remoção de acervo**.

---

## Pacote canônico RAFAELIA/RLL — conhecimento, publicação e validação

Este repositório inclui agora um pacote público organizado para leitura, auditoria e continuidade do trabalho RAFAELIA/RLL:

- Documento-mãe: [`docs/canonicos/BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md`](docs/canonicos/BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md)
- Epistemologia: [`docs/canonicos/13_EPISTEMOLOGIA_RAFAELIA_RLL.md`](docs/canonicos/13_EPISTEMOLOGIA_RAFAELIA_RLL.md)
- Modelo cosmológico: [`docs/canonicos/14_MODELO_COSMOLOGICO_RLL.md`](docs/canonicos/14_MODELO_COSMOLOGICO_RLL.md)
- Dados externos reais: [`docs/canonicos/15_DADOS_EXTERNOS_REAIS_RLL.md`](docs/canonicos/15_DADOS_EXTERNOS_REAIS_RLL.md)
- Pipeline de validação: [`docs/canonicos/16_PIPELINE_VALIDACAO_RLL.md`](docs/canonicos/16_PIPELINE_VALIDACAO_RLL.md)
- Onda, neuro, física e linguagem: [`docs/canonicos/17_ONDA_VERBO_FISICA_NEURO_LINGUAGEM.md`](docs/canonicos/17_ONDA_VERBO_FISICA_NEURO_LINGUAGEM.md)
- Orquestrador ASCII/UTF: [`docs/canonicos/18_ORQUESTRADOR_ASCII_UTF_RAFAELIA.md`](docs/canonicos/18_ORQUESTRADOR_ASCII_UTF_RAFAELIA.md)
- Roadmap e falsificadores: [`docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md`](docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md)
- Checklist de publicação: [`docs/canonicos/20_CHECKLIST_PUBLICACAO_RAFAELIA_RLL.md`](docs/canonicos/20_CHECKLIST_PUBLICACAO_RAFAELIA_RLL.md)
- Limite nulo e AION: [`docs/canonicos/21_LIMITE_NULO_AION_E_CANCELAMENTO_DIFERENCIAL_RLL.md`](docs/canonicos/21_LIMITE_NULO_AION_E_CANCELAMENTO_DIFERENCIAL_RLL.md)
- Modelo Vetorial Informacional (MVICS): [`docs/canonicos/21_MODELO_VETORIAL_INFORMACIONAL.md`](docs/canonicos/21_MODELO_VETORIAL_INFORMACIONAL.md)
- Detecção imperfeita e estados de prova: [`docs/canonicos/23_LOBO_DETECCAO_IMPERFEITA_E_ESTADOS_DE_PROVA.md`](docs/canonicos/23_LOBO_DETECCAO_IMPERFEITA_E_ESTADOS_DE_PROVA.md)

Regra de leitura: metáfora ilumina, mas não valida; dado, predição, cálculo e falsificador sustentam a camada científica.

---

## Workflow canônico de dados reais

O workflow canônico para execução completa, política de claims, checksums e artefatos de dados reais é [`.github/workflows/real-data-complete-execution.yml`](.github/workflows/real-data-complete-execution.yml). Workflows reais auxiliares devem declarar `CANONICAL_REAL_DATA_WORKFLOW=.github/workflows/real-data-complete-execution.yml`, herdar a fronteira contra dados sintéticos/mock/fixture/demo/example/placeholder, usar checkout sem persistência de credenciais, gerar checksums finais e publicar artefatos com `actions/upload-artifact@v4`.

## Rastreabilidade, anterioridade e cadeia de custódia

A leitura de claims do RLL/MCRP deve passar pelo mapa central de rastreabilidade antes de qualquer conclusão:

- Mapa central: [`docs/RLL_TRACEABILITY_MAP.md`](docs/RLL_TRACEABILITY_MAP.md)
- Arquitetura operacional claim-bounded: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Arquitetura segura claim-gated: [`docs/architecture/ARCHITECTURE_CLAIM_GATED.md`](docs/architecture/ARCHITECTURE_CLAIM_GATED.md)
- Registry cross-repo evidence-gated: [`docs/audits/CROSS_REPO_RELATIONSHIP_REGISTRY.md`](docs/audits/CROSS_REPO_RELATIONSHIP_REGISTRY.md)
- Auditoria da tag `v1.0.0`: [`docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md`](docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md)
- Proveniência celular/Termux: [`docs/RLL_MOBILE_TERMUX_PROVENANCE_LEDGER.md`](docs/RLL_MOBILE_TERMUX_PROVENANCE_LEDGER.md)
- Plano de documentação seguinte: [`docs/RLL_NEXT_WORK_DOCUMENTATION_PLAN.md`](docs/RLL_NEXT_WORK_DOCUMENTATION_PLAN.md)
- Auditoria textual do `1234.zip`: [`docs/RLL_1234_CHUNK_TEXT_AUDIT.md`](docs/RLL_1234_CHUNK_TEXT_AUDIT.md)

Estados permitidos para qualquer alegação:

| Estado | Uso |
|---|---|
| `VERIFIED` | lido em tag, commit, arquivo, release, resultado ou manifesto |
| `DECLARED_BY_AUTHOR` | declarado por Rafael, ainda sem prova independente no repo |
| `TOKEN_VAZIO` | evidência necessária ainda não localizada |
| `CONTRADICTION` | evidência encontrada contradiz a alegação |

Resumo seguro atual:

> A tag pública `v1.0.0` de 2025 já documenta a base RLL, incluindo formulação cosmológica, termo de superposição e observáveis planejados. As validações DESI/CPL/AICc/joint-real sãoaturações posteriores. Isso sustenta anterioridade documental/matemática da estrutura-base, mas não confirma verdade física nem vitória estatística.

Avaliação honesta de estado (julho 2026):

> **Relativity in Living Light é um programa autoral de pesquisa falsificável, com infraestrutura crescente de dados reais, CI, inventário, contratos e bloqueio de claims, ainda sem validação cosmológica forte.** Ver [`docs/AVALIACAO_HONESTA_ESTADO_ATUAL.md`](docs/AVALIACAO_HONESTA_ESTADO_ATUAL.md) para análise completa.

---

## Aviso de cronologia, DOI e prova técnica (referência 10.5281/zenodo.17188137)

- Este repositório GitHub é a trilha primária de versionamento contínuo de trabalho.
- O DOI de referência `10.5281/zenodo.17188137` foi usado para citação e preservação de artefatos após publicação de conteúdo no GitHub, compondo uma camada complementar de arquivamento científico.
- Em termos probatórios, a data exata do DOI deve ser confirmada por metadado oficial do Zenodo/DataCite quando disponível publicamente em estado *Findable*.
- Enquanto não houver metadado direto acessível, a leitura correta é: o DOI está associado ao ecossistema Zenodo e pode ser tratado como evidência de preservação/citação, sem substituir a trilha de commits do GitHub.

Para formalização adicional, consulte `docs/README_ADVERTENCIA_DOI.md`.
- Janela indiciária (não oficial) para o DOI citado: entre **11/09/2025** e **29/10/2025**, com estimativa central em **~22/09/2025**.
- Evidência direta complementar: commit/tag com assinatura **GitHub Verified** em **19/09/2025 03:58** (GPG `B5690EEEBB952194`) reforça a cronologia da trilha Git.

---

## Carta de apresentação institucional

Este repositório consolida a linha **Relativity Living Light (RLL/MCRP)** em formato de revisão acadêmico-profissional: verificável, citável, multilíngue e com governança documental, sem que isso substitua validação científica externa.

### Objetivos desta refatoração
- Preservar integralmente dados, trilhas autorais e histórico técnico.
- Elevar o padrão de forma para revisão técnica externa, bancas e colaborações internacionais.
- Conectar fundamentos matemáticos, física, cognição linguística e rotas de validação observacional com fronteiras explícitas de claim.

## Painel de governança GitHub (selos)
- **Licença e conformidade**: badge de licença + `LICENSE.md`.
- **Ritmo de manutenção**: badge de último commit.
- **Abertura colaborativa**: badges de issues e pull requests abertas.
- **Escala de acervo**: badge de tamanho do repositório para transparência operacional.

## Formalidades acadêmicas e "selos" GitHub
- **Citação científica**: `data/CITATION.cff`
- **Licença**: `LICENSE.md`
- **Template de PR**: `.github/pull_request_template.md`
- **Resumo de segurança**: `SECURITY_SUMMARY.md`
- **Pacote reprodutível (artefatos)**: `results/manifest.json`, `data/zenodo.json`

## Leitura recomendada (ordem canônica)
1. `README.md` (este documento)
2. `ARCHITECTURE.md`
3. `docs/architecture/ARCHITECTURE_CLAIM_GATED.md`
4. `docs/RLL_TRACEABILITY_MAP.md`
5. `docs/INDICE_MESTRE.md`
6. `docs/audits/CROSS_REPO_RELATIONSHIP_REGISTRY.md`
7. `docs/canonicos/BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md`
8. `docs/ACADEMIC_TAXONOMY_INDEX.md`
9. `docs/REFERENCES.md`
10. `docs/DOCUMENTATION_FULL_INVENTORY.md`

---

O RLL/MCRP passa a separar validação em três blocos: geofísico local, helioférico-radiativo e cosmológico. A AMAS/SAA é caso observacional local; DESI/Pantheon+/Planck testam a camada cosmológica.

# README — Edição Técnica Profissional (2026)

> **Status**: revisão formal com indexação semântica, rastreabilidade metodológica e atualização conceitual inspirada por práticas de ciência computacional, FAIR data, reproducibility-by-design e governança de evidência, sem substituir validação científica.

## Índice Estruturado
- [1. Escopo e finalidade](#1-escopo-e-finalidade)
- [2. Fundamentos técnico-científicos](#2-fundamentos-técnico-científicos)
- [3. Arquitetura documental e encadeamento por índices](#3-arquitetura-documental-e-encadeamento-por-índices)
- [4. Critérios de qualidade e validação](#4-critérios-de-qualidade-e-validação)
- [5. Referências bibliográficas](#5-referências-bibliográficas)
- [6. Conteúdo histórico preservado](#6-conteúdo-histórico-preservado)

## 1. Escopo e finalidade
Este arquivo foi normalizado para **uso acadêmico-profissional** com linguagem formal, clareza de auditoria e integração ao ecossistema documental do repositório. A revisão privilegia rigor epistemológico, verificabilidade, interoperabilidade e manutenção de integridade textual.

## 2. Fundamentos técnico-científicos
- **Reprodutibilidade**: processos, decisões e resultados devem ser rastreabeis.
- **Integração teoria-dados**: hipótese, modelagem, inferência e validação observacional são tratadas como pipeline com fronteiras explícitas de claim.
- **Estado da arte**: adoção de boas práticas contemporâneas de documentação técnica para pesquisa computacional e ciência de dados.

## 3. Arquitetura documental e encadeamento por índices
- Arquitetura operacional: `ARCHITECTURE.md`
- Índice mestre: `docs/INDICE_MESTRE.md`
- Mapa de rastreabilidade: `docs/RLL_TRACEABILITY_MAP.md`
- Arquitetura segura claim-gated: `docs/architecture/ARCHITECTURE_CLAIM_GATED.md`
- Registry cross-repo evidence-gated: `docs/audits/CROSS_REPO_RELATIONSHIP_REGISTRY.md`
- Inventário científico: `docs/ACADEMIC_TAXONOMY_INDEX.md`
- Referências globais: `docs/REFERENCES.md`
- Inventário documental: `docs/DOCUMENTATION_FULL_INVENTORY.md`

## 4. Critérios de qualidade e validação
1. Consistência terminológica e semântica.
2. Conectividade entre hipóteses, métodos, resultados e limitações.
3. Priorização de evidência verificável e versionamento explícito.
4. Preparação para revisão técnica externa em estilo de auditoria, sem pressupor aceitação ou validação final.

## 5. Referências bibliográficas
1. Wilkinson, M. D., et al. (2016). *The FAIR Guiding Principles for scientific data management and stewardship*. Scientific Data, 3, 160018.
2. Peng, R. D. (2011). *Reproducible Research in Computational Science*. Science, 334(6060), 1226–1227.
3. Nosek, B. A., et al. (2015). *Promoting an open research culture*. Science, 348(6242), 1422–1425.
4. Saltelli, A., et al. (2020). *Five ways to ensure that models serve society*. Nature, 582, 482–484.
5. European Commission. (2020). *Horizon 2020 Programme: Guidelines on FAIR Data Management in Horizon 2020*.

## 6. Conteúdo histórico preservado
O conteúdo original permanece abaixo para preservar trilha de auditoria e contexto evolutivo.

---
