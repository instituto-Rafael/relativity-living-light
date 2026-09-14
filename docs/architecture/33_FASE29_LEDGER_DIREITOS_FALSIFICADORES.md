# FASE 29 — Integridade Temporal, Direitos e Falsificadores

> **Estado:** `IMPLEMENTED_SECURITY_AND_SCIENCE_GATED`  
> **Claim boundary:** `claim_allowed=false`  
> **Data:** 2026-07-20

## 1. Correção conservadora

A primeira versão materializou D5, D6 e D7, mas a auditoria encontrou quatro classes de erro:

1. o sumário dizia `2 PASS`, embora `pass_ids` contivesse três elementos;
2. o texto de Delta AIC misturava AIC e BIC e o baseline colava ajustes com contagens de parâmetros diferentes;
3. F-COS-03 e F-COS-04 apontavam para artefatos que não continham os valores declarados;
4. acessibilidade pública foi tratada como domínio público ou CC-BY sem prova jurídica específica.

A versão v2 corrige essas fronteiras e acrescenta um gate não compensatório de trinta lentes.

## 2. Trinta lentes

```text
aritmética · licença · relógio · genealogia · assimetria
silêncio · redundância · reversibilidade · granularidade · fronteira
entropia · custódia · causalidade · ambiguidade · cobertura
desvio · identidade · proveniência · saturação · refutação
latência · diversidade · monotonicidade · fragilidade · observabilidade
proporcionalidade · independência · conservação · reparabilidade · legado
```

Contrato:

```text
data/contracts/fase29_integrity_lenses.v1.json
```

Regra:

\[
Q_{global}=PASS
\iff
\forall l\in L_{30},\;l=PASS
\]

Uma média não pode compensar uma lente falha.

## 3. D5 — Ledger temporal v2

Arquivo:

```text
results/state_transition_ledger.jsonl
```

Cada um dos 17 eventos possui:

- `effective_at`: quando o fato ocorreu;
- `recorded_at`: quando foi registrado no ledger;
- `backfill`: indica reconstrução histórica;
- `previous_event_sha256`;
- `event_sha256`;
- `supersedes`: somente evento anterior existente ou `null`;
- `claim_allowed=false`.

A cadeia começa em `GENESIS` e termina em:

```text
d7dc5da7736575f74bbb881d5f21ba4bdb36f0e3a7f16d216ca018b77e84c327
```

O hash torna mutação, remoção e reordenação observáveis. Ele não prova que a descrição histórica seja verdadeira; prova a integridade do ledger apresentado.

## 4. D6 — Direitos de datasets v2

Arquivo:

```text
data/contracts/dataset_rights_manifest.json
```

Estado conservador:

| Dataset | Acesso | licença verificada | treinamento | redistribuição |
|---|---|---:|---:|---:|
| Pantheon+SH0ES | público | não | bloqueado | bloqueada |
| DESI DR2 BAO | público | não | bloqueado | bloqueada |
| Moresco H(z) | cópia local | não | bloqueado | bloqueada |
| Planck 2018 priors | público | não | bloqueado | bloqueada |
| Dense Features | interno | não | bloqueado | bloqueada |

Princípio:

```text
publicly accessible != public domain != redistribution license != ML permission
```

Até que os termos exatos sejam arquivados e revisados:

```text
license_status       = TOKEN_VAZIO
training_allowed     = false
redistribution_allowed = false
rights_complete      = false
```

## 5. D7 — Falsificadores v2

### F-COS-01 — Delta AIC

A fonte Pantheon registra:

```text
N usado        = 1624
k_LCDM         = 2
k_RLL          = 4
chi2_LCDM      = 710.808
chi2_RLL       = 710.613
AIC_LCDM       = 714.808
AIC_RLL        = 718.613
DeltaAIC       = 3.805
```

\[
\Delta AIC=(\chi^2_{RLL}+2k_{RLL})-(\chi^2_{LCDM}+2k_{LCDM})=3.805
\]

### F-COS-02 — χ² reduzido

\[
\chi^2_{red}=710.613/(1624-4)=0.43865
\]

O threshold passa, mas o valor muito baixo abre auditoria de covariância, duplicação, nuisance parameters e distribuição de resíduos.

### F-COS-03 — \(z_t\)

A fonte correta é:

```text
results/rll_fase20_mcmc_bayes.json
```

Resultado:

```text
p16 = 4.66286
p50 = 11.54312
p84 = 17.31198
```

O critério convencional `[0.5, 1.5]` falha. Isso não prova sozinho ΛCDM.

### F-COS-04 — Bayes factor

Da fonte dynesty real:

\[
\ln B_{10}=\log Z_{RLL}-\log Z_{LCDM}
=-404.3402865-(-398.1500757)
=-6.1902108
\]

com incerteza combinada:

\[
\sigma_{\ln B}=0.6906527
\]

A comparação favorece fortemente ΛCDM **neste conjunto de dados, priors e implementação**.

### F-COS-05 — DESI nominal

```text
chi2_RLL  = 93.80609
chi2_LCDM = 28.96592
Delta     = 64.84017
```

O RLL passa o teto convencional `<150`, mas permanece muito pior que ΛCDM. Portanto:

```text
status           = PASS
promotion_effect = NONE
```

### Sumário derivado

```text
PASS         = 3
FAIL         = 2
TOKEN_VAZIO  = 0
claim_allowed = false
```

Contar votos não substitui interpretação científica.

## 6. Gate executável

```bash
python tools/validate_fase29_integrity.py --strict --write-report
python -m pytest -q tests/test_fase29_integrity.py
```

O gate verifica:

- trinta lentes exatas e únicas;
- fórmulas e contagens derivadas;
- correspondência threshold/status;
- existência dos artefatos-fonte;
- separação entre contextos Pantheon, joint Bayes e DESI nominal;
- direitos fail-closed;
- holdout bloqueado;
- owners, ações e critérios de saída;
- dupla temporalidade;
- monotonicidade de gravação;
- genealogia e SHA-256 de cada evento;
- fronteira `claim_allowed=false`.

Recibo:

```text
artifacts/fase29-integrity/validation.json
```

## 7. Estado de evidência

```text
source corrections        = IMPLEMENTED
thirty-lens validator      = IMPLEMENTED
adversarial tests          = IMPLEMENTED
workflow execution         = TOKEN_VAZIO até run observável
independent legal review   = TOKEN_VAZIO
independent reproduction   = TOKEN_VAZIO
training_allowed           = false
redistribution_allowed     = false
claim_allowed              = false
```

## 8. R3

```text
F_ok   = contexto estatístico separado, fontes corrigidas, direitos rebaixados e ledger encadeado
F_gap  = execução remota, termos jurídicos exatos, holdout, diagnóstico do χ² baixo e reprodução independente
F_next = executar o gate, corrigir falhas observáveis e só então decidir promoção da PR
```
