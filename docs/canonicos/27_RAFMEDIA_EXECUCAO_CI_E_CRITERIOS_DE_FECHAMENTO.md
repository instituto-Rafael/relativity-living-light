# 27 — RAFMEDIA: Execução, CI e Critérios de Fechamento

## 1. Estado

Este documento registra o estado operacional do núcleo RAFMEDIA e define quando cada módulo pode ser considerado funcional, testado e cientificamente utilizável.

## 2. Núcleo já verificado

Repositório executável: `rafaelmeloreisnovo/Img`.

Componentes:

- `include/rafmedia_standalone.h`;
- `src/rafmedia_standalone.c`;
- `tests/test_rafmedia.c`;
- `Makefile`;
- `.github/workflows/rafmedia-standalone-ci.yml`.

A CI atual valida:

- Clang e GCC;
- ASan e UBSan;
- contrato sem `malloc` e sem chamadas proibidas de libc no núcleo;
- cross-build ARM32 e ARM64;
- ausência de símbolos indefinidos nos objetos freestanding;
- geração de hashes e artefatos compilados;
- testes determinísticos para arena, PNG, GIF, BMP, WAV e sondagem de formatos.

## 3. Regra de claims

\[
\text{probe de formato}\neq\text{decodificação}\neq\text{análise forense}\neq\text{prova de autenticidade}
\]

Estados permitidos:

- `VERIFIED`;
- `DECLARED_BY_AUTHOR`;
- `TOKEN_VAZIO`;
- `CONTRADICTION`.

## 4. Ordem de execução

### Fase 1 — PNG + WAV

Objetivo: fechar uma vertical completa de imagem estática e áudio PCM.

PNG:

- chunks;
- CRC;
- IHDR/PLTE/IDAT/IEND;
- filtros;
- DEFLATE bounded;
- limites contra decompress bombs;
- corpus válido, truncado e adversarial.

WAV:

- RIFF/WAVE;
- `fmt`, `data` e chunks desconhecidos;
- PCM 8/16/24/32 bits;
- canais e sample rate;
- janelas temporais;
- espectro inteiro;
- corpus válido, truncado e adversarial.

### Fase 2 — JPEG + GIF + FLAC

### Fase 3 — TIFF/DNG/RAW + MP3/AAC

### Fase 4 — MP4/MOV/AVI/Matroska/MPEG

### Fase 5 — física forense

- PRNU/DSNU;
- CFA/demosaicing;
- white balance e resposta espectral;
- CCD/CMOS plano ou curvo;
- Petzval, MTF, vinheta e chief-ray angle;
- dark current, hot pixels e temperatura;
- OIS/EIS/gimbal e microvibração corporal;
- rolling shutter;
- turbulência térmica;
- espectrometria inferencial da voz;
- assinatura de microfone e eletrônica.

### Fase 6 — FLL/FRLL calibrado

\[
\mathcal H=\{H_R,H_S,H_P,H_T\}
\]

- captura física;
- síntese;
- processamento pesado;
- refotografia/regravação.

## 5. Critério de fechamento por módulo

Um módulo só recebe estado `VERIFIED` quando:

1. implementa exatamente o subconjunto declarado;
2. rejeita entradas fora do contrato sem overflow;
3. possui limites de memória e iteração;
4. passa testes golden;
5. passa truncamento sistemático;
6. passa sanitizers;
7. passa fuzzing com orçamento;
8. passa Clang e GCC;
9. passa ARM32 e ARM64;
10. produz manifesto, hashes e limitações explícitas.

## 6. Reprodutibilidade

Para os mesmos bytes, parâmetros e arquitetura de referência:

\[
F(x,\theta)=y
\]

A execução deve ser determinística. Diferenças de backend SIMD devem permanecer dentro de tolerância registrada.

## 7. Relação com Google Drive

O Drive mantém o espelho canônico de decisões, estado de evidência e roadmap. O GitHub permanece a fonte executável e versionada.

## 8. Regra final

A expansão horizontal por muitos codecs não deve preceder o fechamento vertical de pelo menos um caminho completo. A prioridade científica e operacional é PNG + WAV completos, depois JPEG/GIF/FLAC, e somente então contêineres e codecs de vídeo de maior complexidade.
