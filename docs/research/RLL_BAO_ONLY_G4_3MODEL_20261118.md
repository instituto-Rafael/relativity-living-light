# DESI DR2 BAO-only — execução independente G4, RLL × ΛCDM × wCDM (2026-11-18)

**Estado:** REVIEW_ONLY / BAO_ONLY_SYNTHETIC_SOURCE_ADAPTER_PASS_SCOPED / PROVIDER_EXACT_HEAD_NOT_RUN_AT_CREATION / \`claim_allowed=false\`.

## Fonte de autoridade
- Produtor: \`instituto-Rafael/relativity-living-light\`, base \`rll/lab@f83f6173cb98fc785935da35afe4b31c609f1744\`
- Equações: \`tools/run_g4_background_tournament.py\` (G4); o executor apenas usa seu \`e2\`.
- Dados: \`data/real/cosmology/desi_dr2_bao_primary_points.csv\` (13 coordenadas; blob \`f6d05ead6fef7fea663eff8b31bc2c337dc30435\`), matriz \`data/real/desi_dr2_bao_covariance.csv\` (13×13; blob \`e01d0235a2f0e61d81af0c36a7338953f845f5c3\`). O carregador G4 valida ordem dos elementos e hashes das entradas; nenhuma tabela observacional foi duplicada no executor.
- Parâmetro livre BAO-only \`q=c/(H0*r_d)\`, além de \`Omega_m\` e extensões. Dados BAO isolados não estimam H0 nem r_d separadamente.

## Primeiro ensaio local independente (transcrição auditável)

| Modelo | n | k | min χ² | AICc | BIC |
| --- | ---: | ---: | ---: | ---: | ---: |
| ΛCDM | 13 | 2 | 10.90298739 | 16.10298739 | 16.03288610 |
| wCDM | 13 | 3 | 7.46726123 | 16.13392790 | 15.16210930 |
| RLL | 13 | 5 | 6.47422916 | 25.04565773 | 19.29897595 |

AICc: ΛCDM e wCDM quase empatam, RLL penalizado pela complexidade. Menor χ² do RLL não prova superioridade física; seus parâmetros \`Omega_m=0.10\` e \`w_t=0.05\` ficaram nas fronteiras estabelecidas. Null checks \`w=-1\` e \`Omega_s0=0\` = 0. Modelos usam \`Omega_r=9e-5\` e geometria FLRW plana G4.

## Falsificação e sensibilidade

- Refits BAO-only removendo cada um dos sete tracers: em 7/7 subconjuntos RLL não foi escolhido por AICc (ΛCDM 6; wCDM 1); não tratar como sete estudos independentes.
- Relaxar experimentalmente os limites de \`Omega_m\` e \`w_t\` permite min χ² de 6.4742 chegar a 5.4093; ainda no limite de matéria. Essa sensibilidade invalida a inferência física forte da região ótima BAO-only.
- Fonte original G4 Pantheon+ \`STAT+SYS\` ~33 MB não está no checkout/versionamento atual. **Não usar diagonal como se fosse covariância completa.**
- O novo script depende de fonte local G4 e usa \`g4.load_desi()\`; o ensaio local reproduziu os valores por um adaptador sintético correspondente à fonte. **CI real de HEAD e reprodução externa ainda devem ser observadas.**

## Executar sem sobrescrever resultados existentes

\`\`\`sh
OPENBLAS_NUM_THREADS=1 python scripts/run_bao_only_from_g4_v1.py --starts-extra 18 --output artifacts/evidence/bao_only_g4_3model_$(date -u +%Y%m%dT%H%M%SZ).json
\`\`\`

O script falha quando o destino já existe; \`python -m pytest -q tests/test_bao_only_g4_v1.py\` exige os 13 pontos e matriz completos na ordem canônica.

## Próximo gate científico
Materializar e verificar \`Pantheon+SH0ES_STAT+SYS.cov\` por hash/tamanho/dimensão; então executar **G4 completo** com SN+BAO+CC na mesma seleção, nuisance profile e parâmetros/priors justos, em vários seeds. Manter separados G4 e ajuste legado de 64 pontos com growth/CMB aproximados.

\`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM\`; \`claim_allowed=false\`. Sem merge nem mudança na main.
