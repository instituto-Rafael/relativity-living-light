# Atlas 20 / Falsificadores CCC+TL × RLL × ΛCDM (2026-11-07)

**ROUTE_STATE:** DRAFT/HOLD; `claim_allowed=false`; `model_runtime=NOT_RUN`.
**Fonte de notícias:** [news_manifest_v2.json](news_manifest_v2.json) — 20 títulos preservados literalmente, datas, URLs, DOI relatado e lacunas.
**Roteador produtor:** `docs/presentation/00_START_HERE_RLL.md` → `05_CURRENT_STATE_RLL.md` → `docs/RLL_TRACEABILITY_MAP.md`.
**Autoridade:** a notícia documenta alegações e pistas, **não** comprova física; artigos revisados, dados observacionais e código executor são camadas separadas. SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM.

## Distinções que não podem regredir
- CCC+TL (Gupta / Samaras), RLL (Instituto Rafael), ΛCDM e modelo de Richard Lieu são **quatro hipóteses/famílias distintas**. Não transferir equações, parâmetros nem confirmação de uma para outra.
- Notícias de 2023, 2024, 2025 e 2026 do grupo Gupta **não são replicações independentes por multiplicidade de manchetes**.
- Lei et al. (2026), DOI `10.1093/mnras/stag430`, publicaram uma incompatibilidade de cronômetros cósmicos / SN Ia (~6σ e ΔBIC em uma análise específica). Gupta (2026), DOI `10.1093/mnras/stag1126`, apresentou correção **fenomenológica** com tensão reportada ~0,13σ. Esses números têm pressupostos diferentes: exigir física estelar/SPS autoconsistente, congelada antes do ajuste. A própria resposta não a apresenta como confirmação definitiva.
- SPARC: catálogo oficial 175 galáxias; estudo `10.1093/mnras/stag1777` usa formulação **inversa** e subamostras em etapas. Ajustes comparáveis a MOND não provam poder preditivo fora da amostra.
- SPT-3G polarização CMB (`arxiv:2411.06000`) dá suporte observacional à ΛCDM; uma cosmologia alternativa precisa prever CMB/perturbações, não só utilizar prior comprimido.
- KM3NeT/ORCA não encontrou sinal de violação de Lorentz. Isso **não** elimina automaticamente CCC+TL, nem confirma RLL; exige calcular uma previsão específica que o experimento possa medir.
- JWST Misty Moons, little red dots, LOFAR e PTA são rotas de observação/cenários, com seleção, população e astrofísica como variáveis latentes. Horizontes análogos de laboratório e dínamos planetários não constituem teste de expansão de fundo.
- Arqueologia, química de cabelos, micro-CT, gravuras e externalidades de fogos permanecem na catalogação como **métodos transversais**. Não são evidência cosmológica.

## Programa adversarial pré-registrável (ordem de valor)
| Gate | Observável | Falsificador operacional | Fronteira |
|---|---|---|---|
| F01 P0 | BBN: D/H, Yp, Li-7 | Falha de abundância após fixar ηB, rede nuclear, constantes e covariância; proibir reescala pós-hoc | 10.3390/universe12070193 |
| F02 P0 | SNe Ia + cronômetros H(z) | Não existir **um mesmo conjunto paramétrico** e SPS autoconsistente que acomode ambos | stag430 vs stag1126 |
| F03 P0 | SPT-3G EE/lensing + CMB TT/TE/EE | Modelo incapaz de fornecer previsões de perturbações e likelihood comparável | arxiv:2411.06000 |
| F04 P0 | BAO DESI radial/transversal | D_M/r_d e D_H/r_d incompatíveis sob mesma parametrização, erro e covariância | 10.3847/1538-4357/ad1bc6 |
| F05 P0 | SN dilatação temporal e cromaticidade | Componente tired-light viola duração observada e cor sem explicação física independente | arxiv:2609.10582 |
| F06 P1 | SPARC 165/175 | Predição forward/holdout não sustenta ajuste inverso, comparada com MOND/halos | 10.1093/mnras/stag1777 |
| F07 P1 | Bullet Cluster | Mapa de convergência e image-plane lensing falham frente a centroides gás/galáxias | 10.3390/universe12100308 |
| F08 P1 | Misty Moons z~11-12 | População massa-idade-SFR não reproduzida após propagação de lenteamento/AGN | 10.3847/1538-4357/ae8d09 |
| F09 P1 | JWST >z50, se dados adequados | Previsão numérica preregistrada excluída por observação com completude comprovada | **PENDING_DATA** |
| F10 P1 | Constantes fundamentais / neutrinos | Previsão quantitativa explícita excede limites adequados de laboratório/astro | ORCA só se aplicável |
| F11 P2 | PTA e LOFAR | Modelo de população SMBH / jatos com seleção não explica dados | observável condicional |
| F12 P0 | Governança científica | Leakage, ausência de priors/covariância, retuning, dados indisponíveis ou CI não reprodutível | FAIL-CLOSED |

## Contrato de execução — menor mudança reversível
1. **Congelar** equações, hashes e versões de dados dos modelos **antes** de qualquer ajuste; nenhum parâmetro CCC pode ser importado em RLL sem derivação e escopo novo.
2. Criar adapters de observáveis específicos por modelo, sem tocar baseline físico existente. Separar **interpretação do dado** da **predição do modelo**.
3. A mesma matriz de covariância observacional e política de missing-data precisa ser usada entre modelos quando realmente comparável. Documentar diferenças instrumentais onde não for.
4. Comparar likelihood/χ² e critérios penalizados **somente quando suas hipóteses de uso forem satisfeitas**, publicar resultados negativos. Dividir treino/holdout sem leakage.
5. Reproduzir em ambiente limpo, com seeds, checksums, input manifest, tabelas, gráficos e revisão independente.
6. **Promover status** apenas depois de execução real e receitp em repositório produtor; caso contrário `TOKEN_VAZIO_NOT_RUN`. Nenhum resultado científico calculado nesta PR.
7. **Rollback:** fechar PR DRAFT e descartar branch; `main` e códigos de produção permanecem intocados.

## Critérios deste patch / não critérios
- **PASS catálogo documental:** exatamente 20 manchetes, URLs distintas, fontes legíveis, 5 itens metodológicos não cosmológicos, modelo de Lieu identificado como distinto e SPT preservado como contraponte.
- **PASS conteúdo do teste** não implica PASS físico. O script de integridade só valida o catálogo.
- **PENDENTE:** validadores astronômicos de likelihood, arquivos de dados/covariância oficiais, reprodução em máquina independente, CMB completo, revisão científica/autoridade de publicação.
- **R3:** F_ok=source20 + falsificadores + limites explícitos; F_gap=execução, parâmetros, revisão independente; F_next=benchmark sombra F02/F03 com congelamento e aceitação observável. 
