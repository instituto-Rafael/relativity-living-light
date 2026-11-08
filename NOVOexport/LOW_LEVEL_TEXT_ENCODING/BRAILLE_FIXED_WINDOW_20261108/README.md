# RLL — mesma informação em português e Braille, mesma janela

**Objetivo do usuário:** comparar a taxa de compressão **do texto-fonte escrito**,
não compilar programas nem comparar assembly/binários.

## Protocolo comparável

- **Corpus idêntico:** 1.256 caracteres de português, SHA-256
  `ce345d79784d938039382b5d98cc89fa867e137a1a22f46e7a2a7f80623effd2`.
- **Janela semântica:** cinco partes correspondentes do texto: 256, 256, 256, 256, 232 caracteres.
- Cada parte é transcrita para Braille português básico, **sem estenografia**.
- Três codificações do mesmo trecho: português UTF-8, Braille Unicode UTF-8,
  Braille empacotado em 6 bits/célula (cabeçalho de 4 bytes por trecho).
- **Mesmo algoritmo:** Zstandard 1.5.7 nível 19, `--long=10` (janela máxima de
  correspondência de **1.024 bytes**), um fluxo independente por janela, sem dicionário.
- Contamos bytes brutos e bytes comprimidos incluindo cabeçalho do compressor.
- Medida: `taxa_de_redução = 100*(1 - comprimido / original)`. Negativo significa expansão.
- Roundtrip de transcrição e de compressão realizado em todas as janelas.

## Resultado: soma de cinco janelas semanticamente correspondentes

| Texto / escrita | Bruto | Zstd 1 KiB | Redução no próprio formato |
|---|---:|---:|---:|
| Português UTF-8 | 1.304 B | **945 B** | **27,531%** |
| Braille Unicode UTF-8 | 3.843 B | 1.296 B | **66,276%** |
| Braille 6-bit com cabeçalho | 984 B | 1.049 B | **−6,606%** |

**Mesmo conteúdo:** em cada janela o português ocupa menos bytes comprimidos,
embora a redução relativa do Braille Unicode seja maior. O Braille de seis bits
é mais curto antes da compressão, porém nas janelas pequenas aumenta ao comprimir.
Os cabeçalhos de 4 bytes se repetem porque cada janela é autônoma.

## Valores de cada janela

| Janela | Caracteres | PT B/Zstd | Braille Unicode B/Zstd | Braille 6-bit B/Zstd |
|---|---:|---:|---:|---:|
...
| 1 | 256 | 262/198 | 789/278 | 202/215 |
| 2 | 256 | 270/184 | 801/250 | 205/218 |
| 3 | 256 | 266/195 | 774/266 | 198/211 |
| 4 | 256 | 267/191 | 777/253 | 199/212 |
| 5 | 232 | 239/177 | 702/249 | 180/193 |

`janelas_256.csv` contém os números linha a linha.

**Não confundir:** comparar a mesma janela de caracteres e limitar a janela do
compressor são dois controles diferentes; ambos estão especificados aqui.
A escrita Braille foi transcrita com subconjunto documentado da grafia portuguesa,
não com um transcritor editorial completo; norma e revisão humana podem alterar a
contagem de células. Diferentes versões e parâmetros do Zstd podem mudar bytes.

**Reproduzir:** `python3 medir.py` com `zstd` CLI v1.5.7 instalado.
Este cálculo mede representação textual, **não** poder preditivo de RLL, nem
entropia semântica, nem performance de código de máquina.

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM` ·
`claim_allowed=false` para extrapolações científicas.

**Rollback:** fechar PR sem merge ou reverter apenas arquivos aditivos.
