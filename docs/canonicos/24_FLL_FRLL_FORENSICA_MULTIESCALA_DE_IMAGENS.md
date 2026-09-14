# 24 — FLL/FRLL: Forense Multiescala de Imagens e Coerência Relacional

## Estado epistemológico

Este documento define uma extensão metodológica do ecossistema RLL para análise forense de imagens. Não constitui prova automática de autenticidade. Toda conclusão deve ser classificada como `VERIFIED`, `DECLARED_BY_AUTHOR`, `TOKEN_VAZIO` ou `CONTRADICTION`, conforme a cadeia de evidência disponível.

## 1. Hipóteses

\[
\mathcal H=\{H_R,H_S,H_P,H_T\}
\]

- `H_R`: captura fotográfica física;
- `H_S`: síntese GAN/difusão/render;
- `H_P`: fotografia fortemente processada;
- `H_T`: refotografia de tela.

## 2. Campo FLL

A camada FLL — *Forensic Likelihood Layer* — mede a razão de verossimilhança entre hipóteses:

\[
\Lambda_{FLL}^{a,b}(I)=\log\frac{p(\mathbf x(I)\mid H_a)}{p(\mathbf x(I)\mid H_b)}
\]

com:

\[
\mathbf x=[x_1,\ldots,x_{20}]^\top
\]

Os vinte componentes são:

1. coerência física da iluminação;
2. PRNU e ruído de sensor;
3. consistência óptica;
4. geometria facial não-identitária;
5. coerência de oclusão;
6. reflexos especulares;
7. microtextura de pele e materiais;
8. topologia de cabelo, barba e fibras;
9. continuidade do fundo;
10. profundidade de campo;
11. bordas e halos;
12. JPEG, quantização e dupla compressão;
13. metadados e cadeia de custódia;
14. distribuição de frequência;
15. dimensão fractal;
16. densidade de bordas;
17. entropia luminosa;
18. simetria global;
19. clipping e faixa dinâmica;
20. anomalias semântico-geométricas.

## 3. Campo direcional de 14 componentes

\[
\mathbf g=[g_h,g_v,g_{d+},g_{d-},g_r,g_t,g_z,g_{sf},g_{sm},g_{sg},g_x,g_\omega,g_p,g_\tau]
\]

Interpretação:

1. horizontal; 2. vertical; 3. diagonal positiva; 4. diagonal negativa; 5. radial; 6. tangencial; 7. profundidade; 8. fina; 9. média; 10. global; 11. espacial; 12. frequencial; 13. fotométrica; 14. topológica.

Derivadas orientadas:

\[
G_\theta=G_x\cos\theta+G_y\sin\theta
\]

## 4. Fórmulas dos vinte índices

### 4.1 Luz
\[
E_L=\sum_{p\in\Omega}\|\nabla I(p)-\hat\nabla_L(p)\|_2^2
\]

### 4.2 Sensor/PRNU
\[
W=I-F(I),\qquad \rho_K=\frac{\langle W,K\rangle}{\|W\|\|K\|}
\]

### 4.3 Óptica
\[
r_d=r(1+k_1r^2+k_2r^4+k_3r^6)
\]

### 4.4 Geometria
\[
E_G=\sum_{(i,j)}w_{ij}|d_{ij}/s-\mu_{ij}|
\]

### 4.5 Oclusão
\[
C_O=1-\frac{N_{cycles}+N_{viol}}{N_{edges}+\varepsilon}
\]

### 4.6 Especularidade
\[
\mathbf r=2(\mathbf n\cdot\mathbf l)\mathbf n-\mathbf l
\]

### 4.7 Microtextura
\[
LBP_{P,R}(p)=\sum_{k=0}^{P-1}s(g_k-g_p)2^k
\]

### 4.8 Fibras
\[
T_F=\frac{N_{junctions}+N_{crossings}+N_{endpoints}}{A}
\]

### 4.9 Fundo
\[
E_B=\sum_e\|\Delta\theta_e\|+\lambda|\Delta\kappa_e|
\]

### 4.10 Desfoque
\[
c=\frac{A|z-z_f|}{z}\frac{f}{z_f-f}
\]

### 4.11 Halo
\[
H_E=\mathbb E_e|I(e^-)+I(e^+)-2I(e)|
\]

### 4.12 JPEG
\[
Q_{uv}=\operatorname{round}(DCT_{uv}/q_{uv})
\]

### 4.13 Custódia
\[
C_{chain}=H(f_0)\Vert H(f_1)\Vert\cdots\Vert H(f_n)
\]

### 4.14 FFT
\[
F(u,v)=\sum_{x,y}I(x,y)e^{-j2\pi(ux/M+vy/N)}
\]

### 4.15 Fractalidade
\[
D_B=-\lim_{\epsilon\to0}\frac{\log N(\epsilon)}{\log\epsilon}
\]

### 4.16 Bordas
\[
\delta_E=\frac{|\{p:\|\nabla I(p)\|>\tau\}|}{|\Omega|}
\]

### 4.17 Entropia
\[
H_Y=-\sum_kp_k\log_2p_k
\]

### 4.18 Simetria
\[
S=1-\frac{\|I-\mathcal M(I)\|_1}{\|I\|_1+\varepsilon}
\]

### 4.19 Clipping
\[
C_{clip}=\frac{N(I\le\tau_b)+N(I\ge255-\tau_w)}{N}
\]

### 4.20 Semântica geométrica
\[
E_{SG}=\sum_m\alpha_m d(\phi_m(I),\mathcal C_m)
\]

## 5. FRLL — Fractal Relational Likelihood Layer

FRLL amplia FLL por escala, relação e causalidade:

\[
\mathcal F_s(I)=\{D_B(s),H_s,\delta_E(s),A_{FFT}(s),R_{wavelet}(s)\}
\]

\[
\Lambda_{FRLL}=\sum_s\beta_s\Lambda_{FLL}^{(s)}+
\sum_{i<j}\gamma_{ij}I(z_i;z_j)-
\lambda\mathcal E_{contra}
\]

A penalidade relacional é:

\[
\mathcal E_{contra}=E(sensor,lens)+E(light,geometry)+E(texture,codec)+E(topology,semantic)
\]

A distribuição posterior é:

\[
P(H_h\mid I)=\frac{e^{\Lambda_h}}{\sum_{q\in\mathcal H}e^{\Lambda_q}}
\]

## 6. Latentes

\[
\mathbf z=[z_{sensor},z_{lens},z_{codec},z_{light},z_{geometry},z_{texture},z_{topology},z_{semantic},z_{generator}]
\]

Latentes mínimos:

- `z_sensor`: PRNU, shot noise, read noise, CFA e demosaicing;
- `z_lens`: MTF, distorção, vinheta, aberração cromática;
- `z_codec`: quantização, subsampling, double-JPEG, ringing;
- `z_light`: número/direção/cor/intensidade das fontes;
- `z_geometry`: pose, perspectiva, profundidade, epipolaridade;
- `z_texture`: wavelets, autocorrelação, LBP, GLCM;
- `z_topology`: junções T, oclusões e continuidade de contorno;
- `z_semantic`: compatibilidade material–forma–ambiente;
- `z_generator`: fingerprints de GAN/difusão, resíduos de upsampling e erro de reconstrução.

Representação variacional:

\[
\mathcal L_{ELBO}=\mathbb E_{q_\phi(z|I)}[\log p_\theta(I|z)]-D_{KL}(q_\phi(z|I)\|p(z))
\]

## 7. Correspondência FLL/FRLL com a estrutura RLL

A analogia operacional é:

\[
\text{FLL}: \text{evidência local}\rightarrow\text{verossimilhança}
\]

\[
\text{FRLL}: \text{evidência local}\oplus\text{escala}\oplus\text{relações}\rightarrow\text{coerência global}
\]

Definição formal de coerência forense relacional:

\[
C_{FRLL}=1-\frac{\mathcal E_{contra}}{\mathcal E_{max}+\varepsilon}
\]

Score composto:

\[
R_{FRLL}=C_{FRLL}\cdot(1-H_{pred})\cdot Q_{chain}\cdot Q_{cal}
\]

onde `H_pred` é a entropia da posterior, `Q_chain` é a qualidade da cadeia de custódia e `Q_cal` é a qualidade de calibração.

## 8. Oito níveis

1. contêiner;
2. pixel;
3. borda;
4. objeto;
5. cena;
6. frequência/fractalidade;
7. hipóteses concorrentes;
8. decisão calibrada e auditável.

## 9. Pipeline reprodutível

1. preservar bytes originais;
2. gerar SHA-256 e BLAKE3;
3. identificar MIME real;
4. extrair EXIF/XMP/ICC/quantização;
5. linearizar cor;
6. calcular resíduos com múltiplos denoisers;
7. medir CFA/PRNU;
8. medir JPEG/FFT/wavelets;
9. estimar luz/perspectiva/profundidade/oclusão;
10. calcular 20 índices × 14 direções × múltiplas escalas;
11. inferir FLL;
12. inferir FRLL;
13. calibrar;
14. executar ablação;
15. emitir mapas, JSON, hashes e manifesto.

## 10. Validação

- divisão por câmera e gerador;
- open-set para geradores não vistos;
- recompressão, resize, crop, blur, screenshot e redes sociais;
- AUROC, AUPRC, EER, FPR@95TPR, Brier e ECE;
- bootstrap estratificado;
- ablação leave-one-index-out;
- conformal prediction;
- `TOKEN_VAZIO` quando faltarem original, referência de sensor ou cadeia de custódia.

## 11. Referências bibliográficas

1. Lukas, J.; Fridrich, J.; Goljan, M. *Digital Camera Identification from Sensor Pattern Noise*. IEEE TIFS, 2006.
2. Popescu, A. C.; Farid, H. *Exposing Digital Forgeries in Color Filter Array Interpolated Images*. IEEE TSP, 2005.
3. Farid, H. *Exposing Digital Forgeries from JPEG Ghosts*. IEEE TIFS, 2009.
4. Fridrich, J.; Soukal, D.; Lukáš, J. *Detection of Copy-Move Forgery in Digital Images*. DFRWS, 2003.
5. Bayar, B.; Stamm, M. C. *A Deep Learning Approach to Universal Image Manipulation Detection*. IH&MMSec, 2016.
6. Cozzolino, D.; Poggi, G.; Verdoliva, L. *Recasting Residual-based Local Descriptors as CNNs*. IH&MMSec, 2017.
7. Marra, F. et al. *Do GANs Leave Artificial Fingerprints?* MIPR, 2019.
8. Wang, S.-Y. et al. *CNN-Generated Images Are Surprisingly Easy to Spot... for Now*. CVPR, 2020.
9. Verdoliva, L. *Media Forensics and DeepFakes: an Overview*. IEEE JSTSP, 2020.
10. Wang, Z. et al. *DIRE for Diffusion-Generated Image Detection*. ICCV, 2023.
11. Ma, R. et al. *Exposing the Fake: Effective Diffusion-Generated Images Detection*. 2023.
12. Coccomini, D. A. et al. *Detecting Images Generated by Diffusers*. 2023.
13. Tailanian, M. et al. *Diffusion Models Meet Image Counter-Forensics*. 2023.

## 12. Falsificadores

A hipótese de captura física perde suporte quando:

- não existe coerência entre lente, sensor e codec;
- sombras e reflexos exigem fontes incompatíveis;
- oclusões e junções formam relações topologicamente impossíveis;
- resíduos de upsampling ou reconstrução de difusão dominam múltiplas escalas;
- o detector falha sistematicamente em open-set ou após recompressão.

A hipótese sintética perde suporte quando existe cadeia de custódia original, PRNU consistente, CFA coerente, óptica plausível e ausência robusta de fingerprints sintéticos sob múltiplas transformações.

## 13. Regra final

Realismo visual não equivale a realidade física. A inferência válida exige convergência entre aquisição, óptica, geometria, textura, topologia, semântica e proveniência.
