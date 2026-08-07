# RLL TOKEN_VAZIO Reconciliation V1

## Objetivo

Converter lacunas genéricas e incertezas em estados auditáveis sem fabricar conclusão.

O reconciliador distingue:

- `RESOLVED`: evidência materializada fecha positivamente a pergunta operacional;
- `RESOLVED_NEGATIVE`: a incerteza foi fechada por um resultado negativo/limite conhecido;
- `REDUCED`: um vazio amplo ficou obsoleto e foi substituído por lacunas menores e mais precisas;
- `OPEN_INTERNAL`: falta execução/código que pode ser realizado dentro do projeto;
- `OPEN_EXTERNAL`: falta dado, likelihood, aparelho ou autoridade externa;
- `OPEN_HUMAN`: falta replicação/revisão verdadeiramente independente;
- `OPEN_GOVERNANCE`: falta receipt de configuração/permissão;
- `OPEN_MIXED`: teoria + runtime/dado ainda precisam convergir;
- `OPEN_EVIDENCE_MISSING`: uma regra tentou fechar/reduzir um token, mas a evidência requerida faltou ou não satisfez as assertions.

`TOKEN_VAZIO` nunca é interpretado como zero, PASS ou ausência de problema.

## Estado efetivo desta revisão

Após materialização científica e auditoria do histórico Bayes:

```text
input_tokens       = 20
terminal_resolved  = 4
reduced_generic    = 2
open               = 14
claim_allowed      = false
publication_ready  = false
```

A contagem mede fechamento/narrowing do ledger desta revisão; não é percentual de verdade física do RLL.

## Mudanças de estado sustentadas

### 1. Full likelihood moderno de supernovas — `REDUCED`

`TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD` é amplo demais. A execução anterior já materializou Pantheon+ full covariance e DES-Dovekie full precision.

A revisão atual executou os sucessores relevantes e deixou de usar o token genérico como se o likelihood moderno inteiro estivesse ausente.

### 2. Common-nuisance Pantheon+ ↔ Dovekie — `RESOLVED`

A run GitHub Actions `31225058309` executou um companion Pantheon+ Hubble-flow-only com:

```text
H0 = 70 km/s/Mpc apenas como escala de referência
1 offset aditivo de magnitude perfilado analiticamente
mesma lógica de nuisance usada pelo likelihood Dovekie
```

Resultado materializado:

```text
Pantheon+ Hubble-flow: N = 1580
Δχ²(CPL−ΛCDM) = -0.4693068159
ΔBIC(CPL−ΛCDM) = +14.2610534361
Δχ²(RLL−ΛCDM) ≈ -2.73e-12
ΔBIC(RLL−ΛCDM) = +22.0955403781
RLL best Omega_s0 = 0

DES-Dovekie: N = 1820
Δχ²(CPL−ΛCDM) = -4.7924225030
ΔBIC(CPL−ΛCDM) = +10.2207610571
Δχ²(RLL−ΛCDM) ≈ -7.50e-8
ΔBIC(RLL−ΛCDM) = +22.5197752652
```

Portanto o mismatch de nuisance/H0 foi removido como explicação possível para a direção nula do RLL em SN-only. Isso fecha o gap operacional, mas o resultado científico continua desfavorável à necessidade dos parâmetros adicionais RLL.

### 3. Boundary sensitivity de CPL `wa` — `RESOLVED_NEGATIVE`

O fit original Dovekie encontrou `wa=-3`, exatamente no limite inferior. A revisão executou profile likelihood com grid:

```text
[-8, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3]
```

Todos os starts convergiram. O melhor ponto passou para:

```text
wa_best = -6
Δχ²(wa=-8) ≈ 0.0557
Δχ²(wa=-3) ≈ 1.2741
95% grid interval = [-8, -1]
left 95% exclusion = false
right 95% exclusion = true
```

Conclusão: o antigo `wa=-3` era boundary-sensitive. A pergunta antiga foi fechada negativamente; `wa` continua não identificado pelo lado inferior e o gap correto agora é:

```text
TOKEN_VAZIO_CPL_DOVEKIE_WA_LOWER_PROFILE_CLOSURE
```

### 4. Identificabilidade RLL em SN-only — `RESOLVED_NEGATIVE`

`TOKEN_VAZIO_RLL_SN_ONLY_PARAMETER_IDENTIFIABILITY` deixa de ser incerteza aberta. Pantheon+ e Dovekie materializados registram `BLOCKED_SN_ONLY`; os parâmetros de transição RLL não foram medidos nessa classe de dado.

A evidência seguinte deve vir de outros setores observacionais/perturbações, não de repetição indefinida do mesmo ajuste SN-only.

### 5. Bayes real genérico — `REDUCED`, não apagado

O repositório já contém uma execução formal histórica com `dynesty.NestedSampler`, `nlive=150`, `dlogz=0.5` e seed 42. O resultado armazenado é:

```text
log Z_RLL  = -404.3402864972 ± 0.5299056817
log Z_LCDM = -398.1500757348 ± 0.4429460223
ln(B10)    = -6.1902107624 ± 0.6906527421
```

Portanto `TOKEN_VAZIO_REAL_BAYES_INFERENCE` como afirmação de que “Bayes real nunca foi executado” é obsoleto.

Mas a execução histórica não fecha o gate moderno porque:

- CPL não foi incluído no mesmo nested run;
- o prior payload moderno não possui hash/registry comum aos três modelos;
- a versão do sampler não foi registrada no receipt histórico;
- não há replicação independente;
- não usa o contrato observacional moderno completo materializado em 2026.

O vazio foi estreitado para:

```text
TOKEN_VAZIO_REAL_BAYES_MODERN_3MODEL_PRIOR_LOCK
TOKEN_VAZIO_INDEPENDENT_REPLICATION
```

### 6. Licença explícita do upstream DES-SN5YR — `RESOLVED_NEGATIVE`

No commit upstream pinado `c9a4fcafc4cbd19bd750dee47fc76194a45c181f`, a auditoria verificou a ausência de `LICENSE`, `LICENSE.md`, `LICENCE` e `COPYING` no root e não encontrou grant explícito de redistribuição no README.

A conclusão operacional é conservadora:

```text
redistribution_allowed_by_this_audit = false
```

Isso não prova que nenhuma licença/permissão exista em Zenodo, ReadTheDocs, publicação ou outro canal; apenas impede que a redistribuição seja presumida.

## P0 ainda realmente aberto

Após retirar os vazios obsoletos, os P0 principais são:

1. `TOKEN_VAZIO_CPL_DOVEKIE_WA_LOWER_PROFILE_CLOSURE`;
2. `TOKEN_VAZIO_REAL_BAYES_MODERN_3MODEL_PRIOR_LOCK`;
3. `TOKEN_VAZIO_INDEPENDENT_REPLICATION`;
4. `TOKEN_VAZIO_DESI_DR2_OFFICIAL_REPRODUCTION`;
5. `TOKEN_VAZIO_PHYSICAL_EXECUTION`.

Os dois últimos exigem, respectivamente, produtos/likelihood oficial materializados e autoridade física Android/Termux. Replicação independente, por definição, não pode ser fechada por autorrepetição do mesmo projeto.

## P1/P2 preservados

P1 mantém ACT DR6, DES Y6 3x2pt, CLASS/CAMB + contrato explícito de perturbações RLL, H0 formal, configurações externas do GitHub e refresh coerente de `rll/release`.

P2 mantém arqueologia de refs e validação empírica/Termux/treino do UTM-185.

## Execução

```bash
python3 tools/rll_token_vazio_reconcile.py \
  --output artifacts/governance/RLL_TOKEN_VAZIO_RECONCILIATION_CURRENT.json
```

O reconciliador combina o ledger-base com overrides append-only. O ledger antigo permanece preservado; a projeção efetiva usa evidência mais nova sem reescrever a cadeia de custódia.

Código de saída:

- `0`: regras coerentes, mesmo que existam gaps externos/científicos legitimamente abertos;
- `2`: uma regra que deveria fechar/reduzir um token não conseguiu provar sua própria evidência.

```text
reconciler saudável != ciência concluída
```

## Anti-regressão

- estado terminal/reduzido exige arquivo de evidência + assertions;
- assertion falha → `OPEN_EVIDENCE_MISSING`;
- resultado negativo não promove `claim_allowed`;
- token genérico reduzido sai da fila efetiva e seus sucessores entram;
- overrides são append-only na visão longitudinal;
- receipt físico não pode ser substituído por CI/container;
- external likelihood não pode ser substituída por citação de paper;
- Bayes histórico não pode ser transplantado para likelihood moderno diferente;
- `claim_allowed=false` e `publication_ready=false` permanecem invariantes.

## R3

- **F_ok:** common-nuisance SN foi executado; boundary `wa=-3` foi diagnosticado; identificabilidade SN-only foi encerrada negativamente; Bayes histórico foi reconhecido e estreitado; licença upstream foi convertida em política conservadora.
- **F_gap:** evidência moderna 3-model Bayes, fechamento inferior de `wa`, DESI oficial, Termux físico, perturbações/CMB/LSS e replicação independente permanecem reais.
- **F_next:** fechar o restante por autoridade correta, sem converter ausência externa em PASS artificial.
