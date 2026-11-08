# RLL — Atlas de hipóteses, teses e teorias falsificáveis (V1)

**Estado:** `CANDIDATE_ATLAS_CONSERVATIVE`, `claim_allowed=false`, `merge_allowed=false`. Não altera modelos, likelihood, workflows, claims, parâmetros, resultados anteriores, nem o registro `rll_falsifier_bundle.json`.

**Rota:** `FALSIFIABILITY_PROTOCOL.md` → `data/contracts/rll_falsifier_bundle.json` → `data/contracts/rll_epistemic_evidence_graph.v1.json` → este índice. Fonte canônica do produtor `instituto-Rafael/relativity-living-light`.

## Taxonomia

- **TEOREMA / DEMONSTRAÇÃO:** contraexemplo lógico somente dentro de hipóteses declaradas; não se testa uma igualdade euclidiana por telescópio.
- **HIPÓTESE EMPÍRICA / TEORIA FÍSICA:** define observável, escala, unidade, modelo concorrente, likelihood, covariance, falsificador e janela temporal.
- **CONTRAPROVA RESTRITA:** falha de critério em condições específicas; não faz automaticamente falsa toda uma família de modelos.
- **TOKEN_VAZIO:** inexistência de experimento/contrato suficiente; não é resultado zero nem evidência negativa.

## Registro de 27 proposições e critérios de rejeição

| ID | Domínio | Proposição condensada | Estado atual | Prioridade |
|---|---|---|---|---|
| F-MAT-01 | MATEMATICA | Se q=√3/2<1, uma recorrência afim com q tem órbita exata não estacionária de período 42. | `PROPOSICAO_CONTRADITA_MATEMATICAMENTE` | P0 |
| F-MAT-02 | MATEMATICA | Para quadrado euclidiano de lado a, diagonal=a√2. | `DEMONSTRADO_SOB_AXIOMAS` | P2 |
| F-MAT-03 | MATEMATICA | 7 escalado por 10 torna-se 70 e 3 por 10 torna-se 30, preservando soma 100; portanto 7 deixou de ser primo. | `CONCLUSAO_FALSA` | P1 |
| F-MAT-04 | MATEMATICA | 42 índices/combinações da geometria T7 correspondem a 42 atratores físicos distintos. | `TOKEN_VAZIO_ATRATORES` | P1 |
| F-MAT-05 | MATEMATICA | Os números 7,35,50,70 compartilham momento angular físico ao alternar bases 7,10,14. | `TOKEN_VAZIO_MAPA_ANGULAR` | P2 |
| F-CMP-01 | CODIFICACAO | Usar 5 bits por código sempre reduz o tamanho total em relação a Braille 6 bits. | `CONTRAPROVA_AMOSTRAL` | P0 |
| F-CMP-02 | CODIFICACAO | Maior redução percentual por compressor sempre corresponde a menor arquivo final. | `CONTRAPROVA_AMOSTRAL` | P0 |
| F-CMP-03 | CODIFICACAO | Uma tabela de 5 bits adaptativa à frequência do português supera todas as representações em bytes comprimidos incluindo dicionário e decodificador. | `TOKEN_VAZIO_HOLDOUT` | P1 |
| F-CMP-04 | CODIFICACAO | Transcritor Braille básico preserva qualquer texto português real sem perda e sem adaptação. | `TOKEN_VAZIO_COBERTURA` | P1 |
| F-STB-01 | ESTABILIDADE | O potencial V_t=Σw_i(t)[1−cos(θ_i−a_i(t))] nunca aumenta com atrator e pesos variáveis. | `CONTRAPROVA_SINTETICA` | P0 |
| F-STB-02 | ESTABILIDADE | A geometria dinâmica T7 melhora a previsão observacional fora da amostra contra um modelo físico sem T7. | `TOKEN_VAZIO_REAL_DATA` | P0 |
| F-STB-03 | ESTABILIDADE | Baixa entropia ou baixo desvio padrão em uma codificação demonstra estabilidade física de uma órbita. | `CONCLUSAO_NAO_IMPLICADA` | P1 |
| F-OBS-01 | ASTROFISICA | Uma margem do tipo estoque de segurança B=zσpred mantém cobertura nominal para séries astronômicas heterocedásticas e autocorrelacionadas. | `TOKEN_VAZIO_COBERTURA` | P0 |
| F-OBS-02 | ASTROFISICA | Tendência linear na velocidade radial isolada prova decaimento de uma órbita. | `IMPLICACAO_FALSA` | P1 |
| F-OBS-03 | ASTROFISICA | Espectroscopia + astrometria + lentes produzem massa/gravitacão mais bem calibradas que qualquer canal isolado. | `TOKEN_VAZIO_INFERENCIA` | P1 |
| F-OBS-04 | ASTROFISICA | Uma assistência gravitacional sem propulsão sempre aumenta a velocidade heliocêntrica da nave. | `CONTRAEXEMPLO_FISICO` | P1 |
| F-OBS-05 | ASTROFISICA | A Voyager cruzou o limite externo da Via Láctea ao atravessar a heliopausa. | `FALSO_IDENTIFICACAO_DE_ESCALA` | P2 |
| F-COS-01 | COSMOLOGIA | No conjunto conjunto FASE20, RLL não é substancialmente penalizado frente ao ΛCDM: ln B10 > -5. | `FAIL_EXISTENTE_F_COS_04` | P0 |
| F-COS-02 | COSMOLOGIA | O parâmetro de transição z_t do ajuste conjunto pertence a [0,5;1,5]. | `FAIL_EXISTENTE_F_COS_03` | P0 |
| F-COS-03 | COSMOLOGIA | RLL supera ΛCDM ao prever BAO DESI DR2, Pantheon+ e cronômetros, com mesma seleção/covariância e penalização. | `TOKEN_VAZIO_G4_G5_COMPLETO` | P0 |
| F-COS-04 | COSMOLOGIA | wCDM/CPL com energia escura dinâmica predizem os mesmos observáveis melhor que ΛCDM após a penalização de liberdade extra. | `TOKEN_VAZIO_COMPARACAO_CONJUNTA` | P1 |
| F-COS-05 | COSMOLOGIA | RLL prevê CMB e crescimento de estruturas sem prescrição de perturbações diferente por modelo. | `TOKEN_VAZIO_PERTURBACOES` | P0 |
| F-COS-06 | COSMOLOGIA | Um modelo CCC+TL sem energia/matéria escura explica simultaneamente BBN, CMB, BAO, supernovas e formação de estrutura melhor que ΛCDM. | `TOKEN_VAZIO_MULTIPROBE` | P2 |
| F-BIO-01 | BIOLOGIA | Melanina converte energia de radiação ionizante em produção metabólica útil com rendimento quantitativo mensurável. | `TOKEN_VAZIO_ENERGY_YIELD` | P1 |
| F-BIO-02 | BIOLOGIA | Células comuns emitem raios X triboluminescentes e os utilizam como fonte de energia metabólica. | `BLOCKED_NO_EVIDENCE` | P1 |
| F-BIO-03 | BIOLOGIA | Modelo de fluxos N/P/S e redox prevê fisiologia melhor que modelo de estoques de carbono/ATP. | `TOKEN_VAZIO_HOLDOUT_BIO` | P1 |
| F-EPI-01 | EPISTEMOLOGIA | Duas notícias, um DOI e um dataset reanalisado são três evidências observacionais independentes. | `CONCLUSAO_ERRADA_SE_MESMA_FONTE` | P0 |

## Contraprova ou ensaio exigido para cada ID

### F-MAT-01 — DEMONSTRACAO
**Falsificador:** Deduzir x_(n+42)−x* = q^42(x_n−x*) e verificar q^42≠1; toda órbita periódica finita tem de ser o ponto fixo.
**Autoridade/referência:** `PapersPub/08_multiscale_validation_methods/prime_scale_falsifiable_subset_20260915.md`. **Classificação:** `FORMAL_COUNTEREXAMPLE`.

### F-MAT-02 — TEOREMA
**Falsificador:** Contraexemplo só seria válido respeitando as mesmas hipóteses euclidianas; não há falsificação observacional genérica.
**Autoridade/referência:** `data/contracts/rll_epistemic_evidence_graph.v1.json`. **Classificação:** `FORMAL_THEOREM`.

### F-MAT-03 — IDENTIDADE_VS_INFERENCIA
**Falsificador:** A aritmética 70+30=100 é correta; 7 continua primo. Escalonar não é equivalência geral entre Z/10Z e Z/100Z nem transforma a primalidade de 7.
**Autoridade/referência:** `PapersPub/08_multiscale_validation_methods/prime_scale_falsifiable_subset_20260915.md`. **Classificação:** `NOT_EQUIVALENT`.

### F-MAT-04 — HIPOTESE_FISICA
**Falsificador:** Registrar mapa bem-definido T7, jacobiano, bacias de atração disjuntas e robustez a ruído; rejeitar se não houver 42 bacias reproduzíveis.
**Autoridade/referência:** `PapersPub/08_multiscale_validation_methods/prime_scale_falsifiable_subset_20260915.md`. **Classificação:** `NOT_RUN`.

### F-MAT-05 — HIPOTESE_GEOMETRICA
**Falsificador:** Definir referencial, unidade, função de projeção de dígitos em ângulo e invariante; contraprova com qualquer elemento que mude sob transformação declarada.
**Autoridade/referência:** `data/contracts/geodesic_numeral_projection_v1.json`. **Classificação:** `NOT_RUN`.

### F-CMP-01 — HIPOTESE_UNIVERSAL
**Falsificador:** Comparar o mesmo texto, 5 janelas semânticas, escapes/shifts e cabeçalhos incluídos; corpus RLL: 5bit próprio 1016 B versus Braille6 984 B (bruto).
**Autoridade/referência:** `NOVOexport/LOW_LEVEL_TEXT_ENCODING/TELEX_5BIT_FIXED_WINDOW_20261108/README.md`. **Classificação:** `COUNTEREXAMPLE_SCOPED`.

### F-CMP-02 — HIPOTESE_UNIVERSAL
**Falsificador:** RLL: Braille Unicode reduz 66,276% mas termina 1296 B; português UTF8 reduz 27,531% e termina 945 B em janelas equivalentes.
**Autoridade/referência:** `NOVOexport/LOW_LEVEL_TEXT_ENCODING/BRAILLE_FIXED_WINDOW_20261108/README.md`. **Classificação:** `COUNTEREXAMPLE_SCOPED`.

### F-CMP-03 — HIPOTESE_EXPERIMENTAL
**Falsificador:** Treinar tabela apenas no conjunto de treino, usar corpus de teste separado e contabilizar tabela, escapes, índices, decoder e cabeçalhos; não vence se bytes totais ≥ baseline.
**Autoridade/referência:** `NOVOexport/LOW_LEVEL_TEXT_ENCODING/TELEX_5BIT_FIXED_WINDOW_20261108/README.md`. **Classificação:** `NOT_RUN`.

### F-CMP-04 — HIPOTESE_EXPERIMENTAL
**Falsificador:** Corpus com caracteres fora do subconjunto e controle editorial: falsifica a universalidade caso falhe roundtrip ou fidelidade à norma Braille.
**Autoridade/referência:** `NOVOexport/LOW_LEVEL_TEXT_ENCODING/BRAILLE_FIXED_WINDOW_20261108/README.md`. **Classificação:** `NOT_RUN`.

### F-STB-01 — HIPOTESE_DINAMICA
**Falsificador:** Perturbação de referência ou choque nos pesos com mesmo estado: ΔV_t positivo refuta monotonicidade universal; derivar condições de drift para proposição restrita.
**Autoridade/referência:** `data/contracts/rll_entropy_dispersion_stability.v1.json`. **Classificação:** `COUNTEREXAMPLE_SYNTHETIC`.

### F-STB-02 — HIPOTESE_PREDITIVA
**Falsificador:** Pré-registrar variáveis, baseline orbital/gravitacional, janela temporal independente, métricas e penalização da complexidade; rejeitar ganho se intervalo de melhora inclui zero.
**Autoridade/referência:** `data/contracts/rll_entropy_dispersion_stability.v1.json`. **Classificação:** `NOT_RUN`.

### F-STB-03 — HIPOTESE_UNIVERSAL
**Falsificador:** Produzir dados de órbita caótica/sistema dinâmico não estacionário com codificação altamente comprimível ou medidas constantes insuficientes; sem ligação entre observáveis e física não há inferência.
**Autoridade/referência:** `data/contracts/rll_entropy_dispersion_stability.v1.json`. **Classificação:** `LOGICAL_NONSEQUITUR`.

### F-OBS-01 — HIPOTESE_ESTATISTICA
**Falsificador:** Pré-registrar taxa de alertas e confiabilidade, testar em holdout por época/instrumento com covariância temporal; falsificar se cobertura empírica inferior ao alvo fora do IC.
**Autoridade/referência:** `data/contracts/rll_entropy_dispersion_stability.v1.json`. **Classificação:** `NOT_RUN`.

### F-OBS-02 — TESE_CAUSAL
**Falsificador:** Contramodelos de órbita excêntrica periódica, companheiro, precessão, referência e viés instrumental podem gerar tendência sem da/dt<0.
**Autoridade/referência:** `FALSIFIABILITY_PROTOCOL.md`. **Classificação:** `INSUFFICIENT_CAUSAL_INFERENCE`.

### F-OBS-03 — HIPOTESE_PREDITIVA
**Falsificador:** Comparar predição de massa projetada/velocidades em sistemas com linhas de visada controladas, lente disponível, erro instrumental e holdout; rejeitar se não houver ganho com penalidade.
**Autoridade/referência:** `data/contracts/rll_entropy_dispersion_stability.v1.json`. **Classificação:** `NOT_RUN`.

### F-OBS-04 — TESE_UNIVERSAL
**Falsificador:** Comparar v_in/out=Vplaneta+v∞ in/out com |v∞| conservado; orientação da passagem pode reduzir ou aumentar energia heliocêntrica.
**Autoridade/referência:** `FALSIFIABILITY_PROTOCOL.md`. **Classificação:** `PHYSICS_COUNTEREXAMPLE`.

### F-OBS-05 — TESE_FACTUAL
**Falsificador:** Diferenciar fronteira da heliosfera solar, meio interestelar e fronteira galáctica; medidas de plasma e potência elétrica não estabelecem limite galáctico.
**Autoridade/referência:** `docs/workflows/RLL_POLYMORPHIC_EVIDENCE_ORCHESTRATION_V1.md`. **Classificação:** `FACTUAL_CORRECTION`.

### F-COS-01 — MODELO_BAYESIANO
**Falsificador:** Resultado reportado ln B10=-6,190±0,691; critério pré-declarado falhou. Repetir prior/likelihood/modelos, dados/covariância e uncertainties; não apagar resultado adverso.
**Autoridade/referência:** `data/contracts/rll_falsifier_bundle.json`. **Classificação:** `FAIL_SCOPED`.

### F-COS-02 — HIPOTESE_DE_PARAMETRO
**Falsificador:** Mediana posterior reportada z_t≈11,543, intervalo p16/p84 ≈[4,66;17,31] nesse teste; falha do critério contextual, não refutação de todo modelo possível.
**Autoridade/referência:** `data/contracts/rll_falsifier_bundle.json`. **Classificação:** `FAIL_SCOPED`.

### F-COS-03 — MODELO_PREDITIVO
**Falsificador:** Roda G4 seis modelos, mesma likelihood e covariância, sementes, holdout e G5 congelado; rejeitar superioridade se diferença de evidência corrigida for contrária ou não robusta.
**Autoridade/referência:** `data/contracts/rll_g4_background_tournament.v1.json`. **Classificação:** `NOT_RUN`.

### F-COS-04 — MODELO_PREDITIVO
**Falsificador:** Comparação com DR2 BAO+SN+CMB, priors e covariâncias oficiais, medidas fora da amostra e posterior/odds; modelos podem ser desconfirmados pela ausência robusta de ganho.
**Autoridade/referência:** `data/contracts/rll_g4_background_tournament.v1.json`. **Classificação:** `NOT_RUN`.

### F-COS-05 — TEORIA_FISICA_INCOMPLETA
**Falsificador:** Exigir equações de perturbação, soluções estáveis, espectros CMB, lensing e fσ8 com mesmas regras; falha se previsões físicas incompatíveis com dados e incertezas.
**Autoridade/referência:** `data/contracts/rll_g4_background_tournament.v1.json`. **Classificação:** `NOT_RUN`.

### F-COS-06 — HIPOTESE_COMPARADORA
**Falsificador:** Confrontar previsões independentes e likelihood conjunta com calibração estelar coerente, seleção e penalidade de parâmetros; rejeitar explicação ampla se qualquer família bem medida falhar robustamente.
**Autoridade/referência:** `FALSIFIABILITY_PROTOCOL.md`. **Classificação:** `NOT_RUN`.

### F-BIO-01 — HIPOTESE_BIOENERGETICA
**Falsificador:** Dose, espectro, calorimetria, balanço redox/ATP, controles pigmentados/despigmentados e replicação; rejeitar ganho de energia se ≤ controle dentro das incertezas.
**Autoridade/referência:** `data/science/rll_cellular_metabolic_manifold_claims_v1.json`. **Classificação:** `NOT_RUN`.

### F-BIO-02 — HIPOTESE_EXPLORATORIA
**Falsificador:** Medição espectrométrica in situ com controles de fundo e dose, verificação de conversão ATP/energia; se emissão/uso não observados no limite predefinido, hipótese específica falha.
**Autoridade/referência:** `data/science/rll_cellular_metabolic_manifold_claims_v1.json`. **Classificação:** `BLOCKED_TOKEN_VAZIO`.

### F-BIO-03 — HIPOTESE_DE_MODELO
**Falsificador:** Séries de fluxos e observáveis independentes, baseline estático, regularização e teste cego; rejeitar se não melhora desempenho após custo de complexidade.
**Autoridade/referência:** `data/science/rll_cellular_metabolic_manifold_claims_v1.json`. **Classificação:** `NOT_RUN`.

### F-EPI-01 — REGRA_METODOLOGICA
**Falsificador:** Traçar grafo de linhagem e matriz de overlap; fontes que reutilizam os mesmos indivíduos/medições não podem multiplicar likelihoods independentes.
**Autoridade/referência:** `data/contracts/rll_epistemic_evidence_graph.v1.json`. **Classificação:** `NOT_RUN`.

## Gates interdisciplinares obrigatórios

1. Pré-registrar `H0`/`H1`, versão do modelo, dataset release, seleção, covariância, métrica, priori e janela de holdout. Sem isto, `TOKEN_VAZIO`.
2. Se a mesma fonte observacional sustenta múltiplas notícias/DOIs/reanálises, deduplicar grupo de independência antes de calcular fatores de Bayes. Publicação ≠ medição ≠ replicação.
3. Comparação cosmológica justa exige ΛCDM/wCDM/CPL/GEDE/IDE/RLL no G4 com mesmas entradas, covariâncias oficiais completas e contagem de parâmetros; nenhum CMB/growth para RLL sem fecho de perturbação.
4. Propriedade de compressão mede bytes incluindo dicionário, cabeçalho, escape e decoder; nunca igualar taxa alta a maior verdade científica ou a entropia física.
5. Experimentos físicos orbitais ou biológicos exigem mecanismos e observações próprias; referências matemáticas do toro não substituem dinâmica/gravitacão/biologia.

## Evidências adversas que devem permanecer visíveis

- `F-COS-03` no legado: (z_t) fora de ([0.5,1.5]) (mediana 11.543). `FAIL_SCOPED`.
- `F-COS-04` no legado: (ln B_{10}=-6.190 pm 0.691) contra condição (>-5). `FAIL_SCOPED`.
- `F-COS-05` legado: (chi^2_{RLL}=93.806) passa teto fraco <150, mas (chi^2_{Lambda CDM}=28.966) foi menor no teste nominal; **não é superioridade**.
- Experimento português/Braille/Telex: 5 bits por código não significa 5 bits por caractere do texto; evidência em corpus e janelas específicos, não lei universal.
- q=√3/2 afim: (q^{42}
eq1), sem órbita periódica exata não estacionária. 42 índices combinatórios não são 42 atratores físicos.

## Leituras primárias e restrições

- [DESI DR2 oficial](https://data.desi.lbl.gov/doc/papers/dr2/), [Pantheon+ data release](https://github.com/PantheonPlusSH0ES/DataRelease), [Planck parâmetros base-ΛCDM](https://doi.org/10.1051/0004-6361/201833910).
- `FALSIFIABILITY_PROTOCOL.md` define condições de rejeição; não apagar `FAIL` por retrospectiva.
- Se não houver materialização verificável e controle de covariância/seleção, status fica `NOT_RUN` mesmo que um argumento pareça convincente.

**Rollback:** fechar PR sem merge ou reverter documentos aditivos; preservar fontes originais e registros históricos append-only.
