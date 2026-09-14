# RLL_BALANCE_REPORT_TEMPLATE — Relatório da Balança

> Repositório: `relativity-living-light`  
> Ponte: Livro Vivo RAFAELIA  
> Status: `FORMALIZACAO_READY`  
> Regra: a balança só ensina quando o peso é escrito

## 1. Parábola do escrivão da balança

O mestre colocou a hipótese em um prato.

No outro, colocou os modelos de comparação.

A balança se moveu.

O discípulo viu o movimento e disse:

— Já entendi.

O mestre respondeu:

— Ainda não. Enquanto o peso não for escrito, amanhã tua memória pode mudar o resultado.

Chamou então o escrivão.

O escrivão não opinava sobre qual prato deveria vencer.

Ele apenas registrava:

```text
quem pesou
o que foi pesado
qual dado entrou
qual métrica decidiu
qual prato venceu
qual limite ficou
qual teste vem depois
```

O discípulo perguntou:

— Mestre, o escrivão não torna a hipótese mais bela.

O mestre respondeu:

— Não. Ele torna a hipótese mais honesta.

Assim nasce este template.

---

## 2. Invariante

```text
resultado bruto → métrica comparada → decisão → limite → próximo teste
```

Forma compacta:

```math
Inv(Relatório)=ResultRaw \rightarrow Metrics \rightarrow Decision \rightarrow Limitations \rightarrow NextTest
```

---

## 3. Cabeçalho do relatório

```yaml
report_id: "YYYYMMDD-HHMM-rll-balance"
run_id: ""
repository: "relativity-living-light"
status_epistemologico: "RESULTADO_COMPUTACIONAL"
dataset:
  name: ""
  type: "DADO_REAL|SIMULACAO|MISTO|TOKEN_VAZIO"
  n: null
config:
  seed: null
  maxiter: null
  tolerance: null
  priors: []
artifacts:
  raw_results: ""
  report_md: ""
  figures: []
```

---

## 4. Tabela de modelos

| Modelo | χ² | AIC | AICc | BIC | Evidência | Bayes factor | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| RLL | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | HIPOTESE_AUTORAL |
| ΛCDM | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | BASELINE |
| wCDM | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | BASELINE |
| CPL | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | TOKEN_VAZIO | BASELINE |

---

## 5. Decisão da balança

Escolher um estado:

```text
RLL_VENCE
RLL_PERDE
RLL_EMPATA
RLL_COLAPSA_BASELINE
DADOS_INSUFICIENTES
EXECUCAO_INVALIDA
```

Decisão:

```yaml
decision_state: "TOKEN_VAZIO"
winner: "TOKEN_VAZIO"
reason: ""
confidence_note: ""
```

---

## 6. Limites obrigatórios

```text
1. Quais dados foram usados?
2. O dataset é real, sintético ou misto?
3. Quais priors foram usados?
4. A execução é reprodutível?
5. O resultado depende fortemente de seed?
6. Algum modelo colapsou para outro?
7. O baseline venceu em alguma métrica?
8. O que ainda é TOKEN_VAZIO?
```

---

## 7. Como escrever derrota honesta

Usar linguagem assim:

```text
Nesta execução, RLL não superou os baselines declarados sob as métricas usadas.
Isso não prova falsidade universal do programa RLL, mas indica F_gap operacional:
melhorar modelo, dados, priors, implementação ou hipótese.
```

Não usar:

```text
O resultado não importa porque a hipótese é bonita.
```

---

## 8. Como escrever vitória cautelosa

Usar linguagem assim:

```text
Nesta execução, RLL superou os baselines declarados sob as métricas usadas.
O resultado exige repetição com novos dados, priors declarados, seeds diferentes e revisão independente.
```

Não usar:

```text
RLL está provado.
```

---

## 9. Próximo teste

```yaml
next_test:
  objective: ""
  dataset: ""
  metric: ""
  expected_failure_mode: ""
  artifact_to_generate: ""
```

---

## 10. Parábola final — A tinta que não torce o peso

O discípulo perguntou ao escrivão:

— Tu preferes que meu modelo vença?

O escrivão respondeu:

— Minha tinta não escolhe prato.

— Então para que serves?

— Para que, quando o tempo passar, ninguém diga que a balança falou outra coisa.

E escreveu:

```text
peso medido → palavra fiel → próxima investigação
```

---

## 11. Retroalimentar[3]

- **F_ok:** há agora um template para transformar comparação RLL em relatório auditável.
- **F_gap:** falta script que leia JSON real e preencha o template automaticamente.
- **F_next:** criar `scripts/rll_balance_report.py`.
