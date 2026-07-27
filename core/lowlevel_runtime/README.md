# lowlevel_runtime (Java → C → ASM)

Base autoral mínima para evolução de runtime determinístico sem GC.

## Estrutura
- `java/KernelBridge.java` — casca Java para chamada nativa.
- `include/kernel_bridge.h` — cabeçalho C da ponte.
- `c/kernel_bridge.c` — implementação C mínima sem libs externas do projeto.
- `asm/arch_detect_x86_64.S` — detecção de arquitetura via CPUID (x86_64).

## Objetivo
- ponto único de entrada para rotinas low-level;
- detecção de arquitetura em ASM;
- evolução para biblioteca autoral de runtime/JNI.

## Build de referência (local)
```bash
gcc -c core/lowlevel_runtime/asm/arch_detect_x86_64.S -o core/lowlevel_runtime/asm/arch_detect_x86_64.o
gcc -c core/lowlevel_runtime/c/kernel_bridge.c -Icore/lowlevel_runtime/include -o core/lowlevel_runtime/c/kernel_bridge.o
```


## Pantheon autoral freestanding (C)
- `include/pantheon_freestanding.h` — API mínima sem stdlib.
- `c/pantheon_freestanding.c` — hash FNV-1a, CRC32 bitwise e syscall write branchless (x86_64).

### Build de referência (freestanding, objeto)
```bash
gcc -ffreestanding -fno-builtin -nostdlib -c core/lowlevel_runtime/c/pantheon_freestanding.c -Icore/lowlevel_runtime/include -o core/lowlevel_runtime/c/pantheon_freestanding.o
```


### Limitações e garantias
- **Escopo:** este módulo "Pantheon freestanding" é runtime de baixo nível e **não** é o dataset cosmológico Pantheon+.
- **Garantias:** sem heap (`malloc`), sem `stdlib`, sem `stdio`, sem `string.h`, sem chamadas libc no módulo C.
- **FNV-1a 64-bit:** `offset_basis=14695981039346656037`, `prime=1099511628211`; hash **não criptográfico**.
  - Vetor conhecido: entrada `"123456789"` → `0x06d5573923c6cdfc`.
- **CRC32:** variante IEEE (poly reversed `0xEDB88320`, init `0xFFFFFFFF`, final xor `0xFFFFFFFF`).
  - Vetor conhecido: entrada `"123456789"` → `0xCBF43926`.
- **syscall:** `rll_sys_write1` usa syscall direta somente em **Linux x86_64**; fora desse alvo retorna `-38` (`ENOSYS`).

### Testes rápidos
```bash
pytest -q tests/test_pantheon_freestanding.py
gcc -ffreestanding -fno-builtin -nostdlib -c core/lowlevel_runtime/c/pantheon_freestanding.c -Icore/lowlevel_runtime/include -o /tmp/pantheon_freestanding.o
```

## RAFAELIA sqrt3_2 kernel Q16.16
- `rll_sqrt3_2_project_q16` aplica `sqrt(3)/2` como projeção/contração fixed-point.
- `rll_sqrt3_2_reverse_q16` aplica o inverso `2/sqrt(3)` como rota de rollback aproximada.
- `rll_sqrt3_2_decay_q16` implementa `R_{n+1}=Entrada_n+h*R_n` sem heap.
- `rll_sqrt3_2_hex_grid_q16` gera coordenadas de grid triangular/hexagonal em Q16.16.
- `rll_sqrt3_2_cosmo_pivot_q16` expõe `a_h=sqrt(3)/2` e `z_h=2/sqrt(3)-1` como pivô diagnóstico, não como constante cosmológica fundamental.
- `rll_sqrt3_2_spiral_step_q16` gera a próxima evolução espiral dimensional em setores de 60°, usando a altura do triângulo equilátero como componente `y`/altura auditável.

Build/teste focal:
```bash
pytest -q tests/test_sqrt3_2_freestanding_kernel.py
```

## Região canônica RLL em C freestanding
- `include/rll_canonical_region.h` — ABI fixa para observação, unidade, incerteza, proveniência, estado e recibo.
- `c/rll_canonical_region.c` — ingestão streaming sem heap/libc/floating point, conversão Q32.32 e falha fechada.
- Consome diretamente os blocos reais versionados de H(z), DESI DR2 BAO, fσ8/RSD e CMB Planck com covariância 3×3.
- Contrato atual: 65 observações canônicas (`33 + 13 + 16 + 3`), SHA-256 externo obrigatório e `claim_allowed=0`.
- Ausência de bloco obrigatório produz `RLLC_TOKEN_VAZIO`; dado sintético, incerteza inválida ou proveniência ausente é bloqueado.
- O adaptador de física/geofísica local permanece `LOCAL_CONTEXT_ONLY` e não satisfaz o gate cosmológico.

Build/teste focal:
```bash
gcc -std=c11 -Wall -Wextra -Werror -pedantic \
  -ffreestanding -fno-builtin -fno-stack-protector \
  -fno-asynchronous-unwind-tables -nostdlib -c \
  core/lowlevel_runtime/c/rll_canonical_region.c \
  -Icore/lowlevel_runtime/include \
  -o /tmp/rll_canonical_region.o
nm -u /tmp/rll_canonical_region.o
pytest -q tests/test_rll_canonical_region_freestanding.py
```

Contrato completo: [`docs/CANONICAL_REGION_FREESTANDING_C_V1.md`](../../docs/CANONICAL_REGION_FREESTANDING_C_V1.md).
