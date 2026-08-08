# RLL TOKEN_VAZIO Reconciliation V1

## Objetivo

Converter lacunas genéricas e incertezas em estados auditáveis sem fabricar conclusão.

Estados efetivos:

- `RESOLVED`: pergunta operacional fechada por evidência materializada;
- `RESOLVED_NEGATIVE`: incerteza fechada por resultado negativo/limite conhecido;
- `REDUCED`: vazio amplo substituído por sucessor mais específico;
- `OPEN_INTERNAL | OPEN_EXTERNAL | OPEN_HUMAN | OPEN_GOVERNANCE | OPEN_MIXED`: autoridade ainda ausente;
- `OPEN_EVIDENCE_MISSING`: uma regra tentou fechar/reduzir sem conseguir provar sua evidência.

`TOKEN_VAZIO` nunca significa zero, PASS ou inexistência de problema.

## Estado efetivo desta revisão

```text
input_tokens       = 22
terminal_resolved  = 7
reduced_generic    = 3
open               = 12
claim_allowed      = false
publication_ready  = false
```

A contagem mede somente o ledger auditado desta revisão; não é percentual de verdade física do RLL.

## Fechamentos e reduções materializados

### 1. Modern SN full likelihood — `REDUCED`

Pantheon+ full covariance e DES-Dovekie full precision já foram materializados. O token genérico foi substituído por perguntas específicas de nuisance, limites e identificabilidade.

### 2. Common-nuisance Pantheon+ ↔ Dovekie — `RESOLVED`

A run `31225058309` executou Pantheon+ Hubble-flow-only com a mesma lógica SN-only de nuisance usada por Dovekie: `H0=70` apenas como escala e um offset aditivo de magnitude perfilado.

```text
Pantheon+ Hubble-flow: N=1580
Δχ² CPL−ΛCDM = -0.4693068159
ΔBIC CPL−ΛCDM = +14.2610534361
Δχ² RLL−ΛCDM ≈ -2.73e-12
ΔBIC RLL−ΛCDM = +22.0955403781
RLL best Ωs0 = 0

DES-Dovekie: N=1820
Δχ² CPL−ΛCDM = -4.7924225030
ΔBIC CPL−ΛCDM = +10.2207610571
Δχ² RLL−ΛCDM ≈ -7.50e-8
ΔBIC RLL−ΛCDM = +22.5197752652
```

O mismatch de nuisance/H0 deixa de ser explicação para a direção RLL≈ΛCDM em SN-only.

### 3. CPL `wa=-3` boundary sensitivity — `RESOLVED_NEGATIVE`

Ao expandir o profile, o ótimo moveu de `wa=-3` para aproximadamente `wa=-6`, confirmando que o antigo valor era boundary-sensitive.

### 4. CPL lower 95% profile closure — `RESOLVED`

O gate dedicado `Dovekie CPL wa Lower-Bound Gate`, run `31227378178`, materializou a travessia `Δχ²=3.841458820694124`:

```text
global best χ²       = 1625.3554394914
wa lower 95% estimate = -12.6064453125
excluded low          = -12.609375   Δχ²=3.8473252234
included high         = -12.603515625 Δχ²=3.8356923917
bracket width         = 0.005859375
all starts converged  = true
```

Isto fecha `TOKEN_VAZIO_CPL_DOVEKIE_WA_LOWER_PROFILE_CLOSURE` numericamente sob o box declarado. Não transforma CPL em modelo bem determinado: na região da travessia, o otimizador leva `w0` ao bound superior `-0.3`, o que limita interpretação física.

### 5. RLL SN-only parameter identifiability — `RESOLVED_NEGATIVE`

Pantheon+ e Dovekie registram que os parâmetros de transição RLL não são identificados por SN-only no formalismo testado. Repetir indefinidamente SN-only não altera essa autoridade.

### 6. Bayes histórico genérico — `REDUCED`

Já existia nested sampling real com `dynesty` na FASE20:

```text
logZ_RLL  = -404.3402864972 ± 0.5299056817
logZ_LCDM = -398.1500757348 ± 0.4429460223
ln(B10)   = -6.1902107624 ± 0.6906527421
```

Portanto “Bayes nunca foi executado” era um vazio genérico obsoleto.

### 7. Modern Dovekie LCDM×CPL×RLL Bayes — `RESOLVED`

A run `31226738703` executou nested sampling normalizado, prior-locked e com nuisance de magnitude próprio para os três modelos. O receipt custodiado registra:

```text
dynesty = 3.1.0
nlive   = 160 por run
seeds   = 20260807, 20260808
N_SN    = 1820

logZ_LCDM = 246.6346691182 ± 0.1963855122
logZ_CPL  = 246.5239546274 ± 0.2254315078
logZ_RLL  = 246.4082724076 ± 0.1876292006

lnB(CPL/LCDM) = -0.1107144908 ± 0.2989759758
lnB(RLL/LCDM) = -0.2263967106 ± 0.2716099894
```

Sob esses priors e o likelihood Dovekie SN-only, não há discriminação Bayesiana forte entre os três modelos. Isto fecha `TOKEN_VAZIO_REAL_BAYES_MODERN_3MODEL_PRIOR_LOCK`, mas não fecha multi-probe nem replicação independente.

Sucessores:

```text
TOKEN_VAZIO_REAL_BAYES_JOINT_MULTI_PROBE
TOKEN_VAZIO_INDEPENDENT_REPLICATION
```

### 8. DESI DR2 genérico — `REDUCED`

O repositório já possui um setup real de 13 observáveis DESI DR2 BAO e comparação local:

```text
χ²_LCDM = 28.6936910789
χ²_RLL  = 34.5274716705
Δχ²     = +5.8337805916
ΔAIC    = +9.8337805916
ΔBIC    = +10.9636793067
```

Esse resultado local favorece ΛCDM e é preservado. O vazio correto não é “DESI ausente”; é:

```text
TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION
```

Um setup local/block-diagonal não será relabelado como likelihood oficial joint/cross-block.

### 9. DES-SN5YR explicit repository license — `RESOLVED_NEGATIVE`

No commit pinado upstream auditado não foi encontrado grant explícito de redistribuição no root/README. Política operacional: não presumir permissão de redistribuição até receipt de licença/permissão aplicável.

### 10. `rll/release` refresh — `RESOLVED`

`rll/release` foi fast-forwarded com `force=false` para um baseline então idêntico ao `main`, sem descartar commits exclusivos de release. Isso não autoriza transportar automaticamente história divergente de `rll/lab`/`rll/integration`.

## P0 realmente aberto agora

1. `TOKEN_VAZIO_REAL_BAYES_JOINT_MULTI_PROBE` — depende de componentes observacionais reproduzidos e sem double counting;
2. `TOKEN_VAZIO_INDEPENDENT_REPLICATION` — exige autoridade realmente independente;
3. `TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION` — exige produtos/likelihood oficial e referência LCDM/CPL;
4. `TOKEN_VAZIO_PHYSICAL_EXECUTION` — exige Android/Termux físico.

## P1/P2 preservados

P1 mantém ACT DR6, DES Y6 3x2pt, CLASS/CAMB + contrato explícito de perturbações RLL, H0 formal e settings externos GitHub. P2 mantém arqueologia das refs e validação empírica/Termux/treino do UTM-185.

## Execução do reconciliador

```bash
python3 tools/rll_token_vazio_reconcile.py \
  --output artifacts/governance/RLL_TOKEN_VAZIO_RECONCILIATION_CURRENT.json
```

O reconciliador combina ledger-base + overrides append-only. Estado terminal/reduzido exige evidence file + assertions; assertion ausente/falsa vira `OPEN_EVIDENCE_MISSING`.

```text
reconciler saudável != ciência concluída
```

## Anti-regressão

- `claim_allowed=false` e `publication_ready=false` permanecem invariantes;
- resultado negativo não é promovido a suporte do modelo;
- Bayes histórico não é transplantado para likelihood moderno;
- Bayes SN-only não é transplantado para multi-probe;
- Pantheon+ e Dovekie não são multiplicados como likelihoods independentes sobrepostos;
- setup DESI local não é chamado de reprodução oficial joint;
- CI/container não substitui receipt físico Termux;
- release refresh exige fast-forward verificável e `force=false`.

## R3

- **F_ok:** common-nuisance fechado; boundary `wa=-3` diagnosticado; lower `wa` 95% fechado em `≈-12.60645`; RLL SN-only não identificável; modern Dovekie Bayes executado; DESI genérico estreitado; release refresh e licença convertidos em estados auditáveis.
- **F_gap:** joint multi-probe Bayes, reprodução DESI joint oficial, Termux físico, ACT/DES Y6/CLASS-CAMB/H0, settings externos e replicação independente.
- **F_next:** preencher cada lacuna somente pela autoridade correspondente, mantendo resultados negativos e TOKEN_VAZIO residuais explícitos.
