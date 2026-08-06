# RLL — Fila Executável Pós-Merge 2026-08-06 V1

**Commit-base:** `e7997693d4038f379aa0d960a3485f61e94d454b`  
**PRs já integradas:** `#645` e `#646`  
**Fronteira:** `claim_allowed=false`

## Invariante

```text
Catálogo/checkpoint != evidência materializada.
Arquitetura já implementada não deve ser duplicada.
Execução física exige receipt físico.
Proxy BIC != Bayes real.
Corpus privado permanece em custódia privada.
```

## O que já existe e foi retirado da fila

1. Contrato `E/C/H/P`, reconciliador da run `31066012098`, schema e fronteira pública.
2. Comparador `CPL/w0waCDM` no pipeline conjunto.
3. Matriz DESI 13×13 **block-diagonal** construída dos seis blocos 2×2 declarados.
4. Separação epistemológica da camada neuro/física/linguística.

Esses elementos não devem ser reconstruídos. Devem ser consumidos e fechados pelos gates restantes.

## Ordem operacional obrigatória

```text
P0-1 receipt CI pós-merge
  ↓
P0-2 replay físico Termux
  ↓
P0-3 nova run Pantheon
  ↓
P0-4 Pantheon full covariance
  ↓
P0-5 nested sampling/Bayes real
  ↓
P2 revisão científica independente
```

Em paralelo, após o receipt pós-merge:

```text
DESI adapter vetorial + fonte cross-block
CLASS/CAMB para fσ8
H0 formal
S8/weak lensing
ponte magnética observável
fontes primárias neuro/linguística
```

## P0 — não pode passar sem fazer

### 1. Receipt da suíte conjunta pós-merge

Os dois merges existem, mas ainda deve haver um receipt único provando a `main` conjunta. A soma de dois estados verdes não substitui uma execução sobre o estado combinado.

**Pronto quando:** pytest completo, schemas, governança e gate determinístico passam, com logs/JUnit/SHA ligados ao commit pós-merge.

### 2. Replay físico Termux

O runner existe, mas nenhum receipt físico retornou.

**Pronto quando:** dois ciclos byte-idênticos, device/model, `uname`, Python, hashes de entrada/saída, timestamp e commit.

### 3. Nova run científica Pantheon

A run `31066012098` continua historicamente falha. A correção de código só ganha classe executada quando uma nova run produzir novo artifact.

**Pronto quando:** novo `run_id`, sem `ModuleNotFoundError`, checksums internos e resultado `E/C/H/P` sem promover referência histórica.

### 4. Pantheon full covariance

A rota existe; os bytes oficiais e hashes não estão no GitHub público.

**Custódia correta:** bytes no Drive privado; no GitHub apenas provider ID sanitizado, tamanho, SHA-256, licença/autoridade e receipt.

### 5. Bayes real

`ln(B10)=-5.6682695` é proxy BIC de classe `C`, com gate desfavorável. Bayes real permanece `P` até nested sampling.

## P1 — fechamento observacional

### DESI

A matriz 13×13 atual prova apenas os blocos declarados. Falta adapter vetorial no fit, auditoria independente da transcrição e covariância oficial cross-block/joint quando disponível.

### H0

Há diagnóstico parcial, não likelihood formal Planck/SH0ES. Nenhum claim de alívio é permitido.

### S8 e lentes fracas

A função S8 existe, mas falta prior/likelihood versionado de weak lensing e custódia autorizada dos bytes.

### Crescimento

`fσ8` ainda usa proxy no joint real. É obrigatório benchmark CLASS/CAMB antes da migração.

### Magnetismo

FRB, Faraday e EB/TB são rotas de hipótese. Primeiro deve existir contrato dimensional `alpha_B/beta → observável`, limite nulo, priors e predição datada.

## P2 — credibilidade e publicação

### Neuro/física/linguística

A separação epistemológica já existe. O trabalho restante é um registry claim→fonte primária→trecho suportado→classe.

### Revisão independente

CI valida execução e contratos; não substitui peer review. A revisão deve registrar pessoa/grupo, conflito de interesse, commit revisado, críticas e respostas.

## F_ok

- #645 e #646 integradas;
- E/C/H/P e custódia integrados;
- w0wa já implementado;
- DESI 13D block matrix já implementada;
- camada neuro/linguística já separada.

## F_gap

- receipt pós-merge;
- Termux físico;
- nova run Pantheon;
- full covariance Pantheon;
- nested sampling;
- DESI joint/cross-block e adapter;
- H0/S8/crescimento;
- ponte magnética;
- fontes primárias;
- revisão independente.

## Regra de fechamento

```text
Fazer por dependência.
Registrar cada falha.
Não duplicar o que existe.
Não promover hipótese.
Não esconder resultado negativo.
```
