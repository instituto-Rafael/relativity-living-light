# RLL — Checklist de Robust Fit

**Status:** checklist operacional para transformar smoke/sanity test em bateria robusta.  
**Escopo:** comparação `LCDM` × `wCDM` × `CPL/w0waCDM` × `RLL` sem alterar dados brutos e sem sobrescrever resultados canônicos.

---

## 1. Regra de proteção

Nenhum robust fit deve:

- alterar `data/real/**`;
- sobrescrever `results/structure_d/joint_real_likelihood.json` canônico;
- mudar fórmulas cosmológicas;
- mudar bounds/priors sem registro explícito;
- declarar `claim_allowed=true` por interpretação posterior;
- declarar RLL vencedor sem gates completos.

Todo resultado robusto deve ser salvo em diretório ou arquivo versionado por seed, maxiter e timestamp.

---

## 2. Pré-checks leves

Executar antes de qualquer bateria:

```bash
python -m py_compile \
  rll_vs_lcdm.py \
  data/pipelines/structure_d/joint_real_likelihood.py \
  data/pipelines/structure_d/likelihood.py \
  src/rll/cosmology_fairness.py
```

Testes mínimos:

```bash
pytest \
  tests/test_likelihood_functions.py \
  tests/test_cosmology_fairness.py \
  tests/test_joint_real_likelihood.py \
  tests/test_synthetic_real_boundary.py
```

Se qualquer check falhar:

```text
estado = TOKEN_VAZIO_TEST_FAILURE
claim_allowed = false
próxima_medida = corrigir falha antes de fit robusto
```

---

## 3. Configuração smoke reproduzível

Objetivo: confirmar que a execução rasa atual é reprodutível.

```bash
STRUCTURE_D_JOINT_SEED=1 \
STRUCTURE_D_JOINT_MAXITER=3 \
python data/pipelines/structure_d/joint_real_likelihood.py
```

Registrar:

- commit;
- Python;
- NumPy/SciPy;
- seed;
- maxiter;
- hash dos inputs;
- hash dos outputs;
- `claim_allowed`;
- ranking por `chi2`, `AIC`, `AICc`, `BIC`;
- se `Os0=0.0` aparece.

Critério:

- se divergência não explicada aparecer, marcar `TOKEN_VAZIO_REPRODUCIBILITY`.

---

## 4. Bateria robusta mínima

Objetivo: testar estabilidade do ranking.

Configuração mínima:

```text
seeds = 1..10
maxiter = 100
tol = valor padrão ou registrado explicitamente
modelos = LCDM, wCDM, CPL/w0waCDM, RLL
```

Modelo de execução via wrapper seguro (recomendado):

```bash
python scripts/run_structure_d_robust_fit_matrix.py \
  --seeds 1,2,3,4,5,6,7,8,9,10 \
  --maxiter 100 \
  --existing-output-policy fail
```

Ou via variável de ambiente (pipeline direto):

```bash
for seed in 1 2 3 4 5 6 7 8 9 10; do
  STRUCTURE_D_JOINT_SEED=$seed \
  STRUCTURE_D_JOINT_MAXITER=100 \
  STRUCTURE_D_JOINT_OUTPUT_STEM="joint_real_likelihood_seed_${seed}_maxiter_100" \
  python data/pipelines/structure_d/joint_real_likelihood.py
done
```

> O suporte a `STRUCTURE_D_JOINT_OUTPUT_STEM` está implementado em `data/pipelines/structure_d/joint_real_likelihood.py` e `scripts/run_structure_d_joint_likelihood.py`. Stems canônicos são bloqueados pelo plan validator.

---

## 5. Tabela de coleta obrigatória

| Campo | Obrigatório | Observação |
|---|---:|---|
| commit | sim | SHA da execução |
| seed | sim | inteiro |
| maxiter | sim | 100 mínimo |
| model | sim | LCDM/wCDM/CPL/RLL |
| chi2 | sim | total |
| AIC | sim | com k correto |
| AICc | sim | N finito |
| BIC | sim | N documentado |
| N | sim | pontos efetivos |
| k | sim | parâmetros livres/nuisance |
| dof | sim | N-k |
| H0 | sim | fitted ou fixado |
| Om | sim | fitted ou fixado |
| OL | sim | fitted ou closure |
| w | se wCDM | `TOKEN_VAZIO` se não aplicável |
| w0 | se CPL | `TOKEN_VAZIO` se não aplicável |
| wa | se CPL | `TOKEN_VAZIO` se não aplicável |
| Os0 | se RLL | frequência de zero é métrica crítica |
| zt | se RLL | transição |
| wt | se RLL | largura |
| claim_allowed | sim | esperado false até gates completos |

---

## 6. Métricas derivadas

Calcular por seed e agregado:

- `delta_chi2_RLL_minus_LCDM`;
- `delta_AIC_RLL_minus_LCDM`;
- `delta_AICc_RLL_minus_LCDM`;
- `delta_BIC_RLL_minus_LCDM`;
- `delta_chi2_RLL_minus_CPL`;
- `delta_AIC_RLL_minus_CPL`;
- `delta_AICc_RLL_minus_CPL`;
- `delta_BIC_RLL_minus_CPL`;
- frequência de `Os0=0.0`;
- melhor modelo por seed;
- estabilidade do ranking.

---

## 7. Ablations obrigatórias

| Ablação | Pergunta | Resultado esperado |
|---|---|---|
| DESI+Hz apenas | expansão favorece RLL? | ranking por bloco de expansão |
| sem growth | proxy de crescimento enviesou ranking? | ranking sem `fsigma8` |
| sem CMB shift | CMB parcial enviesou ranking? | ranking sem CMB |
| DESI+Hz+CMB | CMB altera preferência? | delta contra CPL |
| DESI+Hz+growth | crescimento altera preferência? | delta contra CPL |
| RLL com `Os0>0` | camada RLL ativa melhora? | delta e penalização AICc/BIC |
| RLL contra CPL em grade `w_eff(z)` | RLL consegue aproximar CPL? | distância funcional |
| Pantheon+ completo | supernovas mudam ranking? | pendente até materialização |

Se uma ablação não for executada:

```text
estado = TOKEN_VAZIO_ABLATION
claim_allowed = false
```

---

## 8. Gates para avançar de smoke para robusto

| Gate | Condição | Se falhar |
|---|---|---|
| sintaxe | `py_compile` PASS | `TOKEN_VAZIO_TEST_FAILURE` |
| testes | pytest mínimo PASS | corrigir antes |
| saída versionada | não sobrescrever canônico | bloquear execução |
| seeds | 1..10 completas | `TOKEN_VAZIO_ROBUST_FIT` |
| métricas | chi2/AIC/AICc/BIC por modelo | bloquear claim |
| ranking | registrar vencedor por seed | sem interpretação forte |
| `Os0` | medir frequência de zero | investigar prior/bounds |

---

## 9. Gates para claim científico forte

`claim_allowed=true` só pode ser discutido se todos forem verdadeiros:

- robust fit concluído;
- outputs versionados;
- Pantheon+ materializado com covariância;
- CMB compressed likelihood completa;
- growth benchmark externo com CLASS/CAMB ou justificativa equivalente;
- RLL competitivo contra LCDM e CPL em critérios pré-registrados;
- incertezas/posterior documentados;
- ablações mínimas executadas;
- nenhum dado sintético usado como prova externa;
- nenhum parâmetro ajustado post-hoc sem registro.

Enquanto qualquer item faltar:

```text
claim_allowed = false
```

---

## 10. R3

```text
F_ok   = checklist robust fit definido; métricas e gates explícitos; suporte a output_stem verificado.
F_gap  = execução robusta ainda não materializada; bateria seeds 1..10 ainda pendente.
F_next = executar bateria seeds 1..10 com stems versionados usando scripts/run_structure_d_robust_fit_matrix.py.
```
