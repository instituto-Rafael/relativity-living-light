# Arquitetura Freestanding FLL/FRLL — Contrato Canônico

## 1. Função

Este documento define a fronteira executável do formalismo FLL/FRLL. O núcleo recebe evidência já extraída, opera apenas com memória fornecida pelo chamador e devolve uma distribuição entre quatro hipóteses, coerência relacional, incerteza e confiabilidade.

## 2. Fronteira de claims

- `VERIFIED`: resultado reproduzido a partir de entrada, modelo e hash registrados;
- `DECLARED_BY_AUTHOR`: parâmetro ou interpretação ainda não validado externamente;
- `TOKEN_VAZIO`: ausência de evidência suficiente;
- `CONTRADICTION`: a evidência contradiz a hipótese ou o contrato.

## 3. Estado

\[
X\in Q16.16^{20\times14\times3}
\]

\[
Z\in Q16.16^9
\]

\[
H=\{H_R,H_S,H_P,H_T\}
\]

## 4. Redução

\[
\bar x_i=\sum_{d=1}^{14}\sum_{s=1}^{3}\omega_d\beta_sX_{i,d,s}
\]

## 5. FLL

\[
L_h=b_h+\sum_iw_{h,i}\bar x_i+\sum_r\ell_{h,r}z_r
\]

## 6. Energia relacional

\[
E_{contra}=c_1|z_{sensor}-z_{lens}|+c_2|z_{light}-z_{geometry}|+
 c_3|z_{texture}-z_{codec}|+c_4|z_{topology}-z_{semantic}|
\]

## 7. FRLL

\[
F_h=L_h-\lambda_hE_{contra}
\]

\[
P_h=\frac{F_h-F_{min}+\epsilon}{\sum_q(F_q-F_{min}+\epsilon)}
\]

## 8. Confiabilidade

\[
U=1-\max_hP_h,\qquad C=1-E_{contra}
\]

\[
R=C(1-U)Q_{chain}Q_{cal}Q_{coverage}
\]

## 9. Invariantes

- `I1`: posterior soma `1±ε`;
- `I2`: `0≤C≤1`;
- `I3`: estado de evidência válido;
- `I4`: nenhuma alocação dinâmica;
- `I5`: nenhuma dependência de libc;
- `I6`: saturação em toda multiplicação/acumulação crítica;
- `I7`: mesma entrada, modelo e arquitetura produzem mesma saída;
- `I8`: CRC32C ou hash externo vincula entrada e resultado.

## 10. ABI estreita

```c
void frll_zero_tensor(frll_tensor *t);
void frll_zero_latents(frll_latents *z);
void frll_default_model(frll_model *m);
int frll_set_feature(frll_tensor *t, unsigned index,
                     unsigned direction, unsigned scale, int q16);
int frll_validate_tensor(const frll_tensor *t);
int frll_evaluate(const frll_tensor *t, const frll_latents *z,
                  const frll_quality *q, const frll_model *m,
                  frll_result *out);
unsigned frll_crc32c(const void *data, unsigned size);
```

## 11. Separação operacional

### Núcleo freestanding

- redução 20×14×3;
- FLL;
- latentes;
- energia de contradição;
- FRLL;
- normalização inteira;
- confiabilidade;
- invariantes;
- CRC32C.

### Adaptadores externos

- decodificação JPEG/PNG/WebP;
- EXIF/XMP/ICC;
- FFT e wavelets;
- PRNU/CFA;
- landmarks;
- redes neurais;
- I/O e relatório.

## 12. Compilação de referência

```sh
clang -O2 -std=c11 -ffreestanding -fno-builtin -fno-stack-protector \
  -march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=softfp \
  -Iinclude -c src/frll_freestanding.c -o frll_freestanding.o
```

## 13. Falsificadores técnicos

A implementação deixa de satisfazer o contrato quando:

- requer heap, libc ou syscall;
- produz posterior fora da tolerância;
- apresenta overflow não saturado;
- depende de ordem não determinística;
- mistura extração visual com decisão sem fronteira auditável;
- atribui autenticidade sem qualidade de cadeia, calibração e cobertura.

## 14. Relação com o documento canônico 24

O documento `docs/canonicos/24_FLL_FRLL_FORENSICA_MULTIESCALA_DE_IMAGENS.md` define a teoria e os índices. Este arquivo define a máquina mínima capaz de executar a camada decisória em ambiente bare-metal ou freestanding.
