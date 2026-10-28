# RAFAELIA Ω — Contracabeças, a direção oposta e o teste das próprias invariantes

**Estado 2026-10-28:** PESQUISA / HOLD. Não foram observadas cabeças internas do GPT-6. Não há execução de likelihood RLL nem confirmação de novo mecanismo físico. `claim_allowed=false`.

## Proposição científica

Ao invés de escolher apenas associações positivas entre `H He O C spin H2O H2O3 heads 21cm C IV BAO`, escolher explicitamente o complemento **falsificador**:

**A contracabeça não é necessariamente o negativo aritmético de uma cabeça. Pode ser uma operação que bloqueia, desfaz, neutraliza, troca posição, restaura, contradiz, ou revela o falso positivo de uma interpretação.**

O atlas tipado `data/governance/RLL_OPPOSITE_HEADS_SCIENTIFIC_DUALITY_20261028.json` contém **14 contrastes com fontes, estados e testes negativos**. Procede das grafias e das 15 sinapses de `RLL_TYPED_CHEM_WATER_SESSION_TOKENS_V1.json` e `RLL_SYNAPTIC_MULTIDIMENSIONAL_FEEDBACK_20261028.json`; não substitui essas estruturas.

## 1. As cabeças reais de IA: reforço versus supressão

Em `softmax(QKᵀ/√d)`, cada peso de atenção é ≥0 e as linhas somam 1. Isto NÃO implica que a contribuição final de cada cabeça seja positiva: `V` e `W_O` podem produzir contribuições de qualquer sinal e a avaliação depende do token e da tarefa.

- [Copy Suppression (ACL, 2024)](https://aclanthology.org/2024.blackboxnlp-1.22/): a cabeça L10H7 em **GPT-2 Small** suprime cópia ingênua de tokens e pode melhorar a perda de previsão. Não generalizar resultados a todas as IAs.
- [Causal Head Gating (NeurIPS, 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/a7f530e11fa19e9551b7a51dbd0f336f-Abstract-Conference.html): função pode ser facilitadora, interferente ou pouco relevante, e depende da intervenção; efeitos entre cabeças são interativos.
- [When Do Attention-Head Ablations Support Causal Claims? (2026, preprint)](https://arxiv.org/abs/2610.00373): uma ablação **depois da projeção de saída** pode zerar canais misturados, não uma cabeça individual. Testar antes da projeção, usar métricas contínuas e controles aleatórios compatíveis.
- [Curse of Multiple Mediators (2026, preprint)](https://arxiv.org/abs/2606.27510): mecanismos residuais, bypass e interações dificultam atribuição de efeito a uma cabeça.
- [Which Attention Heads Are Like the Human Head? (2026, preprint)](https://arxiv.org/abs/2609.37991): alinhamento representacional com EEG humano não equivale a ser causalmente a cabeça mais importante para computação. **Não confundir cérebro, Transformer e spin.**

## 2. A cabeça muda de posição: simetria real ou troca destrutiva?

Em uma camada com a representação concatenada `h` das cabeças e projeção de saída `W_O`, a transformação simultânea

```math
h' = hP
W'_O = P^T W_O
h'W'_O = hPP^T W_O = hW_O
```

com `P` matriz de permutação é uma **simetria de reparametrização**: a função permanece igual (desde que cada cabeça e os respectivos blocos de parâmetros Q/K/V/output sejam reposicionados consistentemente). Mudar **somente** as cabeças, sem os pesos de saída correspondentes, não é essa simetria.

Experimento sintético definido e executado localmente com `h=[2,-1]`, `W_O=[3,4]`:
```text
original                    = 2
troca simultânea h e W_O    = 2
troca isolada de h          = 5
```
Isto mede **equivalência funcional** de uma composição linear, não diferença cognitiva real entre cabeças de modelos disponíveis no ChatGPT.

Complemento `1-A`: se `A` tem 3 posições e linhas com soma 1, `1-A` tem linhas de soma 2. A versão normalizada `(1-A)/2` pode ser uma heurística de desatenção, mas não é a inversa única da rede nem um transformador original aprendido.

## 3. O oposto na física: hiperfino, energia, espectro e química

**H neutro:** o acoplamento de spins do núcleo e do elétron, ambos 1/2, produz estados `F=1` (triplete, degenerescência 3) e `F=0` (singlete, degenerescência 1). A diferença de energia equivale a `ν≈1420,40575177 MHz`, `E≈5,8743×10⁻⁶ eV`; esta é a linha HI de 21 cm, não um mecanismo de redes neurais. [Material da Univ. Maryland](https://pages.astro.umd.edu/~rmushotz/ASTRO421/A421_GAS_lec7.pdf).

**Emissão × absorção:** são processos radiativos em sentidos opostos numa transição; o espectro observado depende de população, campo, temperatura de excitação e profundidade óptica. Um sinal de absorção NÃO é automaticamente um sinal de emissão com sinal trocado.

**H2⁺ + H2 → H3⁺ + H:** é possível escrever a transformação estequiométrica inversa preservando átomos e carga, mas a existência de uma seta inversa não assegura taxa reversa, igualdade de fluxo, nem barreira adequada em condições distintas. [Nuvens moleculares e ionização por raios cósmicos, 2026](https://arxiv.org/abs/2601.11761).

**Água:** menor/maior ordenamento de ligações de hidrogênio ou redes locais concorrentes não convertem `H2O` em `H2O3`. A anomalia coletiva exige temperatura, pressão e estrutura, enquanto trioxidano é espécie química distinta.

**Cosmologia:** inverter `modelo→observação` para `observação→modelo` é um problema estatístico inverso, geralmente não identificável sem hipóteses/priors e seleção instrumental. Um pico em difração molecular não é BAO; C IV e HI 21cm são traçadores espectrais diferentes; RLL permanece `TOKEN_VAZIO_NOT_FITTED`.

## 4. Invariante das invariantes: passar um gate pode não provar nada

[Null Controls Are Necessary but Not Sufficient (2026, preprint)](https://arxiv.org/abs/2610.22445) demonstra um perigo diretamente aplicável a Atlas/invariantes: o mapeamento degenerado `Q(x)=0` pode satisfazer certas condições formais de fechamento dinâmico, porém elimina toda variação do fenômeno. Exigir, portanto, simultaneamente:

- uma propriedade formal preservada ou uma predição correta **E**
- manutenção de informação observável relevante **E**
- testes positivos/negativos correspondentes **E**
- consequências independentes previstas e confrontadas.

Não declarar sucesso pela simples aceitação do teste que o próprio modelo escolheu. Este é o ponto que protege a “invariante das invariantes” contra provas vazias.

## 5. Ablação e patching em dois sentidos

Para um modelo **aberto, acessível e autorizado**: (a) executar com dado limpo e dado contrastante; (b) restaurar apenas a cabeça candidata no dado contrastante; (c) fazer a troca oposta para medir ruptura; (d) ablação antes de `W_O`; (e) comparar ao mesmo nível/camada com cabeças aleatórias e retenção fora de amostra; (f) ablação dupla para detectar compensação. Uma melhora isolada sem controles não é prova.

O paper [Causal Localization of Evidence Effects in Transformers (2026-10-27, preprint)](https://arxiv.org/abs/2610.36524) implementa intervenções e comparações em duas direções, que inspiram a proposta mas não são validação para o projeto RLL.

## 6. Prova sintética executável e limite do receipt

Artefatos adicionais isolados neste branch:
- `data/governance/RLL_OPPOSITE_HEADS_SCIENTIFIC_DUALITY_20261028.json`;
- `tools/rll_opposite_heads_science_gate.py` (stdlib; **14 invariantes/counterexamples**);
- `tests/test_rll_opposite_heads_scientific_gate.py` (contratos + status fail-closed);
- esta nota.

O cálculo **sintético local** de 14 casos foi executado em Python e retornou `PASS_SYNTHETIC_ONLY 14/14`; no experimento de permutação: valor original 2, troca simultânea 2, troca isolada 5. Esse recibo **não** é CI de GitHub, teste real de heads, teste de fenômenos quânticos, nem confirmação física de RLL. CI exato desta branch continua `TOKEN_VAZIO_NOT_EXECUTED`. Sem merge; sem mudanças na main.

```sh
python3 -B tools/rll_opposite_heads_science_gate.py --self-test
python3 -B -m unittest tests.test_rll_opposite_heads_scientific_gate -v
```

**R3** F_ok: contracabeças tipadas e quatro operações de oposição, prova matemática local sintética, fonte e falsificadores; F_gap: intervenções reais em modelo aberto, instrumentação científica e RLL fit com covariância; F_next: executar os testes do HEAD no runner autorizado e, no próximo laboratório, controles combinatórios, nulls e dados mantidos em holdout. `claim_allowed=false`.
