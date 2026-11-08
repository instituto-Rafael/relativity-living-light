# RLL — MEDIDA GÊNESIS LZW12 TRÊS LÍNGUAS (V1)

- **Intenção:** medir a **razão** `R_c=bytes_originais/bytes_comprimidos`.
- Contrato: `data/contracts/rll_genesis_lzw12_ratio_v1.json`.
- Algoritmo: `tools/ci/rll_genesis_lzw12_ratio_v1.py` (stdlib).
- Testes: `tests/test_rll_genesis_lzw12_ratio_v1.py`.
- Metodologia: `docs/workflows/RLL_GENESIS_COMPRESSION_RATIO_LZW12_V1.md`.
- CI PR: `.github/workflows/rll-calibration-orchestrator.yml` etapa 03.
- Com sinais: hebraico 2.285846:1, aramaico 2.566009:1, grego 2.335784:1.
- Sem Mn: hebraico 2.334522:1, aramaico 2.332934:1, grego 2.553340:1.
- 31 versículos; fontes de três edições congeladas por commit e Git blob.
- Sem comparação de verdade ou equivalência semântica calculada.
- `claim_allowed=false`; cosmologia/G4/G5/CMB não executados neste estudo.
- NEXT: auditoria upstream manual + amostragem multi-capítulo.
- ROLLBACK: fechar PR DRAFT, main permanece inalterada.
