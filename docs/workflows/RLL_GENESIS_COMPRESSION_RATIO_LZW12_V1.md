# RLL Ω — Gênesis 1 em hebraico, aramaico e grego: RAZÃO de compressão

**Estado:** resultado empírico de compressão de bytes; sem prova semântica
ou cosmológica. `claim_allowed=false`. Nenhum resultado G4/G5 foi alterado.

## Fórmula solicitada

`R_c = n_bytes_UTF8_original / n_bytes_LZW12_comprimido` (unidade X:1).
Essa razão **não é economia percentual**, que vale `100*(1 - 1/R_c)`.
A medida suplementar `compressed_bits_per_original_byte = 8/R_c` também é
uma taxa de armazenamento, **não** entropia semântica ou teorema universal.

| Representação | Com sinais | Sem marcas Unicode Mn |
|---|---:|---:|
| Hebraico | 7413/3243 = 2.285846:1 | 3929/1683 = 2.334522:1 |
| Aramaico | 6628/2583 = 2.566009:1 | 3896/1670 = 2.332934:1 |
| Grego | 7944/3401 = 2.335784:1 | 7300/2859 = 2.553340:1 |

Corpus: Gênesis capítulo 1 (31 versículos nas três edições).
Hebraico: Westminster Leningrad via Bereshit; aramaico Targum Onkelos;
grego Septuaginta edição Swete. Grego e aramaico são traduções antigas,
não manuscritos originais independentes da composição hebraica.

Os commits e os `git_blob_sha1` das três fontes estão congelados em
`data/contracts/rll_genesis_lzw12_ratio_v1.json`. Não copiamos os textos
completos para o repositório: direitos e edições devem ser respeitados.

### Contrato de execução

- PR/CI sem rede: recalcula seis taxas, confirma aritmética, packing 12-bit,
  limites de corpus, decoder sem perdas e falhas adversariais.
- O receipt de CI nesse modo é **PASS_SCOPED_OFFLINE_RATIO_CONTRACT**;
  testa as medidas verificadas e os limites, sem baixar fontes novamente.
- Rechecagem de fonte: somente execução com rede e solicitação explícita;
  use `--verify-upstream`, que recupera três revisões **pinned**, verifica
  o SHA-1 Git blob, extrai os 31 versículos, comprime, decodifica e exige
  equivalência exata com todas as seis medições. Falha fechada.
- Não alterar o compressor sem uma nova versão, recibo e comparador.
- Remover diacríticos **altera** a informação textual, não é compressão
  reversível do texto vocalizado.
- O código LZW fixa 12 bits, 256 entradas iniciais e até 4096 códigos,
  empacota MSB-first e **não inclui cabeçalho** ou custo de dicionário.
  Não é gzip, ZIP ou zlib; comparações exigem a mesma implementação.

### Comandos

```bash
python tools/ci/rll_genesis_lzw12_ratio_v1.py --require-pass
python -m unittest discover -s tests -p test_rll_genesis_lzw12_ratio_v1.py -v
python tools/ci/rll_genesis_lzw12_ratio_v1.py --verify-upstream --require-pass
```

O último comando requer rede e será executado manualmente fora da PR,
não automaticamente. A rechecagem independente das três fontes já foi
realizada via conexão GitHub nesta sessão com 31/31 versículos e valores
iguais aos registrados, mas a CI padrão não refaz o download.

### Próximos experimentos

Comparar muitos capítulos e edições/idiomas e controles de tamanho,
codificação, permutação e redundância; confrontar razão física de bytes
com equivalência semântica sem contar traduções dependentes como amostras
independentes. `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.
