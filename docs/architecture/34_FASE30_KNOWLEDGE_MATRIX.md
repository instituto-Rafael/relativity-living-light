# FASE 30 — Knowledge Matrix: Orquestração Multi-dimensional

**Status**: IMPLEMENTADO  
**PR**: _pendente_  
**claim_allowed**: false (estrutural, não por lacuna)  
**generated_at**: 2026-07-28

---

## 1. Propósito

A Knowledge Matrix é o artefato de orquestração central do RLL: agrega e classifica
tudo que existe no repositório — fórmulas, conceitos, teses, gaps, observações,
validações, resultados e bridges — em uma estrutura multi-dimensional com integridade
dupla (SHA256 + BLAKE3), rastreabilidade de cadeia (timestamp acadêmico) e
retroalimentação bidirecional.

Nada é esquecido. Nada fica latente sem registro. Nada fica na fila sem estado.

---

## 2. Escala Biológica de Maturidade

| Biológico           | Classe                | Critério no repositório                        |
|---------------------|-----------------------|------------------------------------------------|
| medusa imortal      | `immortal_verified`   | VERIFIED + evidência multi-dataset             |
| equilíbrio          | `verified`            | VERIFIED em fonte                              |
| tartaruga           | `partial`             | PARTIAL ou READY_FOR_TEST                      |
| metamorfose         | `candidate`           | Hipótese com falsificador definido             |
| semente             | `seed`                | LATENT_SEED ou TOKEN_VAZIO com exit_criteria   |
| latente             | `latent`              | LATENT_ACTIVE sem exit_criteria concreto       |
| vazio epistêmico    | `void`                | TOKEN_VAZIO sem caminho ou BLOCKED             |

### Velocidade associada

| Maturidade                       | Velocidade    |
|----------------------------------|---------------|
| immortal_verified, verified      | medusa        |
| partial, candidate               | equilibrado   |
| seed, latent, void               | tartaruga     |

---

## 3. Papéis de Ecossistema

| Biológico         | Role              | Mapeado para                           |
|-------------------|-------------------|----------------------------------------|
| tubarão/baleia    | `apex_validator`  | falsifiers (F-COS-01..05)              |
| DNA/RNA           | `encoder`         | formulas                               |
| plâncton          | `base_concept`    | route_forest nodes                     |
| manguezal         | `buffer`          | rights/governance gaps                 |
| recife            | `accumulator`     | validated results e observações        |
| peixe             | `propagator`      | bridge contracts                       |
| catalisador       | `catalyst`        | theses com potencial transformativo    |

---

## 4. Integridade Dupla SHA256 + BLAKE3

Cada item carrega dois hashes calculados sobre o JSON canônico
`{"kind": ..., "label": ..., "source": ...}`:

```
sha256 = hashlib.sha256(canonical_json).hexdigest()
blake3 = blake3.blake3(canonical_json.encode()).hexdigest()
```

- **SHA256**: compatível com a cadeia existente do repositório (ledger, falsifier bundle)
- **BLAKE3**: mais rápido, resistente a length-extension attacks, nova dependência `blake3>=0.3`
- Se `blake3` não estiver disponível no ambiente, o builder usa fallback SHA256 com prefixo
  `blake3-fallback:` — os testes aceitam ambas as formas (ambas são hex64)

---

## 5. Cadeia de Timestamp Acadêmico

Análogo ao ledger de FASE 29, cada matrix gerada registra:

```json
{
  "matrix_id": "KM-RLL-20260728",
  "generated_at": "2026-07-28T...",
  "previous_matrix_sha256": "GENESIS",
  "matrix_sha256": "<sha256 dos item_ids>"
}
```

Isso cria uma cadeia verificável (blockchain-style sem blockchain):
cada geração referencia o hash da anterior.

---

## 6. Retroalimentação Multi-dimensional

Cada item tem:

```json
"retroalimentacao": {
  "feeds_into": ["KMIT-..."],
  "fed_by": ["KMIT-..."]
}
```

O builder infere as arestas do grafo:
- Teses geradas de gaps: `fed_by` aponta para o gap de origem
- Validações (falsifiers): `fed_by` lista as fórmulas que as alimentam
- Bridges: `feeds_into` aponta para conceitos que dependem delas

A integridade referencial é verificada em `test_retroalimentacao()`:
nenhum `item_id` referenciado pode estar ausente da matrix.

---

## 7. Geração de Hipóteses

Para cada gap com `queue_state=void`, o builder gera automaticamente
um item `kind=thesis, maturity_class=seed`:

```json
{
  "item_id": "KMHYP-...",
  "kind": "thesis",
  "maturity_class": "seed",
  "velocidade": "tartaruga",
  "origin_gap": "<gap_id>",
  "claim_allowed": false
}
```

As hipóteses são salvas tanto no `rll_knowledge_matrix.json` (items)
quanto em `knowledge_matrix_hypotheses.jsonl` (linha por hipótese).

---

## 8. Fontes Mineradas

| Fonte                                          | Itens  | kind         |
|------------------------------------------------|--------|--------------|
| `artifacts/formulas/formulas.json`             | 359    | formula      |
| `data/knowledge_forest/rll_route_forest_blueprint.json` | 17 | concept  |
| `data/epistemic_void/rll_epistemic_void.json` (records + possibilities) | 19 | gap/thesis |
| `data/omega_operational/rll_omega7_operational.json` | 7 | gap       |
| `data/real_sources/rll_latent_theses_registry.yml` | 6  | thesis       |
| `data/results/bootstrap/dense_behavior_features.json` | 19 | observation |
| `data/contracts/rll_falsifier_bundle.json`    | 7      | validation/gap |
| `data/contracts/*.v1.json` (bridges)          | 6      | bridge       |
| **Hipóteses geradas**                         | ≥3     | thesis (seed) |

---

## 9. Outputs

```
artifacts/knowledge-matrix/
├── rll_knowledge_matrix.json          # artefato master (claim_allowed=false)
├── knowledge_matrix_summary.json      # contagens por kind/maturity/queue
├── knowledge_matrix_hypotheses.jsonl  # hipóteses novas geradas
└── CHECKSUMS.sha256                   # integridade dos arquivos de saída
```

---

## 10. Workflow CI

Arquivo: `.github/workflows/concept-knowledge-matrix.yml`  
Job canônico: `build-knowledge-matrix`  
Triggers: push `**`, pull_request, workflow_dispatch  

```
steps:
  1. checkout (persist-credentials: false)
  2. setup Python 3.11 + pip cache
  3. pip install -r requirements.txt   # inclui blake3>=0.3
  4. python tools/build_knowledge_matrix.py --root . --outdir artifacts/knowledge-matrix
  5. python -m pytest -q tests/test_knowledge_matrix.py
  6. actions/upload-artifact@v4 → knowledge-matrix-{run_id}
```

---

## 11. Gate R3: F_ok / F_gap / F_next

| Critério       | Verificação                              | Status    |
|----------------|------------------------------------------|-----------|
| F_ok           | ≥100 items, todos 8 kinds presentes      | ✅ PASS   |
| F_gap          | nenhum gap sem queue_state               | ✅ PASS   |
| F_next         | ≥1 hipótese gerada de gap void           | ✅ PASS   |
| claim_boundary | claim_allowed=false em todos os itens    | ✅ PASS   |
| dual_hash      | sha256 + blake3 hex64 em todos os itens  | ✅ PASS   |
| retroalim.     | nenhuma referência pendente              | ✅ PASS   |

---

## 12. Rastreabilidade

- **Schema**: `schemas/rll_knowledge_matrix.schema.json`
- **Builder**: `tools/build_knowledge_matrix.py`
- **Testes**: `tests/test_knowledge_matrix.py` (10 testes)
- **Workflow**: `.github/workflows/concept-knowledge-matrix.yml`
- **FASE 29**: `docs/architecture/33_FASE29_LEDGER_DIREITOS_FALSIFICADORES.md`
