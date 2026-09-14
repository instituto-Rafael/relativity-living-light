# RLL — Output Stem CLI Gap

**Status:** fechado — mitigado por wrapper seguro, suporte a env/CLI no pipeline e testes.  
**Escopo:** impedir sobrescrita acidental dos artefatos canônicos em `results/structure_d/`.

---

## 1. Fato observado

O pipeline possui a função:

```python
run_joint_likelihood(output_stem: str = "joint_real_likelihood")
```

Essa função escreve os arquivos com base em `output_stem`:

```text
results/structure_d/{output_stem}.csv
results/structure_d/{output_stem}.json
results/structure_d/{output_stem}_covariance_manifest.json
```

Porém o `main()` atual chama:

```python
payload = run_joint_likelihood()
```

Sem ler uma variável como `STRUCTURE_D_JOINT_OUTPUT_STEM` e sem aceitar argumento CLI.

---

## 2. Risco

Se uma bateria robusta for executada diretamente com:

```bash
STRUCTURE_D_JOINT_MAXITER=100 python data/pipelines/structure_d/joint_real_likelihood.py
```

ela tende a escrever no `output_stem` padrão:

```text
joint_real_likelihood
```

Isso pode sobrescrever ou substituir os artefatos canônicos atuais:

```text
results/structure_d/joint_real_likelihood.csv
results/structure_d/joint_real_likelihood.json
results/structure_d/joint_real_likelihood_covariance_manifest.json
```

Mesmo com escrita atômica e backups, isso cria risco de confusão entre:

- smoke atual;
- robust fit;
- seeds diferentes;
- maxiter diferente;
- resultados canônicos;
- resultados experimentais.

---

## 3. Classificação RAFAELIA

```text
estado = TOKEN_VAZIO_CLI_OUTPUT_STEM
objeto = output stem versionado para execuções robustas
risco_se_ignorar = sobrescrita ou mistura de artefatos smoke e robust fit
valor_da_lacuna = protege rastreabilidade e impede falso claim por arquivo reusado
claim_allowed = false
```

---

## 4. Correção recomendada

Antes de executar robust fit, criar PR específico para uma destas opções:

### Opção A — variável de ambiente

```python
output_stem = os.environ.get("STRUCTURE_D_JOINT_OUTPUT_STEM", "joint_real_likelihood")
payload = run_joint_likelihood(output_stem=output_stem)
```

### Opção B — argumento CLI

```bash
python data/pipelines/structure_d/joint_real_likelihood.py \
  --output-stem joint_real_likelihood_seed_1_maxiter_100
```

### Opção C — wrapper robusto separado

Criar script:

```text
scripts/run_structure_d_robust_fit_matrix.py
```

Responsável por:

- iterar seeds;
- definir maxiter;
- gerar output stem versionado;
- nunca sobrescrever canônico;
- consolidar tabela agregada.

---

## 5. Regra de bloqueio

~~Enquanto o output stem versionado não estiver implementado ou garantido por wrapper:~~

A lacuna foi fechada. O output stem versionado está implementado em dois caminhos operacionais:

1. `scripts/run_structure_d_joint_likelihood.py` — wrapper seguro com `STRUCTURE_D_JOINT_OUTPUT_STEM` e `--output-stem`.
2. `data/pipelines/structure_d/joint_real_likelihood.py` — `main()` lê `STRUCTURE_D_JOINT_OUTPUT_STEM` via `_resolve_main_output_stem()`.

Para execuções que não devem sobrescrever o canônico:

```text
robust_fit_execution_allowed = condicionado a uso do stem versionado
```

---

## 6. Critério de aceite

**Cumprido.** A lacuna está fechada com dois caminhos operacionais comprovados:

```bash
# Caminho 1 — wrapper seguro
STRUCTURE_D_JOINT_OUTPUT_STEM="joint_real_likelihood_seed_1_maxiter_100" \
STRUCTURE_D_JOINT_SEED=1 \
STRUCTURE_D_JOINT_MAXITER=100 \
python scripts/run_structure_d_joint_likelihood.py

# Caminho 2 — pipeline direto via env
STRUCTURE_D_JOINT_OUTPUT_STEM="joint_real_likelihood_seed_1_maxiter_100" \
STRUCTURE_D_JOINT_SEED=1 \
STRUCTURE_D_JOINT_MAXITER=100 \
python data/pipelines/structure_d/joint_real_likelihood.py
```

Ambos geram:

```text
results/structure_d/joint_real_likelihood_seed_1_maxiter_100.json
results/structure_d/joint_real_likelihood_seed_1_maxiter_100.csv
results/structure_d/joint_real_likelihood_seed_1_maxiter_100_covariance_manifest.json
```

sem alterar o canônico:

```text
results/structure_d/joint_real_likelihood.json
results/structure_d/joint_real_likelihood.csv
results/structure_d/joint_real_likelihood_covariance_manifest.json
```

---

## 7. R3

```text
F_ok   = lacuna de output_stem fechada; wrapper seguro, suporte a env/CLI no pipeline e testes.
F_gap  = nenhum gap pendente para output stem; robust fit pode usar stems versionados.
F_next = executar bateria robusta (seeds 1..10, maxiter 100) com stems versionados e registrar resultados.
```
