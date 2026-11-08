# RLL Ω — Escritas, Braille, Numerais Históricos e FFT (V2)

**Estado:** `PASS_SCOPED_TEXT_10_LANG_AND_SYNTHETIC_VISUAL_128`, `claim_allowed=false`.

Este experimento compara **a mesma quantidade cinco**, com a equação `2+3=5`. Há 10 palavras em línguas naturais e 10 frases autorais alinhadas à mesma proposição, grafia Braille em português em células Unicode e 6 bits empacotados, numeral maia `𝋥` e hieróglifo egípcio `𓏾`. Maia e egípcio são *numerais*; não são traduções de frases nestas línguas. Traduções textuais ainda não receberam revisão linguística independente.

**Braille do PT `cinco`:** `⠉⠊⠝⠉⠕`, cinco células de 6 pontos → 15 bytes como UTF-8 ou 30 bits → 4 bytes empacotados, **sem comprimento e tabela inclusos**. Braille numeral cinco: `⠼⠑` (sinal numérico + e). A palavra original `cinco` usa 5 bytes ASCII/UTF-8. Essa é uma comparação de codificação, não a taxa intrínseca da língua.

**Métricas de texto:**

- `H_byte = -Σp(b) log2 p(b)` medido sobre bytes UTF-8; `H_codepoint` sobre codepoints Unicode de cada item. Os resultados não correspondem à entropia estatística de uma língua inteira. Para uma palavra de só um codepoint, `H_codepoint=0` — isso não quer dizer zero informação semântica.
- `zlib9`, `gzip9` e `xz6`, aplicados **independentemente** a cada texto, com reversibilidade verificada. Valores negativos de economia são válidos por overhead. Textos curtos não dão base confiável para ranking de idiomas por eficiência.
- Sem misturar tamanhos byte, bits por byte, bits por codepoint, bits por imagem ou entropy FFT em uma métrica universal.

**Imagens e FFT:** seis imagens controladas, **128×128 pixels, 8-bit grayscale**, geradas em `PGM` e `PNG`: símbolo ocidental 5, palavra Braille, numeral Braille, numeral maia esquemático, hieróglifo egípcio esquemático e uma **silhueta de mão sintética que NÃO é um sinal de Libras validado**. A FFT é 2D em quadro estático, média subtraída e DC excluído; a entropia de potência espectral `H_F=-Σ q_k log2 q_k` usa `q_k=|FFT(x)_k|² / Σ|FFT(x)_j|²`. Essa é uma medida espacial de padrão/contorno, **não a entropia de Libras ou de semântica**. Mesmo tamanho de imagem não garante mesma área ocupada nem comparabilidade informacional.

**Libras real** = `TOKEN_VAZIO_REAL_LIBRAS_FRAME`: um sinal exige configuração de mão, movimento e expressões; um frame só é uma amostra. Script aceita `--libras-pgm PATH --provenance METADATA.json` somente com `corpus, gloss, license, source_sha256, crop_policy, frame_number` e `128×128 P5`. O corpus UFSC e a coleção MINDS-Libras incluem vídeos, mas nenhum quadro audiovisual com direitos/verificação apropriados foi materializado neste ciclo. Também faltam 8 quadros equiespaçados para FFT temporal e revisão de sinalizantes fluentes. A figura da mão é apenas **controle sintético**, explicitamente excluída como evidência linguística.

**FONTES:**
- MEC Grafia Braille 2018: https://portal.mec.gov.br/docman/dezembro-2018-pdf/105421-grafia-braille-para-a-lingua-portuguesa-2018/file
- Unicode Braille: https://www.unicode.org/versions/Unicode16.0.0/core-spec/chapter-21/
- Unicode Mayan numerals: https://www.unicode.org/versions/Unicode16.0.0/core-spec/chapter-22/
- Unicode Egyptian glyph Z015D: https://unicode.org/Public/18.0.0/charts/nameslist/13000/
- Corpus Libras UFSC: https://corpuslibras.ufsc.br/
- MINDS Libras dataset: https://huggingface.co/datasets/ibmectech/minds-libras-raw

**Reprodução (stdlib Python 3.11+):**

```sh
python tools/ci/rll_script_entropy_v2.py --output results/audit/rll_entropy_text_v2.json
python tools/ci/rll_visual_fft_v2.py --output-dir results/audit/rll_visual_fft_v2
PYTHONPATH=. python -m unittest discover -s tests -p 'test*.py' -v
```

**Limites:** amostras pequenas; textos autorais não revisados por tradutor independente; nenhum resultado físico/cosmológico/bayesiano inferido; sem execução real em dispositivo ARM, sem prova de legibilidade tátil.

**R3 = ⟨10 línguas / Braille / numerais / 19 testes locais PASS_SCOPED; Libras real e equivalência independente TOKEN_VAZIO; obter quadro/video licenciado e corpus paralelo longo com julgamento humano⟩**.
