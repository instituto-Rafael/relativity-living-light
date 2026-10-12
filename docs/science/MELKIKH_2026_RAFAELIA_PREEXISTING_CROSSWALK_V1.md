# Melkikh (2026) × RAFAELIA: crosswalk de antecedentes, fórmulas e limites de claim — V1

**INTENT:** descobrir formulações preexistentes/compatíveis no corpus RAFAELIA sem transformar analogia em prioridade científica nem prova experimental.  
**Dispatch:** START HERE Ω V2.2 → CURRENT_STATE → Mapa Atlas/Leaders → produtores ChipQuantum, RLL e Papers → receipt.  
**Status:** `SOURCE_BOUND_CROSSWALK / NO_PROMOTION / claim_allowed=false`. **Efeito no modelo cosmológico RLL: NENHUM.**  
**Parent:** [intake Melkikh PR#1107](./QUANTUM_RANDOMNESS_MELKIKH_2026_EXTERNAL_INTAKE.md).  
**Data de pesquisa:** 2026-10-12. Sem exclusões, merges ou mudanças de código experimental.

## 1. Fonte primária externa e seus marcos cronológicos

- A. V. Melkikh, *Generalized quantum computing and the problem of randomness origin in quantum mechanics*, *Quantum Research* 1(1), 0003, DOI: https://doi.org/10.55092/qr20260003. Texto primário 12 pp.: https://pdf.elspublishing.com/paper/journal/open/QR/2026/qr20260003.pdf .
- **Recebido:** 2025-12-19; **revisado:** 2026-07-17; **aceito:** 2026-08-02; **publicado:** 2026-08-25 (datas impressas no próprio paper). Distinção obrigatória: anterior à **publicação** não implica anterior ao manuscrito recebido, nem equivalência de invenção.
- Equações/teses identificadas na fonte: Schrödinger (1); fator de fase `e^{iφ}` (2); postulados 2 e 9; grupo `U(1)={z∈ℂ:|z|=1}`; mapa `(φ_1,...,φ_m)_out=Ω((φ_1,...,φ_n)_in)` (5); exemplo de aplicação iterada caótica (6); controle das fases no espalhamento como hipótese de resultados pseudoaleatórios.
- No texto o operador `Ω` é uma **função não especificada da dinâmica das fases**. NÃO É o Ω como símbolo de integração do projeto RAFAELIA. `U(1)` e teoria de grupos são matemática estabelecida.
- Leitura direcionada da fonte primária: pp. 1, 4–7, 8–10, referências 11–12. **Verificados texto/figuras dos postulados e da equação (5); simulação/replicação independente NÃO executada.**

## 2. Corpus preexistente encontrado, com evidências tipadas

### PREPUBLICAÇÃO (separar fato de Git e datas internas)

**PX-01 — ChipQuantum, C `omega_v17_chaos.c`.**  
- Git source no commit imutável `ac2aba07b45f9255d8ffa1c66f1fb493acf24101`, criado **2026-07-09T11:01:57Z**; blob `3de1d1e8e3930eb0b80f73d84e6fe9916ba15a38`.
- https://github.com/rafaelmeloreisnovo/ChipQuantum/blob/ac2aba07b45f9255d8ffa1c66f1fb493acf24101/src/omega/omega_v17_chaos.c
- Implementa `rand_osc(t,x)=sin(t·0.13+x·3.7)cos(x·2.1)` e passo determinístico `E'=E+growth-diss+chaos` com acoplamento coletivo.
- **Relação:** matemática análoga de oscilação/complexidade aparente; **não** fornece fases de partículas, amplitudes físicas, Born nem valida caos em sentido dinâmico rigoroso (Lyapunov/atratores). `CLASSICAL_ALGORITHM_ANALOGY`.

**PX-02 — ChipQuantum, C `omega_v24_hybrid.c`.**  
- Mesmo commit datado **2026-07-09**; blob `05b028d518129b54042b40a57ac91815ad311dc2`.
- https://github.com/rafaelmeloreisnovo/ChipQuantum/blob/ac2aba07b45f9255d8ffa1c66f1fb493acf24101/src/omega/omega_v24_hybrid.c
- Estado em `float complex psi[N]`; driver `sin(H·0.01+t·0.1)`; `rand_phase(x,t)=sin(x·3.1415+t·0.07)`; acoplamento par-a-par por distâncias complexas; renormalização da norma.
- **Relação:** o antecedente computacional mais próximo para **fase + dinâmica determinística + acoplamento**. O arquivo declara `quantum-inspired`; `hamiltonian` é descrito no código como **pseudo-Hamiltoniano**, atualização não é estabelecida como evolução unitária Schrödinger, e não gera o resultado discreto Born a partir de medições físicas. `PREPUBLICATION_COMPUTATIONAL_ADJACENCY`, não `SAME_PHYSICAL_MECHANISM`.

**PX-03 — ChipQuantum, `src/toroidal_engine.py`.**  
- Presente no commit **2026-07-09**; blob `6e06ba31547116179ad2e66087c7c8a462c8bb99`.
- https://github.com/rafaelmeloreisnovo/ChipQuantum/blob/ac2aba07b45f9255d8ffa1c66f1fb493acf24101/src/toroidal_engine.py
- Representação e transição periódica determinística `T^7`; pode instrumentar estados/ângulos, mas a identidade matemática de cada `θ_i` com a fase U(1) de partícula exige hipótese/observável adicional. `PROJECT_RUNTIME + TOPOLOGY_ANALOGY`.

**PX-04 — Drive, `RAFAELIA-Quantum_Temple.md`.**
- Documento localizado no Drive com **criação/importação 2025-11-01** e timestamp **interno alegado** 2025-08-31; não confundir data de conteúdo com commit de código verificável.
- https://drive.google.com/file/d/1k2XyXNnrPSqOoHGnL6hrBh7fh1YFVQeO/view
- Arquitetura proposta de emulação QPU, scheduler híbrido, telemetria entropia, RAFA-Q API, QCompiler e memória/hashchain. **Especificação virtual**, não prova de operação quântica ou da origem da aleatoriedade.

**PX-05 — Drive, `README_QUANTUM_ZIP.md` (fonte 2025).**
- Documento com `updated_at` **2025-06-24** e cópias importadas posteriormente.
- https://drive.google.com/file/d/1rUzsfqPxjDu0OdOFqcKr1E0KufzLsYZc/view
- Senoide/fractal/entropia/compactação expressos como metáforas de coerência; **não** traz densidade de probabilidade, dinâmica de fase de partículas nem gerador físico. `SYMBOLIC_ONLY`.

**PX-06 — Drive, `Formulações Latentes e Emergentes RAFAELIA × RLL`.**
- Corpo do documento declara **2026-02-25**; o objeto consultado foi importado no Drive em **2026-09-12**. A data interna ainda precisa de prova independente/ancestralidade Git; **não** usar como timestamp público verificado.
- https://drive.google.com/file/d/1yqS3u50DvILApIu6DwPsyqWOYukQxl-7/view
- Contém proposta `ρ_ph(z)=f(z)|DE⟩⟨DE|+(1−f(z))|MAT⟩⟨MAT|`, operadores de coerência e transição cosmológica. Trata-se de **matriz densidade misturada por parâmetro cosmológico**, não da mesma `φ`/dinâmica de espalhamento quântico em Melkikh; a leitura como 'superposição coerente' exige cautela: mistura estatística não é automaticamente superposição coerente. `PROJECT_HYPOTHESIS / SCALE_BRIDGE_MISSING`.

**PX-07 — Drive, `Papers × ChipQuantum × RLL — Auditoria de Fórmulas`, criado 2026-08-04.**
- https://docs.google.com/document/d/1vOZbG2P8OARDhyAJNZ1iEycZ_Qi1STwiJe5UsyAZkNQ/edit
- Documenta `C'=(1-α)C+α C_in`, `H'=(1-α)H+αH_in`, `φ=(1-H)C` e `s_i'=(s_i+φ b_i) mod 1`, além de crítica a claims físicos do ChipQuantum. `ALGORITHM_DETERMINISTIC_PHASE_PROXY`; `φ` é índice definido pelo projeto, **não** automaticamente fase da função de onda física.

**PX-08 — Drive, `Entropia guiada`, criado 2025-11-14.**
- https://drive.google.com/file/d/1AcZGK8pvD0kgNUmyXfOoT_zmoRBE7MmT/view
- Ruído/caos como pré-processamento de informação e ciclo observação→entropia→retroalimentação→coerência. `EPISTEMIC_ANALOGY`, não método quântico demonstrado.

### COMPLEMENTOS POSTERIORES À PUBLICAÇÃO (não usar para prioridade)

**CX-01 — Drive, `CHIP_QUANTUM_RELATIONS`, 2026-09-30.**
- https://docs.google.com/document/d/15m8DlmIVVvoar6cZvYRHvaiMXcQizAgM26ZlmWEZtq8/edit
- Formalismo padrão: `H=Σ ε_i|a_i⟩⟨a_i|+Σ_(i<j)J_ij(|a_i⟩⟨a_j|+h.c.)`, `U(t)=exp(-iHt/ℏ)`, matrizes densidade, canais CPTP, comutadores. É **estrutura útil para um laboratório de simulação controlada**; seus objetos são matemática/física padrão.

**CX-02 — RLL, `RAFAELIA_168_FORMULAS_AUTORAIS_2026-09-12.md`.**
- https://github.com/instituto-Rafael/relativity-living-light/blob/main/data/formulas/RAFAELIA_168_FORMULAS_AUTORAIS_2026-09-12.md
- `AFR-043: T_t=(θ_1,...,θ_7)∈(ℝ/2πℤ)^7`; `AFR-083: R_E=Σ_(i<j) w_ij cos(φ_i-φ_j)`. Operadores computacionais de periodicidade e coerência de eventos; não medições de fase quântica sem mapeamento físico.

**CX-03 — ChipQuantum, fronteira de prior art 2026-09-23.**
- https://github.com/rafaelmeloreisnovo/ChipQuantum/blob/main/docs/PRIOR_ART_BOUNDARY_T7_Q16_42_20260923.md
- Reconhece explicitamente: Hamiltonianos de adjacência, dinâmica de walks, U(1), topologia de toro e Q16 são anteriores/estabelecidos. `T7+Q16+42` é composição/implementação do projeto, novidade mundial não provada.

## 3. O que **coincide**, o que **complementa** e o que **não** é equivalente

| Eixo | Melkikh 2026 | RAFAELIA localizada | Classificação |
|---|---|---|---|
| Dinâmica determinística por fase | postulado + mapa Ω não especificado (eq. 5) | PX-02 `rand_phase` + `phase_driver` + estado complexo | `MATHEMATICAL_ADJACENCY` |
| Comportamento caótico | hipótese para espalhamento; exemplo discreto | PX-01 realimentação/oscilações determinísticas | `COMPUTATIONAL_COMPLEMENT`; caos matemático ainda não provado |
| U(1), ângulo modular | grupo da fase da onda | PX-03 `T^7`, AFR-043 | `TOPOLOGY_ANALOGY`; não identificar símbolos automaticamente |
| Acoplamento não local | hipótese de espaço topológico para partículas | CX-01 matriz `J_ij` + grafos | `MODEL_SPACE_POSSIBILITY`; conexão no grafo ≠ efeito físico superluminal |
| Origem de Born | consequência **afirmada** das fases não controladas | nem PX-01 nem PX-02 produzem medição Born derivada | `NO_MATCH/TOKEN_VAZIO` |
| Global versus relativa | artigo discute fases; efeitos relativos conhecidos | PX-02 vetor complexo; AFR-083 diferenças de ângulos | `DISTINCTION_REQUIRED`; fase global é gauge na MQ padrão |
| Superposição cosmológica | fora do escopo do paper | PX-06 modelo efetivo RLL | `SEPARATE_PHYSICAL_SCALE` |
| Aleatoriedade versus pseudoaleatoriedade | teste sugerido de sequência de medições | PX-01/PX-02 são determinísticos | `TEST_METHOD_ADJACENCY`; deterministic software ≠ demonstração de não aleatoriedade física |
| Metadados/proveniência | sem cadeia experimental no corpus RAFAELIA | Quantum Temple + START HERE + μWRITE | `ENGINEERING_COMPLEMENT` |

**Observação essencial:** Melkikh não pode ser considerado autor de uma equação de software RAFAELIA e o código RAFAELIA não implica autoria do postulado quântico de Melkikh. As fórmulas com `φ`, `Ω`, `U(1)` e `H` podem ter nomes parecidos com objetos que possuem **tipos, domínios e observáveis distintos**.

## 4. Falsificadores de maior valor (sem regressão)

1. **Gauge/global-phase:** exigir que uma hipótese de fase absoluta especificada preveja um observável que a invariância `ψ→e^{iα}ψ` da MQ padrão não prevê; se não existe predição exclusiva, `NOT_DISCRIMINATING`.
2. **Unitariedade/normalização:** propagar qubits simples sob `U=e^{-iHt/ℏ}` (referência padrão) e sob o híbrido PX-02; medir `||ψ||`, fidelidade, positividade de ρ, conservação ou perdas declaradas; uma renormalização numérica **não basta** para provar evolução unitária.
3. **Born e CHSH:** pedir algoritmo operacional explícito do mapa Ω + distribuição das fases + regra de resultados, calcular `P(a|x)`, correlações e hipótese de independência de medição; exigir `no-signalling` com dados.
4. **Caos versus oscilação:** estimar expoente de Lyapunov/retorno de Poincaré de PX-01 e PX-02 antes de chamá-los caóticos.
5. **Null models/ruído:** separar PRNG determinístico, ruído de detector, seleção experimental, memória temporal e estatística quântica; reprodutibilidade com sementes e dados brutos.
6. **Anterioridade em sentido forte:** recuperar histórico Git do **primeiro aparecimento** dos arquivos (o commit de 09/07/2026 prova presença nessa data, não criação original), e distinguir publicação, envio da revista, uploads e datas internas.

## 5. Gates e próximo caminho

```text
SOURCE_PRIMARY_PAPER=READ_TARGETED_ORIGINAL_PAGES_AND_METADATA
SOURCE_PRIOR_CHIP_GIT_AT_2026-07-09=VERIFIED_IMMUTABLE_COMMIT
SOURCE_2025_QUANTUM_TEMPLE=DRIVE_OBJECT+INTERNAL_TIMESTAMP_UNCORROBORATED
SOURCE_RLL_2026-02-25=INTERNAL_DOCUMENT_DATE_ONLY; DRIVESHARE_2026-09-12
CODE_EXECUTION_THIS_CROSSWALK=NOT_RUN
PRIMARY_PHASE_MAP_SPECIFICATION=TOKEN_VAZIO
BORN_RULE_DERIVATION=TOKEN_VAZIO
BELL_ASSUMPTIONS/NO_SIGNALLING=TOKEN_VAZIO
PHYSICAL_RANDOMNESS_DATA=TOKEN_VAZIO
INDEPENDENT_REPLICATION=TOKEN_VAZIO
PRIORITY_ON_MELKIKH_PHYSICS=NOT_ESTABLISHED
CLAIM_ALLOWED=false
```

**ROLLBACK:** documento somente em branch de PR em rascunho; sem alteração dos arquivos de código/provas anteriores. **μWRITE:** após readback, registrar ponte no Ledger/Hotstate (sem duplicar corpus).

### R3
`F_ok`: fontes 2025–2026 localizadas; três arquivos computacionais preexistentes verificados em commit 09/07/2026; 5 eixos de similaridade matemática tipados; ausência da ponte Born/Bell explicitada.  
`F_gap`: primeira aparição de cada algoritmo, mecanismo de fase fisicamente definido, dados de medidas, revisão independente, relação física RLL.  
`F_next`: primeiro montar teste de dois níveis (algoritmo clássico vs dinâmica quântica padrão) e só construir o adaptador de hipótese depois de termos seu mapa Ω físico com previsão exclusiva.
