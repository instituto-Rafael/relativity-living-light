# RLL Bible10 — protocolo multilíngue de entropia, compressão, fonética, acústica e geometria

**Estado:** \`METHOD_IMPLEMENTED / PROVIDER_RUN_REQUIRED / claim_allowed=false\`  
**Data:** 2026-09-30  
**Escopo:** corpus paralelo como laboratório de informação. Nenhuma promoção automática para cosmologia, teologia, acústica física ou causalidade numérica.

## 1. Rota

A extensão preserva a sequência experimental:

\`\`\`text
SOURCE
-> texto normalizado
-> entropia/compressão
-> estrutura numérica
-> grafo/hierarquia
-> Euclidiano x Poincaré
-> G2P sintético
-> waveform sintética
-> acústica física somente com calibração
-> EVIDENCE
-> CLAIM gate
\`\`\`

Painel: inglês, espanhol, português, francês, alemão, italiano, russo, mandarim simplificado, árabe e sérvio latino. A seleção visa diversidade de escrita/família e redistribuição reprodutível em domínio público; **não é ranking das dez línguas mais faladas**.

Ordem inicial solicitada:

\`\`\`text
JHN (João) -> GEN (Gênesis) -> MAT (Mateus)
\`\`\`

Não se assume que João seja o mais entrópico nem que Mateus seja semanticamente mais direto. Isso será testado.

## 2. Fonte/licença

O registro canônico é \`configs/bible10-public-domain.v1.json\`. O ingestor aceita somente \`Public Domain\` e baixa USFM do eBible. ZIP e membros usados recebem SHA-256 no receipt.

## 3. H-JOHN-ENTROPY

Para cada língua/livro:

\[
H(X)=-\sum_x p(x)\log_2p(x)
\]

e entropia condicional de primeira ordem:

\[
H(X_n\mid X_{n-1}).
\]

O primeiro gate testa:

\[
H_1(JHN)>H_1(GEN)\land H_1(JHN)>H_1(MAT).
\]

Mesmo 10/10 seria \`OBSERVED_UNPROMOTED\`: entropia textual não é profundidade semântica, inspiração, verdade teológica ou entropia termodinâmica.

## 4. Mateus: concision surrogate

"Direto" exige anotação semântica. A primeira aproximação mensurável é:

\[
C_{tok}(B)=N_{tokens}(B)/N_{versos}(B).
\]

Testa-se se Mateus usa menos tokens por verso. Isso mede concisão ortográfica/tokenizada, não "objetividade".

## 5. Compressão

Suíte inicial:

\`\`\`text
raw | zlib-9 | gzip-9 | bzip2-9 | LZMA-9 | Brotli-11 | Zstandard-19
\`\`\`

O registro é extensível. Também se compara o mesmo multiconjunto de registros em:

\`\`\`text
REF-major  = verso -> 10 línguas
LANG-major = língua -> todos os versos
\`\`\`

Diferença de tamanho comprimido mede efeito de ordem/localidade, não uma constante semântica.

Os estados anteriores do RLL são preservados:

\`\`\`text
G1 = PASS
G2 = FAIL_STRONG_CLAIM
G3 = PASS_CORRECTED_SCOPE
claim_allowed = false
\`\`\`

## 6. Estrutura numérica

São permitidas medições estruturais:

- índices de capítulos/versículos;
- índices primos;
- resíduos módulo 2, 3, 5, 7, 12, 14 e 40;
- grafos explicitamente definidos;
- controles por permutação.

Invariantes:

\`\`\`text
PRIME_INDEXING != PRIME_CAUSATION
NUMEROLOGY_EXPLORATION != PHYSICAL_CAUSATION
\`\`\`

## 7. Euclidiano x Poincaré

Hierarquia mínima:

\[
ROOT\to BOOK\to CHAPTER\to VERSE.
\]

No disco de Poincaré:

\[
d_{\mathbb B}(u,v)=\operatorname{arcosh}\left(1+
2\frac{\|u-v\|^2}{(1-\|u\|^2)(1-\|v\|^2)}\right).
\]

O código inicial é um baseline radial determinístico, não otimizado. O gate forte continua sendo A/B pareado com mesmas entradas, seed, função objetivo e orçamento.

\`\`\`text
POINCARE_EMBEDDING != PHYSICAL_SPACETIME
\`\`\`

## 8. Texto, fonema e onda

Objetos diferentes:

\`\`\`text
texto Unicode
!= fonema/IPA
!= saída G2P
!= voz humana medida
!= áudio TTS
!= pressão acústica calibrada
\`\`\`

eSpeak-ng é usado apenas para \`SYNTHETIC_G2P\` e WAV TTS de prova de caminho. Não é ground truth de falante nativo.

Uma componente tonal local pode ser aproximada por:

\[
p(x,t)=\hat p\cos(kx-\omega t+\phi),
\]

mas fala real é não estacionária e não se reduz a "uma frequência por fonema".

## 9. Energia: fronteira física

Movimento não é sinônimo de energia, mas uma massa em movimento pode ter energia cinética:

\[
K=\frac12mv^2.
\]

Para onda acústica progressiva plana, sob hipóteses declaradas:

\[
I=\frac{p_{rms}^2}{\rho c_s},
\qquad
u=\frac{p_{rms}^2}{\rho c_s^2}.
\]

Sem calibração que converta amplitude digital em pressão (Pa):

\`\`\`text
physical_acoustic_energy = TOKEN_VAZIO_NO_PRESSURE_CALIBRATION
\`\`\`

A equivalência massa–energia:

\[
E_0=mc^2
\]

não é a equação da acústica. Se uma energia acústica \`E_ac\` já tiver sido medida, pode-se apenas calcular a massa equivalente \`m_eq=E_ac/c^2\`.

Calor/energia térmica requer medições termodinâmicas próprias e não é inferido de texto ou WAV não calibrado.

## 10. Retroalimentação do material do usuário

O material privado fornecido nesta sessão foi usado localmente para localizar rotas de hipótese: linguagem/fonema, entropia/compressão, números/grafos, Euclidiano/Poincaré e fronteiras físicas. Ele **não é copiado para o repositório público**.

\`\`\`text
material privado -> rota/hipótese
material privado != evidência pública
repetição no corpus != prova
\`\`\`

A publicação só recebe métodos reprodutíveis e resultados derivados de fontes que podem ser redistribuídas.

## 11. Falsificadores

1. João não é declarado mais entrópico se a métrica não vencer.
2. Mateus não é declarado mais direto; só se registra o surrogate de concisão.
3. Poincaré não recebe vantagem se o A/B não superar Euclidiano sob condições pareadas.
4. G2P sintético não valida fonética humana.
5. Energia acústica fica bloqueada sem calibração em Pa.
6. Estruturas numéricas não viram mecanismos sem controles e modelo causal independente.

## 12. Rollback

Branch/PR isolada. Fechar o PR ou reverter eventual merge restaura o estado anterior sem sobrescrever G1/G2/G3, Poincaré ou cosmologia.

## R3

\`\`\`text
F_ok   = corpus/codec/number/geometry/G2P/acoustic methods materialized
F_gap  = provider ingestion + optimized A/B + calibrated human audio
F_next = execute 10-language JHN+GEN+MAT provider gate and preserve negative results
\`\`\`
