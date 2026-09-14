# 26 — Ancoragem Relacional de Fala, Acento e Conhecimento

## Estado epistemológico

Este documento registra uma extensão relacional do ecossistema RLL. O princípio central é que compreensão não depende de equivalência acústica perfeita, mas da coerência entre sinal, contexto, histórico, intenção e padrão do falante.

## 1. Sinal observado

\[
y(t)=\mathcal A(s,a,m,c,e,n)+\eta(t)
\]

- `s`: conteúdo pretendido;
- `a`: acento/dialeto;
- `m`: estado motor da fala;
- `c`: contexto;
- `e`: prosódia/estado expressivo;
- `n`: canal e ruído.

Inferência:

\[
\hat s=\arg\max_s P(s\mid y,a,m,c,e,n)
\]

## 2. Ancoragem

\[
K_t=\{W_t,H_t,R_t,C_t,P_t\}
\]

- palavras e hipóteses;
- histórico do falante;
- referentes compartilhados;
- contexto local;
- padrões prosódicos e articulatórios.

Atualização:

\[
P(s_t\mid y_{1:t})\propto P(y_t\mid s_t,H_t,P_t)P(s_t\mid C_t,R_t)
\]

## 3. Acento

\[
\phi_{accent}:\mathcal P_{base}\rightarrow\mathcal P_{speaker}
\]

\[
P(y\mid p,a)=\mathcal N(\mu_{p,a},\Sigma_{p,a})
\]

A adaptação preserva o referente enquanto recalibra a forma acústica.

## 4. Fala motora variável

\[
z_{motor}=[rate,pause,pitch,intensity,formants,articulation,breath,rhythm]
\]

\[
P(s\mid y,H)=\sum_zP(s\mid z,H)P(z\mid y)
\]

Pessoas próximas podem acumular um modelo longitudinal mais rico do falante; isso não deve ser descrito como tradução, mas como ancoragem por convivência e memória relacional.

## 5. Sete direções

1. fonética;
2. fonológica;
3. prosódica;
4. motora;
5. semântica;
6. relacional;
7. pragmática.

## 6. Energia relacional

\[
E_{rel}(s)=w_aE_{acoustic}+w_pE_{phonology}+w_rE_{prosody}+w_mE_{motor}+w_sE_{semantic}+w_hE_{history}+w_gE_{pragmatic}
\]

\[
\hat s=\arg\min_sE_{rel}(s)
\]

\[
C=1-\frac{E_{rel}(\hat s)}{E_{max}+\varepsilon}
\]

## 7. Dez relações

1. som ↔ intenção;
2. fonema ↔ acento;
3. articulação ↔ condição motora;
4. palavra ↔ frase;
5. frase ↔ histórico;
6. prosódia ↔ emoção;
7. ruído ↔ canal;
8. contexto ↔ desambiguação;
9. memória ↔ adaptação;
10. confiança ↔ abstinência.

## 8. Estados de evidência

- `VERIFIED`: hipótese confirmada pelo interlocutor ou por evidência contextual forte;
- `DECLARED_BY_AUTHOR`: interpretação declarada, ainda sem confirmação;
- `TOKEN_VAZIO`: significado não resolvido;
- `CONTRADICTION`: hipótese incompatível com contexto ou confirmação posterior.

## 9. Regra de abstinência

\[
P(s_1\mid y)-P(s_2\mid y)<\tau\Rightarrow TOKEN\_VAZIO
\]

O sistema não deve completar lacunas com confiança artificial.

## 10. Relação com a física de captura

A mesma arquitetura vale para fala e imagem:

\[
\text{sinal observado}=\text{fonte}\circ\text{canal}\circ\text{sensor}\circ\text{processamento}
\]

Em imagem, o canal inclui lente, sensor e temperatura. Em fala, inclui trato vocal, condição motora, acento, ambiente e microfone. Em ambos os casos, conhecimento nasce da coerência entre relações causais.

## 11. Referências

- Warren, R. M. Perceptual restoration of missing speech sounds. *Science*, 1970.
- Clarke, C. M.; Garrett, M. F. Rapid adaptation to foreign-accented English. *JASA*, 2004.
- Bradlow, A. R.; Bent, T. Perceptual adaptation to non-native speech. *Cognition*, 2008.
- Hinsvark, A. et al. Accented Speech Recognition: A Survey, 2021.

## Regra final

\[
\boxed{\text{compreensão}=\text{sinal}+\text{relação}+\text{memória}+\text{confirmação}}
\]
