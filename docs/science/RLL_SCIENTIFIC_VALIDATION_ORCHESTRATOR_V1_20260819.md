# RLL Scientific Validation Orchestrator V1 — 2026-08-19

**Status:** `PROPOSAL_INERT_FAIL_CLOSED`  
**Base de integração:** `rll/lab`  
**claim_allowed:** `false`  
**publication_effect:** `NONE`  
**Contrato:** `data/contracts/rll_scientific_validation_orchestrator.v1.json`

## 1. Objetivo

Transformar a maturidade já existente de governança, CI, falsificabilidade e custódia do RLL em uma rota científica única que reduza incerteza sem apagar resultados negativos, sem misturar rotas de likelihood e sem preencher `TOKEN_VAZIO` por inferência.

A unidade de evolução deixa de ser "mais um arquivo" e passa a ser:

```text
pergunta científica
→ autoridade/fonte
→ formulação
→ dado + covariância
→ baseline adversarial
→ likelihood
→ inferência
→ falsificador
→ robustez
→ replicação
→ receipt
→ linguagem permitida
```

O orquestrador não afirma que o RLL é correto. Ele define as condições sob as quais cada afirmação pode ganhar ou perder sustentação.

## 2. Diagnóstico que motiva esta camada

O repositório já possui:

- matemática estrutural executável e invariantes;
- dados reais e rotas DESI/Pantheon/CMB;
- comparação LCDM/CPL/RLL;
- AIC/AICc/BIC;
- MCMC;
- dynesty/Bayes em rota anterior;
- covariância DESI em rota própria;
- claim gates;
- cadeia de custódia e hashes;
- Transit Tower sequencial/fail-closed;
- preservação de resultados desfavoráveis.

O problema científico prioritário não é ausência total de componentes. É **fragmentação entre componentes que precisam ser executados sob um único contrato congelado**.

Exemplos atuais que exigem reconciliação:

1. Pantheon+ STAT+SYS ainda precisa entrar na mesma rota canônica usada no ranking final quando Pantheon+ for consumido.
2. Resultados MCMC, dynesty e BIC-proxy devem ser reconciliados sob o mesmo conjunto de dados, priors, nuisances e implementação.
3. Um background cosmológico pode ser testado por BAO/SNe, mas não é ainda uma teoria física fechada para crescimento/CMB/lensing sem perturbações explícitas.
4. Reexecução do mesmo pipeline não equivale a replicação independente.
5. Smoke/sanity/dry-run não pode ser usado como ranking científico final.

## 3. Princípio antirregressão

```text
NUNCA:
TOKEN_VAZIO --narrativa--> VERIFIED

SOMENTE:
TOKEN_VAZIO
  --fonte localizada-->
EVIDENCE_CANDIDATE
  --execução rastreável-->
OBSERVED_PENDING_REPLICATION
  --reprodução + falsificador-->
VERIFIED_LIMITED ou FALSIFIED_IN_SCOPE
  --replicação independente-->
VERIFIED_REPRODUCIBLE
```

Uma contradição também é evolução do conhecimento:

```text
hipótese + teste incompatível = CONTRADICTION/FALSIFIED_IN_SCOPE
```

O estado nunca volta silenciosamente para "desconhecido".

## 4. Gates científicos

### G0 — Autoridade, proveniência e freeze

Congelar:

- fonte primária;
- versão do dataset;
- checksums;
- licença/direitos conhecidos;
- critérios de inclusão/exclusão;
- lista inicial de `TOKEN_VAZIO`.

**Stop condition:** identidade do dado, versão ou covariância ambígua.

### G1 — Matemática estrutural e limite nulo

Exigir:

- unidades e domínio;
- `E²(0)=1` na tolerância declarada;
- positividade no domínio usado;
- derivadas analíticas × diferenças finitas;
- setor adicional desligado recuperando exatamente o baseline declarado;
- equivalência numérica entre implementações usadas na inferência.

**Stop condition:** RLL não recupera seu próprio limite nulo ou duas implementações divergem sem explicação.

### G2 — Materialização de dados e covariância completa

Prioridade imediata:

- DESI DR2 BAO: vetor + ordenação + covariância oficial aplicável;
- Pantheon+: dados e STAT+SYS na mesma rota canônica;
- CMB: manifesto explícito entre priors comprimidos e likelihood/espectros completos;
- crescimento `fσ8`: fonte, baixo-z, correlações e seleção;
- cronômetros: matriz/sistemática quando aplicável.

Toda transformação deve gerar:

```text
raw_hash
+ transform_command
+ transform_code_hash
+ derived_hash
+ shape/order checks
+ receipt
```

### G3 — Compatibilidade antes do joint fit

Executar antes da multiplicação de likelihoods:

- `eta(z)`;
- `F_AP(z)`;
- sensibilidade à amostra de SNe;
- sensibilidade de reconstrução/calibração;
- decisão `COMPATIBLE`, `BRANCH_REQUIRED` ou `BLOCKED`.

Compatibilidade falha não deve ser escondida por um posterior conjunto.

### G4 — Torneio justo de baselines

Comparadores mínimos por pergunta de background:

```text
LCDM
w0wa/CPL
GEDE
um comparator interagente ou viscoso formalmente fechado
RLL logistic
```

Regras:

- mesmos blocos observacionais;
- mesma covariância;
- mesma política de nuisances;
- contagem explícita de parâmetros;
- AIC/AICc/BIC derivados dos outputs, nunca hard-coded.

### G5 — Likelihood conjunta canônica

Criar **uma** rota de autoridade para ranking científico.

O manifesto deve fixar:

```text
datasets
covariances
model versions
priors
nuisances
parameter bounds
likelihood components
commit
container/environment
```

Resultados de smoke continuam úteis como testes de software, mas ficam fora da autoridade científica final.

### G6 — Posterior e evidência Bayesiana

Executar duas famílias complementares:

1. MCMC multichain para posterior/degenerescências;
2. nested sampling multiseed para `log Z` e seleção Bayesiana.

Registrar:

- seed set;
- convergência;
- tamanho efetivo/amostragem aplicável;
- `log Z ± erro`;
- posterior de `Omega_s0`, `z_t`, `w_t`;
- correlações e degenerescências;
- estabilidade entre seeds;
- sensibilidade a priors.

O resultado anterior `ln B10 < 0` não deve ser apagado. A nova execução responde se ele é reproduzido sob a rota unificada.

### G7 — Robustez, ablação e synthetic recovery

Rodar matriz controlada:

- retirar um bloco de dados por vez;
- trocar amostra de SNe quando cientificamente defensável;
- full covariance × ablação diagonal explicitamente marcada;
- prior largo × conservador/preregistrado;
- injeção sintética conhecida;
- posterior predictive checks;
- false-positive/null ledger.

Pergunta central:

> o resultado é provocado pelos dados, pelos priors, pela implementação ou pela hipótese?

### G8 — Fechamento físico e perturbações

Antes de interpretar `fσ8`, CMB e lensing como testes completos do RLL, escolher e implementar uma interpretação física explícita:

```text
effective fluid OR covariant field/EFT OR other declared closure
```

Definir:

- conservação;
- gauge/prescrição de perturbação;
- velocidade do som;
- stress anisotrópico;
- estabilidade;
- graus de liberdade;
- limite LCDM.

Primeiro gate em CLASS/CAMB:

```text
RLL_sector_off -> reproduce_standard_LCDM
```

Somente depois ativar o setor RLL.

### G9 — Crescimento, CMB, lensing e não linear

Com G8 fechado:

- `fσ8(z)`;
- TT/TE/EE;
- CMB lensing;
- weak lensing;
- `P(k)`;
- decisão separada para regime não linear/N-body.

Priors CMB comprimidos continuam válidos para perguntas limitadas, mas não substituem full spectra quando a hipótese altera perturbações.

### G10 — Replicação independente

Três níveis:

```text
R1 clean replay: mesmo código, ambiente limpo
R2 computational crosscheck: sampler/likelihood alternativo
R3 independent implementation: implementação separada ou revisor externo
```

A meta mínima antes de linguagem forte é R2; R3 é a rota preferida para validação externa.

### G11 — Publicação e claim router

Toda frase promovida deve resolver para:

```text
claim_id -> source -> run -> artifact -> metric -> falsifier -> state
```

O pacote deve conter:

- método;
- dados/versões;
- ambiente;
- seeds;
- resultados favoráveis e desfavoráveis;
- limitações;
- `TOKEN_VAZIO` residual;
- checksums;
- instrução de reprodução.

## 5. Ordem de maior ganho científico agora

### P0-A — Unificar full covariance + Pantheon STAT+SYS

**Por quê:** reduz uma incerteza que afeta diretamente comparação de modelos.

**Fecha/reduz:**

- `TOKEN_VAZIO` de Pantheon completo na rota conjunta;
- ambiguidade entre resultados de rotas distintas;
- risco de χ² artificialmente baixo por tratamento de erros.

### P0-B — Reconciliar MCMC + dynesty + BIC proxy numa única execução congelada

**Por quê:** já existem resultados, mas a pergunta científica é se convergem quando todos consomem o mesmo contrato.

**Saída:**

```text
model_selection_reconciliation.json
posterior_convergence.json
nested_multiseed.json
prior_sensitivity.csv
```

### P0-C — Synthetic recovery + null injection

Criar dados simulados **somente para validar o método**, nunca para substituir observação real.

Testes:

1. gerar LCDM conhecido → pipeline deve recuperar setor RLL aproximadamente nulo;
2. gerar RLL conhecido → pipeline deve recuperar os parâmetros injetados dentro da cobertura declarada;
3. repetir multiseed;
4. medir falso positivo/falso negativo.

Se falhar, o problema é pipeline/identificabilidade antes de ser cosmologia.

### P1-A — Perturbações + CLASS/CAMB

Esse é o maior salto de **maturidade física**, porque transforma RLL de parametrização de background para modelo confrontável por crescimento/CMB/lensing.

### P0-D — Replicação independente

Após a rota canônica G6 existir, executar em ambiente limpo e por sampler alternativo. Preservar deltas mesmo quando discordarem.

## 6. Materiais externos a congelar no G0

Usar apenas fonte primária/oficial para a execução canônica:

- DESI DR2 BAO e produtos cosmológicos oficiais;
- Pantheon+ DataRelease, incluindo covariância STAT+SYS aplicável;
- Planck Legacy Archive/likelihood oficial quando full CMB for ativado;
- ACT likelihood oficial apenas em branch comparativa declarada;
- datasets de crescimento/lensing somente após identificação primária e contrato de covariância.

A versão exata, URL/provider, data de coleta, licença/termos, SHA-256 e transformação local devem entrar no receipt. O nome de um dataset não é evidência suficiente de materialização correta.

## 7. Orquestração: como integrar sem quebrar a Transit Tower

A Transit Tower atual deve continuar responsável por integridade do repositório.

A nova camada científica deve ser adicionada em duas fases:

### Fase A — agora

```text
contrato científico
+ documentação
+ nenhuma mudança de execução
```

Estado deste commit: `PROPOSAL_INERT_FAIL_CLOSED`.

### Fase B — após revisão

Criar perfil dedicado, por exemplo:

```text
scientific_validation_session
```

com execução sequencial:

```text
repo/governance gates
→ G0/G1
→ G2
→ G3
→ G4/G5
→ G6
→ G7
→ G8/G9 quando habilitados
→ G10
→ receipt final
```

Cada etapa deve possuir `enabled=false` até o workflow correspondente provar:

- input contract;
- output contract;
- artifact-on-failure;
- timeout;
- permissions mínimas;
- no secrets in receipts;
- `claim_allowed=false` por default.

## 8. Função de prioridade

Para evitar gastar esforço em áreas bonitas mas pouco informativas:

```text
Priority =
(uncertainty_reduction
 * scientific_leverage
 * independence
 * observability)
/
(execution_cost * regression_risk)
```

Escala de cada fator: 1..5.

Isso tende a colocar no topo:

1. covariância/likelihood canônica;
2. reconciliação de inferência;
3. synthetic recovery;
4. fechamento perturbativo;
5. replicação independente.

## 9. Receipt mínimo

Cada fechamento deve registrar pelo menos:

```text
event_id
gate_id
repo/ref/commit
input paths + SHA256
code paths + SHA256
environment lock
command
seed/set de seeds
stdout/stderr digest
metrics
falsifier outcome
TOKEN_VAZIO before/after
contradictions
claim_allowed
next observable step
```

## 10. Critério de parada

Parar e registrar, em vez de "forçar evolução", quando:

- dado/covariância não pode ser autenticado;
- o baseline não é recuperado;
- convergência falha;
- posterior é dominado por borda/prior sem identificabilidade;
- uma contradição exige reformulação do modelo;
- o resultado depende de escolha não justificada;
- não existe mecanismo físico definido para o observável reivindicado.

`STOP` com receipt é progresso científico.

## 11. Resultado esperado

O objetivo não é chegar a `TOKEN_VAZIO=0` artificialmente.

O objetivo é que cada vazio importante esteja em um destes estados:

```text
CLOSED_BY_EVIDENCE
FALSIFIED_IN_SCOPE
BOUNDED_BY_LIMIT
BLOCKED_BY_EXTERNAL_DEPENDENCY
DEFERRED_WITH_EXPLICIT_REASON
```

Assim a lacuna deixa de ser desconhecimento amorfo e vira estado científico navegável.

## R3

```text
F_ok:
  infraestrutura, falsificadores, MCMC/dynesty, covariância e governança já existem em partes reais.

F_gap:
  falta unificação da rota científica, fechamento perturbativo e replicação materialmente independente.

F_next:
  G2/G5 -> G6 -> G7 primeiro; G8/G9 depois; G10 fecha a primeira volta de validação reproduzível.
```
