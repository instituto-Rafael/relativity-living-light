# Campo Entrópico do TOKEN_VAZIO — RLL

> Estado: camada estrutural e criativa, `claim_allowed=false`  
> Classe dominante: `[V]` vazio preservado  
> Regra: criatividade gera candidatos; evidência decide promoção.

## 1. O vazio como ambiente de pesquisa

No RLL, `TOKEN_VAZIO` não significa que algo é falso, inexistente ou impossível. Significa que a cadeia necessária para concluir ainda não está completa.

```text
ausência observada
→ desconhecidos nomeados
→ alternativas classificadas
→ hipóteses falsificáveis
→ condições de saída
→ artefato
→ teste
→ memória
```

O vazio deixa de ser uma omissão acidental e passa a ser uma unidade de trabalho auditável.

## 2. Entropia: fronteira de significado

Este módulo usa **entropia operacional** como uma convenção de roteamento `[C]`.

Ela conta:

- desconhecidos;
- possibilidades;
- contradições;
- condições de saída.

Ela **não** é:

- entropia termodinâmica;
- entropia de Shannon;
- evidência física;
- probabilidade;
- Bayes factor;
- pontuação de verdade.

A métrica usada no relatório é:

\[
L_{exploração}=N_{desconhecidos}+N_{possibilidades}+N_{contradições}
\]

e a prontidão de fechamento é:

\[
R_{fechamento}=\min\left(1,\frac{N_{condições\ de\ saída}}{\max(1,N_{desconhecidos}+N_{contradições})}\right)
\]

As duas são apenas instrumentos de organização.

## 3. Classes epistêmicas

| Classe | Papel |
|---|---|
| `[E]` | resultado verificável por cálculo, dado ou execução |
| `[C]` | convenção explícita adotada pelo projeto |
| `[H]` | hipótese com falsificador e observação prevista |
| `[P]` | parábola ou analogia; nunca conta como evidência |
| `[V]` | vazio preservado; falta cadeia suficiente para conclusão |

Uma possibilidade `[H]` é inválida no ledger se não possuir:

- falsificador;
- observação prevista;
- gate de promoção.

Uma possibilidade `[P]` deve permanecer analogia. Sua função é abrir linguagem e relações, não fechar um claim.

## 4. Estrutura executável

Fonte canônica:

```text
schemas/rll_epistemic_void.schema.json
data/epistemic_void/rll_epistemic_void.json
tools/validate_epistemic_void.py
tests/test_epistemic_void.py
```

Cada registro contém:

```yaml
id: EV-...
state: TOKEN_VAZIO
priority: P1
question: ...
known: [...]
unknowns: [...]
contradictions: [...]
possibilities:
  - classification: H
    falsifier: ...
    predicted_observation: ...
  - classification: P
    role: analogy
exit_conditions:
  - evidence_required: ...
    acceptance_criterion: ...
    artifact_path: ...
creative_boundary: creativity_generates_candidates_not_evidence
conclusion: null
claim_allowed: false
next_gate: ...
```

## 5. Invariantes

O schema e o validador bloqueiam:

1. conclusão em item ainda não resolvido;
2. hipótese sem falsificador;
3. hipótese sem observação prevista;
4. item `RESOLVED` sem evidência SHA-256;
5. IDs duplicados;
6. caminho de artefato absoluto ou com travessia `..`;
7. mesma frase declarada simultaneamente conhecida e desconhecida;
8. promoção de criatividade para evidência por simples narrativa.

## 6. Registros iniciais

O ledger começa com cinco campos vivos:

1. reconciliação temporal e precedência de resultados por linhagem;
2. crescimento de estruturas `f_sigma8`;
3. validação fora da amostra;
4. escopo de backend CMB por classe de claim;
5. evidência externa de branch protection.

Esses registros não declaram que uma hipótese é verdadeira. Eles definem o que precisa acontecer para que o vazio mude de estado.

## 7. Ciclo de estado

```text
TOKEN_VAZIO
→ PARTIAL ou READY_FOR_TEST
→ CONTRADICTION, se as evidências conflitarem
→ RESOLVED, somente com artefato auditável
```

`BLOCKED` indica que o gate é conhecido, mas depende de dado, permissão, ambiente ou configuração externa.

Nenhum registro histórico deve ser apagado silenciosamente. Quando resolvido, a evidência entra como evento rastreável.

## 8. Execução

```bash
python tools/validate_epistemic_void.py --strict --write-report
pytest -q tests/test_epistemic_void.py
```

Saídas:

```text
artifacts/epistemic-void/
├── epistemic_void_report.json
├── EPISTEMIC_VOID_REPORT.md
└── CHECKSUMS.sha256
```

## 9. Próximo vetor

O P0 atual é transformar os manifests científicos históricos em uma linhagem comparável e implementar o resolvedor de precedência por campo.

\[
R_3=\langle F_{ok}=vazio\ estruturado,\ F_{gap}=evidências\ históricas\ ainda\ não\ migradas,\ F_{next}=resolvedor\ de\ linhagem\rangle
\]

**O vazio permanece aberto, mas já não permanece sem direção.**
