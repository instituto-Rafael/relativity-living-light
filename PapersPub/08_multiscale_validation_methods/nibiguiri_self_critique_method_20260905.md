# RLL — NIBIGUIRI Self-Critique Discovery Engine — 2026-09-05

**State:** `IMPLEMENTED / YAML_DRIVEN / SELF_CRITIQUE / NO_AUTO_PROMOTION`  
**Canonical context:** `From the Observed Void to Recurrence`  
**Source program:** `16 thesis programs + 32 mathematical hypotheses = 48 units`  
**Audit geometry:** `12 lenses × 48 units = 576 explicit cells`  
**Candidate discovery:** `12 seed candidates = 8 hypothesis + 2 lemma + 2 thesis-program candidates`  
**claim_allowed:** `false` beyond the declared structural validation.

## 0. What was still missing

The earlier NIBIGUIRI-12 document correctly named twelve methodological directions, but it still had an unclosed operational gap: the 48×12 matrix was described as `F_next` rather than materialized as a configuration and executable discovery mechanism.

This successor closes that implementation gap without pretending that automatic text generation is proof.

The method now has five separate layers:

```text
research registry (48 current units)
        ↓
YAML self-critique contract (12 lenses / 6 oppositions)
        ↓
explicit 576-cell matrix seed
        ↓
deterministic Python discovery/audit engine
        ↓
candidate registry + receipt
```

Candidates never enter the canonical T/H registry automatically.

## 1. Twelve overlooked items, one per isogonic direction

### N01 — 000° — scale preservation
The previous method corrected rational reduction only after the distinction `77/33 != 7/3` as scale-bearing geometry was forced into the model. The missing generalized question was whether every research unit stores the unreduced state, units, dimension and scale before applying an invariant.

### N02 — 030° — orientation / transformations
The program had invariants but no universal requirement to declare the equivalence group first. Without that contract, sign, chirality, reflection and coordinate changes can create false identities or false novelty.

### N03 — 060° — local → global
Several discoveries began from one triangle/face before a complete orbit/incidence scan. The missing method must force every local identity through all global classes before global promotion.

### N04 — 090° — finite → asymptotic
The program contains strong finite evidence at `f=2`, `mod 7`, and `n<=14000`. What was still underimplemented was a systematic generator of the questions: `family? limit? rate? error term? threshold?`.

### N05 — 120° — direct → inverse/fibres
Forward formulas were much richer than their preimages. The missing method must treat `F^-1(y)` as a set/fibre when needed and ask cardinality, branch structure, compatibility and reconstruction conditions.

### N06 — 150° — internal → external
Prior-art/null-model review was a gate, but not a discovery operator. The new engine explicitly asks what known construction, baseline or change of variables could explain the same effect before novelty is promoted.

### N07 — 180° — compression / sufficient state
After correcting excessive reduction, the opposite error becomes over-preservation. The missing question is the minimum lossless state that reconstructs the relevant geometry.

### N08 — 210° — quotient / coordinate artifact
The program names semantic namespaces, but it did not operationalize quotienting coordinate duplicates. The new method asks for intrinsic object, representation, equivalence class and canonical form separately.

### N09 — 240° — global → local residual
Global closure (`4π`, spectrum, averages, counts) can hide exceptional local classes. The new method forces residual/outlier localization by vertex, face, residue, module or orbit.

### N10 — 270° — asymptotic → finite exceptions
`O(f^-2)`-type hypotheses do not specify where they begin to work. The missing dual question is the smallest valid regime and the complete finite exception catalogue.

### N11 — 300° — inverse → mechanism
An algebraic inverse was at risk of being interpreted semantically as reverse dynamics. The new method requires separate fields for inverse relation, generative dynamics, causal model and physical mechanism.

### N12 — 330° — evidence → anti-evidence
The repository is strong at hashes/receipts/CI, but those can authenticate a wrong claim. The new method explicitly asks for the observation or counterexample that would defeat the claim even with perfect custody.

## 2. YAML as the operational contract

File:

`nibiguiri_self_critique_engine_20260905.v1.yml`

The YAML contains:

- all 12 lenses with exact `0,30,...,330°` positions;
- involutive 180° opposite pairs;
- one adversarial probe template per lens;
- one discovery operator per lens;
- one seed candidate per lens;
- mandatory falsifier per candidate;
- no-auto-promotion gate;
- prior-art default `TOKEN_VAZIO_PRIOR_ART`;
- proof default `TOKEN_VAZIO_PROOF`;
- counterexample-search default `TOKEN_VAZIO_COUNTEREXAMPLE_SEARCH`;
- method-self-audit questions;
- anti-gaming gates;
- promotion contracts for hypothesis and thesis-program candidates.

The method itself is an audit target. It is not exempt because it produced the other audits.

## 3. The explicit matrix

File:

`nibiguiri_self_critique_matrix_seed_20260905.v1.yml`

It contains all **576 cells** explicitly:

```text
T01..T16 × N01..N12
H01..H32 × N01..N12
```

Initial state:

`TOKEN_VAZIO_NOT_AUDITED`

This is intentional. Creating the matrix is not evidence that a cell has been audited.

## 4. Candidate discovery produced by the first self-critique pass

The first YAML-configured pass produced the following **unpromoted** candidates:

1. **SC01 / LEMMA_CANDIDATE / N01** — Suficiência da decomposição primitivo × escala sob equivalência declarada. Testar se vetor primitivo + gcd/escala + metadados de orientação/grupo bastam para reconstrução lossless. Falsificador: dois estados geometricamente distintos compartilharem exatamente essa representação.
2. **SC02 / HYPOTHESIS_CANDIDATE / N02** — Assinatura canônica de órbita sob grupo de equivalência. Falsificador: duas órbitas não equivalentes com a mesma assinatura proposta.
3. **SC03 / HYPOTHESIS_CANDIDATE / N03** — Fechamento por órbitas das identidades locais icosaédricas. Falsificador: relação local exata fora das órbitas geradas pelo conjunto candidato.
4. **SC04 / HYPOTHESIS_CANDIDATE / N04** — Monotonicidade eventual dos erros geométricos de icosferas. Falsificador: infinitos `f` acima de qualquer limiar com aumento do erro normalizado.
5. **SC05 / LEMMA_CANDIDATE / N05** — Cardinalidade das fibras da dobra modular e composição CRT. Falsificador: resíduo cuja fibra contradiga a fórmula de cardinalidade derivada.
6. **SC06 / THESIS_PROGRAM_CANDIDATE / N06** — Equivalência e não-equivalência por prior art das famílias 7/42/420. Falha: se todas forem apenas estruturas clássicas sem invariante residual, novidade desaparece e resta apenas classificação.
7. **SC07 / HYPOTHESIS_CANDIDATE / N07** — Representação mínima lossless da geometria racional com escala. Falsificador: remover um campo e ainda reconstruir univocamente todos os estados do domínio.
8. **SC08 / HYPOTHESIS_CANDIDATE / N08** — Completude de uma forma canônica por quociente. Falsificador: invariante material que não possa ser recuperado da forma canônica.
9. **SC09 / HYPOTHESIS_CANDIDATE / N09** — Localização dos resíduos globais por classe de incidência. Falsificador: resíduos relevantes indistinguíveis entre as classes declaradas.
10. **SC10 / HYPOTHESIS_CANDIDATE / N10** — Limiar finito de validade para aproximações `f^-2`. Falsificador: violações arbitrariamente grandes acima de todo `f0` candidato.
11. **SC11 / HYPOTHESIS_CANDIDATE / N11** — Bacia admissível das iterações inversas do operador midpoint Möbius. Falsificador: provar que toda órbita inversa do domínio algébrico permanece geometricamente realizável.
12. **SC12 / THESIS_PROGRAM_CANDIDATE / N12** — Grafo dual claim–falsificador para custódia matemática. Falsificador: se o DAG dual não aumentar a detecção de claims mal suportados num corpus de controle, a extensão é rejeitada.

Nenhum `SCxx` é automaticamente renomeado para `H33+` ou `T17+`.

## 5. Candidate counts

```text
HYPOTHESIS_CANDIDATE     = 8
LEMMA_CANDIDATE          = 2
THESIS_PROGRAM_CANDIDATE = 2
TOTAL                    = 12
```

Candidate Merkle root da execução local equivalente:

`3d65d11b30b7c54cb06bea030e6dbf771e2d863c66a56f91d4f477b1a88c0a03`

Expanded 576-cell matrix SHA-256 da execução local equivalente:

`cc7a4a8deb2fcb2eb98e0f2bd9b6db08a9a6113d20531f6ee3fb5d181ee7aaa3`

Hash é proveniência, não prova.

## 6. Autocritique of NIBIGUIRI itself

The method must answer its own questions before being treated as mature:

1. Do 12 lenses create new blind spots?
2. Is 30° spacing merely an operational visualization, or has anyone silently treated it as a theorem?
3. Are some opposite pairs duplicates in different language?
4. Are seed candidates confirmation-biased toward the current corpus?
5. Does one lens overproduce candidates and inflate apparent productivity?
6. Which candidates duplicate `T01..T16/H01..H32` semantically?
7. Which `FAIL/TOKEN_VAZIO` states must block promotion?
8. Does the method seek counterexamples with the same priority as extensions?

Until answered, the method itself remains partially `TOKEN_VAZIO_METHOD_VALIDATION`.

## 7. Anti-gaming gates

```text
candidate_count != quality
hash != proof
CI != theorem
same_number != same_object
same_cardinality != isomorphism
generated_candidate != promoted_hypothesis
NOT_APPLICABLE requires reason
negative results remain append-only
opposite lens must be evaluated
prior art precedes novelty
```

## 8. Execution

```bash
python PapersPub/08_multiscale_validation_methods/scripts/run_nibiguiri_self_critique.py
```

Expected structural output:

```text
matrix_cells = 576
candidate_count = 12
hypothesis candidates = 8
lemma candidates = 2
thesis-program candidates = 2
structural_validation = PASS
```

## 9. Local structural evidence

Equivalent authored content was exercised locally with **18/18 unittest PASS**.

This proves only deterministic structural behavior of the configured method. It does not prove the new mathematical candidates, novelty, prior art, or physical interpretation.

## 10. Promotion logic

A candidate may be considered for the canonical H/T registry only after:

```text
domain declared
units/assumptions declared when applicable
falsifiable statement
counterexample path
prior-art review
non-duplication or explicit difference from existing unit
material NIBIGUIRI lenses resolved
```

Thesis-program candidates additionally need multiple independent research questions, an evaluation protocol and a declared failure condition.

## R3

```text
F_ok =
  NIBIGUIRI moved from prose-only audit to YAML-driven executable self-critique;
  576 cells are explicit;
  12 candidates are generated but unpromoted;
  the method audits itself;
  18/18 structural tests PASS locally

F_gap =
  semantic evaluation of each of 576 cells;
  prior-art review for SC01..SC12;
  proof/counterexample work per candidate;
  provider CI for this successor

F_next =
  fill cells with evidence rather than prose;
  reject/merge duplicates;
  only then promote surviving SC candidates into H/T successor registries
```
