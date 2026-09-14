# 25 — CCD/CMOS Curvo, Retina, Petzval e Geometria do Foco

## Estado

Documento canônico complementar ao FLL/FRLL. A geometria lente–sensor passa a ser variável causal explícita.

## 1. Superfície focal

\[
\frac{1}{R_P}=\sum_i\frac{\Phi_i}{n_i'}
\]

\[
\Delta z(r)=R_P-\sqrt{R_P^2-r^2}\approx\frac{r^2}{2R_P}
\]

## 2. Desfoco e MTF

\[
c(r)\approx\frac{|\Delta z(r)|}{N}
\]

\[
MTF_{sys}(r,\nu)=MTF_{lens}(r,\nu)MTF_{sensor}(\nu)
\]

\[
R_{eff}=N_{px}\,MTF_{sys}\,SNR
\]

Portanto, megapixel nominal não equivale a resolução útil.

## 3. Arquiteturas físicas

- silício afinado e curvado;
- conformação pneumática;
- suporte hemisférico/côncavo;
- ilhas fotossensíveis com interconexões serpentinas;
- padrões mesh/kirigami;
- microlentes conformais.

## 4. Analogia biológica

A retina é curva; a íris regula a abertura; a pupila é a abertura; a fóvea concentra acuidade. A binocularidade estima profundidade principalmente por disparidade:

\[
Z\approx\frac{fB}{d}
\]

Dominância ocular não implica divisão rígida “um olho mira, o outro mede profundidade”.

## 5. Latente adicional

\[
z_{focal}=\{R_P,\Delta z,c,MTF_s,MTF_t,CRA,V,CA,DOF,ML\}
\]

## 6. Energia de compatibilidade lente–sensor

\[
E_{LS}=\int_0^{r_{max}}w(r)\left[
\alpha|\hat{\Delta z}-\Delta z_M|+
\beta|\widehat{MTF}_s-MTF_{s,M}|+
\gamma|\widehat{MTF}_t-MTF_{t,M}|+
\delta|\hat V-V_M|
\right]dr
\]

## 7. FRLL estendido

\[
\Lambda_{FRLL}^{*}=\Lambda_{FRLL}-\eta E_{LS}
\]

\[
C_{focal}=1-\frac{E_{LS}}{E_{LS,max}+\varepsilon}
\]

## 8. Novos índices

1. raio focal estimado;
2. sagita focal;
3. círculo de confusão radial;
4. MTF sagital;
5. MTF tangencial;
6. astigmatismo centro-borda;
7. chief-ray angle;
8. vinheta relativa;
9. aberração cromática lateral;
10. incompatibilidade microlente–raio;
11. coerência de profundidade de foco;
12. assinatura de correção digital versus curvatura física.

## 9. Falsificadores

A hipótese de coerência óptica perde suporte quando o mapa de nitidez, vinheta e chief-ray angle não pode ser explicado por qualquer combinação plausível de lente, sensor plano/curvo e processamento declarado.

## 10. Execução freestanding

Os índices são calculados fora do núcleo, quantizados em Q16.16 e inseridos como bloco focal. O núcleo não executa ray tracing nem ponto flutuante; apenas agrega evidência, contradição e confiabilidade.

## 11. Referências

- Guenter, B. et al. *Highly curved image sensors: a practical approach for improved optical performance* (2017).
- Lombardo, S. et al. *Curved detectors developments and characterization: application to astronomical instruments* (2018).
- Miller, E. D. et al. *Curved detectors for future X-ray astrophysics missions* (2024).

## Regra final

A imagem não nasce no plano: ela é forçada ao plano ou recebida por uma superfície compatível. Essa diferença deve ser tratada como assinatura física de primeira ordem.
