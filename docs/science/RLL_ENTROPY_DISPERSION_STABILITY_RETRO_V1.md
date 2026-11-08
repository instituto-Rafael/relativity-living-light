# RLL Ω — Entropia × Dispersão × Estabilidade × Parametrização — Retroalimentação V1

**Data:** 2026-11-08 · **Estado:** `FORMAL_HYPOTHESIS_PLUS_PASS_SCOPED_SYNTHETIC` · `claim_allowed=false`.

## 0. Pergunta-raiz reencontrada

A investigação iniciada pelo usuário não busca a linguagem/codec de menor arquivo. Busca detectar **regularidades informacionais persistentes condicionadas à composição da matéria, observáveis disponíveis, covariância, geometria local e dinâmica temporal**. Essas regularidades podem ser diagnósticas, mas a passagem para uma explicação causal do Universo requer equações físicas, modelos rivais e observações independentes.

### Quatro distinções inegociáveis

- Estabilidade **da representação**: preservação de informação após codificação/decodificação, com o custo do dicionário/decoder e metadados incluídos.
- Estabilidade **estatística**: dispersão, estacionariedade, deriva, autocorrelação e covariância dos observáveis ou resíduos.
- Estabilidade **dinâmica física**: resposta da evolução física a perturbações dadas as equações, condições de contorno e escala de tempo.
- Estabilidade **epistêmica/inferencial**: robustez de parâmetros, intervalos, previsão e preferência de modelo a variação justificável de amostras, priors, calibração e codificação.

## 1. Retroalimentação desta sessão — item a item

1. **Informação e compressão** — A hipótese de Universo informacional foi usada como *motivação*, não como premissa empiricamente demonstrada. Medir compressão depende do codec, bytes, normalização, dicionário e escala; isso não é automaticamente entropia física.
2. **Código-fonte em múltiplas linguagens** — A intenção correta era **a informação do código-fonte textual** em representações semanticamente equivalentes; tamanho de ELF e variantes do mesmo assembler eram desvios. A equidade exige mesmos algoritmos e accounting de cada fonte.
3. **Braille português** — As cinco células da palavra `cinco` codificam a mesma palavra na convenção adotada, mas 15 bytes UTF-8 e 4 bytes para células cruas de seis pontos têm decoders e custos diferentes. Unicode, células e semântica são camadas separadas.
4. **Libras e imagens** — Uma língua de sinais precisa de movimento temporal, configuração de mão, expressão facial e contexto; FFT de um quadro 128×128 mede energia espectral espacial, não entropia linguística de Libras. A silhueta sintética anterior não era Libras autenticada.
5. **Numerais maias e egípcios** — O mesmo numeral cinco é alinhável a símbolos históricos, mas não autoriza declarar uma sentença completa traduzida ou equivalência semântica total.
6. **8–10 línguas naturais** — Letras, Unicode, UTF-8, morfologia e ortografia mudam a compressão; traduções precisam de revisão independente e paralelismo no mesmo conteúdo, janela e licença. Comprimentos pequenos ampliam overhead do codec.
7. **Entropia de Shannon** — Para uma distribuição discreta declarada, `H(X)=-sum p_i log2(p_i)`. Reetiquetagem bijetiva do alfabeto não muda H; mudar o código binário pode mudar os bytes comprimidos. Não confundir com entropia termodinâmica ou de von Neumann.
8. **Desvio padrão amostral** — `s=sqrt(sum((x_i-xbar)^2)/(n-1))`, para `n>=2`; diferente de desvio populacional e diferente de `sqrt(3)/2` geométrico. Sem valores de incerteza, `TOKEN_VAZIO` não pode virar zero.
9. **Dispersão entre regiões e grupos** — `TSS=WSS+BSS`; média global pode ocultar variação espacial, espectral e temporal entre regiões. Escolher agrupamento antes de olhar o resultado, guardar resíduo não classificado e diferenças de médias.
10. **Regressão, decaimento e ressuprimento** — A analogia de estoque de segurança deve virar um **envelope de tolerância calibrado** (risco de ultrapassagem em holdout), não uma constante universal. Estimar inclinação, incerteza da inclinação, autocorrelação e alarme com nulo especificado.
11. **Composição espectral e observação atrasada** — Atribuir dados a `(região, época de emissão, época de chegada, banda, instrumento, composição candidata, covariância)`. Uma linha espectral não determina isoladamente toda a composição, abundância ou estabilidade orbital.
12. **Spin, órbitas, sling, lentes e plasma** — São domínios diferentes: regime local euclidiano/newtoniano, pós-newtoniano, Kerr/GR, MHD/GRMHD e cosmologia FLRW. Não empilhar variáveis de unidades diferentes sem normalização e operador físico.
13. **Matriz de sobreposição** — Use matriz de observáveis tipados, **nunca** como substituta da matriz de covariância de um dataset real. A matriz `Σ` carrega erros, variações e correlações; o resíduo de modelo é `r=y-m(theta)`.
14. **Branqueamento e qui-quadrado** — Se `Σ=LLᵀ`, então `z=L⁻¹r` e `χ²=Σ_i z_i²=rᵀΣ⁻¹r`. Esta é a autoridade estatística do ajuste cosmológico, que não deve mudar por uma visualização 7D.
15. **Geometria T⁷, 42 fases, SVG/CAD/Q16** — São **coordenadas e estratégias de discretização/representação**, não evidência de sete dimensões físicas ou de estabilidade cósmica. O caso de treliça 3 barras testa mecânica axial sintética; não testa a evolução do Universo nem cisalhamento/torção real.
16. **RLL logístico** — Núcleo histórico com cinco parâmetros livres `(H0, Ωm, Ωs0, zt, wt)`, `Ωr` e `rd` fixos naquela execução. Se `Ωs0→0`, `zt` e `wt` deixam de ser identificáveis e o modelo reduz-se à forma ΛCDM no fundo: nenhum operador entrópico novo deve mascarar esse limite.
17. **Modelos de referência** — Compare ΛCDM, wCDM, CPL, RLL com dados BAO/DESI, H(z), supernovas quando materializadas e priors CMB sob o **mesmo** likelihood documentado. Entropia de bytes, FFT e geometria podem ser diagnósticos a posteriori, nunca um peso oculto no χ².
18. **Falsificação da hipótese central** — É preciso provar, em mocks e holdout, que estatísticas informacionais adicionais melhoram previsão, poder discriminativo ou diagnóstico de sistemáticas além de média/variância/covariância/autocorrelação e do modelo base. Igualdade de compressão por si só não é prova.

## 2. Estatística principal: observações, resíduos e janelas

Dada uma lista de observações `y_i` com unidade, grupo, época, seleção, modelo `m_i(theta)` e `Σ` instrumental:

- `r_i(theta)=y_i-m_i(theta)`;
- `Σ=LLᵀ`, `z=L⁻¹r`, `χ²=zᵀz` **sem alterar** o likelihood existente;
- para janelas pré-declaradas `W_j` de observáveis do *mesmo tipo*, `μ_j=mean(z_i)`; `s_j²=sum((z_i-μ_j)²)/(n_j−1)` (se `n_j>=2`);
- seleção fixa de alfabeto/quantização `Q`, `H_j=-Σ_k p_{jk}log₂p_{jk}`; o alfabeto e a quantização fazem parte do registro;
- `s_H = sqrt[Σ_j(H_j-mean(H))²/(m-1)]` para `m>=2`, com correção/baseline de viés e dependência serial antes de usar em dados reais;
- `b_μ = Σ_j(t_j-tbar)(μ_j-μbar)/Σ_j(t_j-tbar)²`;
- `b_H = Σ_j(t_j-tbar)(H_j-Hbar)/Σ_j(t_j-tbar)²`;
- comparar mudanças de distribuição com `D_KL(p||q)` se o suporte e o smoothing forem congelados; para zeros pode ser infinito, não zero arbitrário.

**Resultado:** a estabilidade informacional *operacional* deve ser representada por um vetor tipado, não por um número mágico:

`S_diag = (s_H, b_H, b_μ, {s_j}, auto_corr, within_SSE, between_SSE, χ², Δχ²_baseline, posterior_robustness, compression_ratio_with_codec_metadata)`.

Não existe um limiar físico universal que transforme `S_diag` em `stable=true`. Os limites de tolerância e nível de erro devem ser estabelecidos por controles nulos, simulações/bootstraps adequados à correlação, múltiplas sementes, análises fora da amostra e invariância de reparametrização.

## 3. Contraprova exata: entropia estável ≠ observações estáveis

O experimento **sintético** contido em `tools/rll_entropy_stability.py` possui sete janelas com 50 valores cada. O baseline repete `[-2,-1,0,1,2]` dez vezes por janela; o alternativo adiciona o índice `j` a todos os valores da janela `j`.

| Diagnóstico | Baseline | Deriva sintética |
|---|---:|---:|
| H discreta por janela (bits/símbolo) | 2.3219280949 | 2.3219280949 |
| Desvio amostral das 7 entropias | 0 | 0 |
| Inclinação da média por janela | 0 | +1 unidade/janela |
| Fração SSE entre janelas | 0 | 2/3 |

A translação de um alfabeto discreto preserva as probabilidades, **mas não preserva o nível da observação**. A mesma entropia pode coexistir com deriva não estacionária. **Não é evidência de instabilidade dinâmica física**: o experimento apenas detecta mudança temporal da média com uma estatística ausente da entropia marginal.

## 4. Ligação a cosmologia — não alterar a física sem evidência

O RLL existente tem, como objeto de fundo histórico documentado:

`E²(z)=Ωm(1+z)³ + Ωr(1+z)⁴ + Ωs0[f(z)+(1−f(z))(1+z)³] + ΩΛ`,

`f(z)=1/[1+exp((z−zt)/wt)]`, `ΩΛ=1−Ωm−Ωr−Ωs0` em universo espacialmente plano.

**Compatibilização correta:**

1. Congelar os dados, a seleção, as unidades, os priors, a covariância e o código do ajuste (`ΛCDM, wCDM, CPL, RLL`).
2. Calcular os resíduos brancos e as estatísticas de janelas como **análise derivada**.
3. Investigar correlações condicionalmente a redshift, banda espectral, região, época, linha de visada e instrumental, não por mistura indiscriminada.
4. Testar se há informação condicional adicional: `I(estrutura_entropica; observavel_holdout | baseline, Σ, grupos) > 0` com nulo, viés e incerteza calibrados.
5. Distinguir efeitos **no fundo FLRW**, **nas perturbações**, **na propagação de fótons**, **na seleção/instrumento**, e **nas regiões locais de plasma e gravitação forte**.
6. Preservar o limite `Ωs0→0`, a não identificabilidade de `zt,wt` e todos os resultados negativos já documentados.

**Bayes:** `p(theta|D,M) ∝ L(D|theta,M)p(theta|M)` e `Z_M=∫L p dtheta`. A divergência KL entre posterior e prior e o ganho de informação dependem de coordenadas/prior; entropia diferencial isolada não é um escore absoluto de estabilidade física. Igualdade de taxa de compressão não equivale a igualdade de evidência Bayesiana.

**Termodinâmica:** `S=k_B ln Ω` (microcanônico) e `dS/dt` necessitam microestados, coarse-graining e dinâmica físicos. A derivação das grandezas de Shannon sobre textos, SVGs ou pixels **não determina** `S` termodinâmica da cosmologia sem um vínculo de probabilidade física demonstrado. Quantum: `S_vN(ρ)=-k_B Tr(ρ ln ρ)` é outro objeto com estado de densidade física definido.

## 5. Critérios de aceitação / gaps

- PASS: a igualdade das sete entropias não impede detectar deriva via inclinação e decomposição da variância; 12 testes locais stdlib validam a propriedade sobre conjunto sintético.
- HOLD: nenhuma inferência nova sobre energia escura, gravidade, entropia cósmica, força ou estabilidade orbital.
- `TOKEN_VAZIO_PINNED_COSMOLOGICAL_RESIDUAL_INPUTS` — ainda não ligamos essa nova análise de janelas a arquivos exatos DESI/Pantheon/CMB.
- `TOKEN_VAZIO_PREREGISTERED_NULL_AND_BOOTSTRAP` — faltam simulações nulas e cobertura de intervalos.
- `TOKEN_VAZIO_ASTROPHYSICAL_TIME_COORDINATE` — janelas por redshift **não** são amostras uniformemente espaçadas no tempo; separar tempo cosmológico, de emissão e de observação.
- `TOKEN_VAZIO_PHYSICAL_DYNAMICS_AND_PERTURBATION_EVOLUTION` — expoentes Lyapunov/Floquet só após equações e regime definidos.
- `TOKEN_VAZIO_REAL_SPECTRAL_COMPOSITION_INSTRUMENTAL_COVARIANCE` — para química espectral e materiais reais.
- `TOKEN_VAZIO_INDEPENDENT_REPRODUCTION` — confirmação por outro pipeline.

**R3:** `<definições reancoradas + contraprova sintética PASS, dados cosmológicos/causalidade/limiares ainda ausentes, conectar resíduos DESI congelados e construir controle nulo sem modificar χ²>`.
