# RLL: Telex 5 bits × Braille 6 bits — janelas iguais

**Experimento de representação escrita, não de execução de código.** Continuação da [PR #1161](https://github.com/instituto-Rafael/relativity-living-light/pull/1161), com a fonte canônica [BRAILLE_FIXED_WINDOW_20261108](../BRAILLE_FIXED_WINDOW_20261108/README.md).

## O que foi controlado

- **Mesmo texto:** 1.256 caracteres do corpus existente; SHA-256 `ce345d79784d938039382b5d98cc89fa867e137a1a22f46e7a2a7f80623effd2`.
- **Cinco segmentos semânticos correspondentes:** 256, 256, 256, 256 e 232 caracteres; nunca dividir bytes UTF-8 no meio.
- **Mesmo compressor:** Zstd CLI 1.5.7, nível 19, `--long=10` (janela LZ até 1.024 bytes), sem dicionário, frame independente por segmento.
- **Cinco representações:** português UTF-8, Braille Unicode UTF-8, Braille empacotado de 6 bits, português com tabela própria de 5 bits, ITA2 inspirado com 5 bits.
- **Conservação da informação:** os formatos de 5 bits têm extensão de escape para maiúsculas, acentos e símbolos não contidos na tabela, mantendo o texto português reconstruível exatamente. São codificações **experimentais**, não um fluxo padrão ITA2 interoperável.
- Cada segmento codificado em 5 bits inclui cabeçalho de 4 bytes com número de códigos. O Braille de seis bits também conta seu cabeçalho. Não se medem start/stop bits físicos do Telex.

## Resultado: soma de cinco streams com o mesmo limite de janela

| Escrita da mesma informação | Bruto | Zstd | Redução |
|---|---:|---:|---:|
| Português UTF-8 | 1.304 B | **945 B** | 27,531% |
| Braille Unicode UTF-8 | 3.843 B | 1.296 B | 66,276% |
| Braille empacotado 6 bits | **984 B** | 1.049 B | −6,606% |
| Português em 5 bits (tabela própria + escape) | 1.016 B | 1.081 B | −6,398% |
| ITA2 5 bits com extensão para Unicode exato | 1.027 B | 1.092 B | −6,329% |

A comparação por janela está em [janelas.csv](janelas.csv). A representação original de 1.256 caracteres demandou 1.592 códigos de 5 bits na tabela própria e 1.608 no ITA2 estendido. Isso explica por que **5 bits por código não significam 5 bits por caractere original**.

Em teoria, 5 bits são **16,667% menos** que 6 bits para a mesma quantidade de símbolos, ou 37,5% menos que 8 bits. **Na prática desta amostra, os escapes e shifts neutralizaram a economia**. Português UTF-8 foi o menor depois da compressão.

## Reproduzir no repositório

```sh
cd NOVOexport/LOW_LEVEL_TEXT_ENCODING/TELEX_5BIT_FIXED_WINDOW_20261108
python3 medir_telex5.py
```

O programa usa o [transcritor Braille já catalogado](../BRAILLE_FIXED_WINDOW_20261108/medir.py) e a fonte textual daquele diretório, sem copiar o corpus ou criar outra tabela Braille concorrente. Precisa de Python 3 e `zstd` CLI. A suíte local mais extensa de codificação/decodificação teve **11/11 PASS_SCOPED**; o código deste arquivo é uma versão curta com comparações estritas de tamanho. **CI do novo HEAD ainda não confirmada**.

**Pontos de rigor:** ASCII histórico era 7 bits, não 5. ITA2 tinha tabelas de letras e números selecionadas por sinais de deslocamento; o escape Unicode usado aqui é uma *extensão autoral*, não parte do ITA2 histórico. A redução percentual interna não mede entropia semântica nem prova superioridade geral. `SOURCE≠ARTIFACT≠EXECUTION≠EVIDENCE≠CLAIM`; `claim_allowed=false` para extrapolações científicas. Rollback: fechar PR sem merge ou reverter arquivos aditivos.

Referências: [ITA2 / Baudot](https://www.irt.org/foldoc/Baudot%20code.htm) · [Telex 5 bits](https://gheinz.de/techdocs/telexcode_5bit.htm).
