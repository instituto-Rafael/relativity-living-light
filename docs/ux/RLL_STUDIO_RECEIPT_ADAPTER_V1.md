# RLL Studio · Evidence Receipt Adapter V1

**Estado:** LAB / fail-closed  
**Contrato de origem:** `rll_evidence_receipt_v1`  
**Contrato de destino:** `rll-experiment-manifest/1.0.0`  
**Autoridade de claim da UI/adapter:** `NONE`

## Propósito

Conectar a superfície de produto já existente `RLL Evidence Runner V1` ao `RLL Studio` sem copiar ou reinterpretar autoridade científica.

```text
experiment YAML
→ Evidence Runner
→ receipt + hashes + decision
→ rll-evidence verify
→ Studio receipt adapter
→ Studio Manifest V1
→ visualização
```

A ordem é obrigatória. O adapter não aceita receipt cuja verificação não seja `PASS`.

## Mapeamento conservador

| Evidence Runner decision | Studio manifest | execution | claim |
|---|---|---|---|
| `VERIFIED_LIMITED` | `OBSERVED_LIMITED` | `PASS` | `BLOCKED` |
| `TOKEN_VAZIO_REQUIRED_INPUT` | `TOKEN_VAZIO` | `BLOCKED` | `BLOCKED` |
| `TOKEN_VAZIO_RESULT` | `TOKEN_VAZIO` | `PASS` | `BLOCKED` |
| `BLOCKED_EXECUTION` | `BLOCKED` | `FAIL` | `BLOCKED` |

Nenhum estado do Evidence Runner V1 é convertido em `claim.allowed=true`.

## Proveniência preservada

O manifest derivado carrega:

- SHA-256 integral do receipt;
- SHA-256 semântico;
- SHA-256 do experimento;
- commit observado;
- caminho do receipt de origem;
- versão do adapter;
- estado explícito da verificação;
- inputs e seus hashes na biblioteca/evidência;
- steps executados;
- extrações e comparações;
- `F_gap` e `F_next` do receipt de origem.

O adapter chama o verificador do próprio Evidence Runner para também detectar alteração dos arquivos de input/output referenciados pelo receipt.

## Execução

```bash
rll-evidence --repository-root "$PWD" verify artifacts/evidence/receipt.json

python tools/rll_studio_receipt_adapter.py \
  artifacts/evidence/receipt.json \
  --repository-root "$PWD" \
  --output artifacts/rll-studio/manifest.json
```

## Same-head CI

O workflow `RLL Studio Contract` executa a rota real do repositório:

```text
RLL-EVIDENCE-JOINT-REAL-001
→ materializa receipt
→ verifica receipt
→ adapta para Studio Manifest
→ valida JSON Schema
→ exige claim.allowed=false
→ preserva todos os outputs como artifact
→ emite studio-ci-receipt.json
```

Este gate demonstra interoperabilidade executável entre dois componentes reais do repositório. Não demonstra usabilidade física, validação cosmológica, replicação independente ou publicação científica.

## Ledger de lacunas

A fila governada está em:

`data/governance/RLL_STUDIO_UX_GAPS_V1.json`

Ordem atual:

1. `P0` same-head real receipt adapter CI;
2. `P0` Android humano físico;
3. `P1` desktop humano;
4. `P1` tecnologia assistiva;
5. `P1` matriz multi-browser;
6. `P2` PWA/offline, bloqueado até os P0 de usabilidade.

Cada item possui autoridade, `TOKEN_VAZIO`, closure test e next producer. Ausência de evidência não é convertida em falha nem sucesso.

## Invariantes

```text
receipt_integrity != scientific_validation
adapter_PASS != scientific_PASS
CI_PASS != human_usability_PASS
UI_AUTHORITY=NONE
claim_allowed=false
TOKEN_VAZIO != zero
```

## R3

- **F_ok:** contrato executável receipt → manifest, preservação de proveniência, testes adversariais e CI same-head.
- **F_gap:** Android/desktop humano, tecnologia assistiva e browser matrix dependem de observação física/humana.
- **F_next:** fechar primeiro o gate same-head; depois executar o protocolo humano Android sem substituí-lo por CI.
