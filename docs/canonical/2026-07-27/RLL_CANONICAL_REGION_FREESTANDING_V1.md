# RLL Canonical Region — Freestanding C V1

**Estado:** `IMPLEMENTED_VERIFIED_LIMITED_LOCAL`  
**Data:** 2026-07-27  
**Claim científico permitido:** `false`

## Resultado

Este pacote materializa, em C freestanding, a região canônica das fontes de projeto já versionadas no RLL. Não é um exemplo, pseudocódigo ou novo banco paralelo. O núcleo é gerado diretamente de:

- `configs/project_sources_manifest.v1.json`;
- `data/receipts/project_sources_local_receipt_20260726.json`;
- `core/lowlevel_runtime/include/pantheon_freestanding.h`;
- `core/lowlevel_runtime/c/pantheon_freestanding.c`.

A tabela compilada contém:

- 14 fontes canônicas;
- 12 fontes com estado `VERIFIED_LOCAL_HASH` herdado do receipt;
- 1 fonte `metadata_only`;
- 1 fonte `PRIVATE_POINTER_ONLY`, sem nome de arquivo local no binário;
- 198 chunks registrados pelo pipeline de origem;
- os 14 SHA-256 dos corpos/pointers;
- relação RLL, visibilidade, política, fronteiras `NOT_EVIDENCE_FOR`, tamanho, linhas, resumo, próximo gate e hash FNV-1a do `source_id`.

## Fronteira freestanding

O objeto `rll_canonical_region.o` foi compilado com:

```sh
gcc -std=c11 -Wall -Wextra -Werror -pedantic \
  -ffreestanding -fno-builtin -fno-stack-protector -nostdlib \
  -c core/lowlevel_runtime/c/rll_canonical_region.c \
  -Icore/lowlevel_runtime/include \
  -o rll_canonical_region.o
```

Garantias observadas neste corte:

- sem `malloc`, heap ou GC;
- sem `stdlib.h`, `stdio.h` ou `string.h` no núcleo;
- sem filesystem, JSON, SQLite ou Python em runtime;
- sem BSS no objeto observado;
- único símbolo externo: `rll_fnv1a64`, já pertencente ao Pantheon freestanding do próprio RLL;
- lookup exato por `source_id`;
- validação fail-closed de metadados, políticas, limites, duplicatas, hashes de ID e fingerprint;
- frame binário little-endian fixo de 128 bytes.

## Frame canônico V1 — 128 bytes

| Offset | Tamanho | Campo |
|---:|---:|---|
| 0 | 8 | magic `RLLCRV1\0` |
| 8 | 4 | ABI |
| 12 | 4 | máscara de validação |
| 16 | 32 | contagens: fontes, verificadas, metadata, private, chunks, dimensões, missing, mismatch |
| 48 | 4 | fronteiras: claim/raw body/database |
| 52 | 4 | flags de custódia |
| 56 | 32 | digest registrado no receipt legado |
| 88 | 32 | SHA-256 dos bytes do manifesto realmente compilado |
| 120 | 8 | fingerprint FNV-1a 64 canônico |

## Divergência de custódia preservada

O receipt anterior registra:

```text
ccb546b713cc8c8a144cd50b90dac8dda57cde026df1a2b8b3141c56a8b51736
```

Os bytes atuais do manifesto em `main` produzem:

```text
3bf6e73eb25568648570ff90185d6ab4f7888124ca9b3892aee3772bb9419c0e
```

E correspondem ao Git blob:

```text
85cf806ec05e920c795f33d9687ba12a88761499
```

A semântica histórica do digest do receipt permanece `TOKEN_VAZIO_RECEIPT_DIGEST_SEMANTICS`. O núcleo não reescreve o receipt antigo e não declara igualdade falsa. Ele incorpora os dois valores e ativa:

```text
RLL_CUSTODY_COMPILED_MANIFEST_HASHED
RLL_CUSTODY_RECEIPT_DIGEST_DIVERGENCE_DECLARED
```

## Validação local observada

```text
pytest: 3/3 PASS
validation_mask: 0
source_count: 14
verified_local_hash_count: 12
metadata_only_count: 1
private_pointer_only_count: 1
chunk_count: 198
ARMv7 source lookup index: 12
unknown lookup: 0xffffffff
frame_size: 128
custody_flags: 0x00000005
fingerprint64: 0x8e4ad37ef3c2ec86
object: text=6252 data=2608 bss=0 total=8860
undefined symbols: rll_fnv1a64 only
```

O teste executável usa libc somente no **harness de teste** para imprimir o resultado; o objeto canônico permanece freestanding.

## Artefatos

- `core/lowlevel_runtime/include/rll_canonical_region.h`
- `core/lowlevel_runtime/c/rll_canonical_region.c`
- `core/lowlevel_runtime/generated/rll_canonical_project_sources.inc`
- `tools/generate_rll_canonical_region.py`
- `tests/test_rll_canonical_region.py`
- `data/receipts/rll_canonical_region_sandbox_receipt_20260727.json`

## Limites epistemológicos

Este núcleo prova materialização determinística dos metadados e dos digests versionados. Ele não prova que o conteúdo de uma fonte é cientificamente verdadeiro, não transforma matemática em lei física e não promove claim cosmológico, biológico ou fisiológico. `claim_allowed` permanece zero em toda a região.
