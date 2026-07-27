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


## Região canônica de acoplamento freestanding
- `include/rll_canonical_coupling.h` — tipos, unidades, estados e políticas de região.
- `c/rll_canonical_coupling.c` — acoplamento Q16.16 sem heap/libc entre observações, modelos, incertezas, proveniência e recibos.
- separa evidência cosmológica, contexto geofísico local, operadores geométricos exatos, referências de gravidade forte, dados sintéticos e `TOKEN_VAZIO`;
- nunca promove geofísica local, geometria exata ou fixture sintética a evidência cosmológica;
- acumula contribuição `chi²` apenas para observações cosmológicas tipadas com unidade, incerteza, calibração, hash e modelo registrado;
- gera recibo determinístico FNV-1a/CRC32 com `claim_allowed=0`;
- valida objetos host, ARMv7 e AArch64.

Comando canônico único:
```bash
python3 tools/validate_rll_canonical_freestanding.py --write-report
```

## Ingestão canônica dos dados reais
- `include/rll_canonical_region.h` — ABI fixa para observação, unidade, incerteza, SHA-256, estado e recibo de ingestão.
- `c/rll_canonical_region.c` — parser streaming Q32.32, sem heap/libc/floating point, que alimenta a região de acoplamento com arquivos reais versionados.
- consome H(z), DESI DR2 BAO, fσ8/RSD e CMB Planck com covariância 3×3;
- contrato atual: 65 observações (`33 + 13 + 16 + 3`), `claim_allowed=0` e `TOKEN_VAZIO` se faltar qualquer bloco;
- rejeita sintético, sigma não positiva, schema inválido ou SHA-256 ausente;
- o bridge geofísico/sensorial continua `LOCAL_CONTEXT_ONLY` e não completa o gate cosmológico.

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
