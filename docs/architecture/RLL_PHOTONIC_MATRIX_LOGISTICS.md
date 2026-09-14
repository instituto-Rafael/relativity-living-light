# RLL Photonic Matrix Logistics

**Status:** arquitetura proposta, ainda não validação física.  
**Estados epistêmicos aplicáveis:** `VERIFIED`, `DECLARED_BY_AUTHOR`, `TOKEN_VAZIO`, `CONTRADICTION`.

## 1. Objetivo

Transformar a luz no RLL de uma variável escalar isolada em um estado matricial propagável, com cadeia explícita de fonte, transporte, interação, detecção, inferência e falsificação.

A logística fotônica é definida como:

\[
\mathbf{s}_{k+1}=\mathcal{D}_k\,\mathcal{M}_k\,\mathcal{T}_k\,\mathbf{s}_k+\boldsymbol\eta_k,
\]

onde:

- \(\mathbf{s}_k\): estado fotônico no passo/camada \(k\);
- \(\mathcal{T}_k\): propagação geométrica e temporal;
- \(\mathcal{M}_k\): interação com matéria/campo;
- \(\mathcal{D}_k\): resposta do detector ou operador observacional;
- \(\boldsymbol\eta_k\): ruído, perda ou informação não observada.

## 2. Estado mínimo da Matrix

Para cada célula espacial, instante e banda espectral:

\[
\mathbf{s}(t,\mathbf{x},\lambda)=
\begin{bmatrix}
I\\Q\\U\\V\\n_\gamma\\\tau\\j_\lambda\\\alpha_\lambda\\\phi\\\sigma
\end{bmatrix},
\]

com:

- \(I,Q,U,V\): parâmetros de Stokes;
- \(n_\gamma\): densidade ou contagem de fótons;
- \(\tau\): profundidade óptica;
- \(j_\lambda\): emissividade;
- \(\alpha_\lambda\): absorção;
- \(\phi\): fase, quando coerência for fisicamente relevante;
- \(\sigma\): incerteza associada.

Campos ausentes não devem ser preenchidos com zero. Devem usar máscara de validade e estado `TOKEN_VAZIO`.

## 3. Dimensões recomendadas

A matriz operacional pode ser armazenada como tensor:

\[
\mathsf{P}[t,z,\varphi,\lambda,p,c],
\]

onde:

- \(t\): ciclo ou instante;
- \(z\): camada/altitude/distância comóvel;
- \(\varphi\): célula espacial ou direção angular;
- \(\lambda\): banda espectral;
- \(p\): polarização;
- \(c\): canal físico ou observacional.

Uma implementação inicial deve evitar uma matriz global densa. Usar blocos esparsos e janelas por domínio:

1. geofísico local;
2. heliosférico-radiativo;
3. cosmológico.

## 4. Operadores fundamentais

### 4.1 Transporte

\[
\frac{1}{c}\frac{\partial I_\nu}{\partial t}+\hat n\cdot\nabla I_\nu
=j_\nu-\alpha_\nu I_\nu+\mathcal{S}_\nu[I].
\]

### 4.2 Propagação matricial

\[
\mathbf{s}_{out}=\mathbf{M}_{N}\mathbf{M}_{N-1}\cdots\mathbf{M}_{1}\mathbf{s}_{in}.
\]

Cada \(\mathbf M_i\) deve possuir:

- domínio físico;
- unidades;
- hipótese;
- referência bibliográfica;
- versão;
- intervalo de validade;
- teste unitário;
- falsificador.

### 4.3 Geometria e lenteamento

\[
\boldsymbol\beta=\boldsymbol\theta-\boldsymbol\alpha(\boldsymbol\theta),
\qquad
\mathbf A=\frac{\partial\boldsymbol\beta}{\partial\boldsymbol\theta}.
\]

A matriz Jacobiana \(\mathbf A\) pode representar convergência, cisalhamento e magnificação, mas não deve ser usada como prova do modelo RLL sem comparação observacional.

### 4.4 Redshift e resposta instrumental

\[
\lambda_{obs}=(1+z)\lambda_{emit},
\]

\[
\mathbf y=\mathbf R\mathbf s+\boldsymbol\epsilon,
\]

onde \(\mathbf R\) é a matriz de resposta do instrumento.

## 5. Logística de dados

Fluxo canônico:

```text
SOURCE
  -> SPECTRAL_BINNING
  -> GEOMETRY
  -> PROPAGATION
  -> MATTER_FIELD_INTERACTION
  -> REDSHIFT/LENSING
  -> INSTRUMENT_RESPONSE
  -> OBSERVABLE
  -> LIKELIHOOD
  -> CLAIM_GATE
```

Cada etapa gera:

- dados de entrada;
- operador aplicado;
- checksum;
- parâmetros;
- unidades;
- incertezas;
- saída;
- estado epistêmico.

## 6. Contrato computacional

Estrutura mínima sugerida:

```text
src/rll_photonic/
  state.py
  operators.py
  transport.py
  spectral.py
  polarization.py
  detector.py
  likelihood.py
  provenance.py

schemas/
  photonic_state.schema.json
  photonic_operator.schema.json
  photonic_manifest.schema.json

tests/
  test_energy_accounting.py
  test_nonnegative_intensity.py
  test_identity_operator.py
  test_absorption_limit.py
  test_redshift_mapping.py
  test_detector_response.py
```

## 7. Invariantes mínimos

### I1 — não negatividade

\[
I_\lambda\ge 0.
\]

### I2 — limite de polarização

\[
Q^2+U^2+V^2\le I^2.
\]

### I3 — contabilidade de energia

\[
E_{in}=E_{out}+E_{absorvida}+E_{espalhada}+E_{TOKEN\_VAZIO}.
\]

### I4 — identidade

Sem interação:

\[
\mathbf M=\mathbf I\Rightarrow\mathbf s_{out}=\mathbf s_{in}.
\]

### I5 — rastreabilidade

Nenhum resultado pode ingressar na likelihood sem manifesto de origem, operador e incerteza.

## 8. Integração com o RLL cosmológico

A Matrix fotônica não substitui \(H(z)\), distâncias cosmológicas ou likelihoods existentes. Ela forma a camada de transporte entre modelo e observável:

\[
\Theta_{RLL}
\xrightarrow{\text{background}}
H(z),D_L,D_A
\xrightarrow{\text{photon matrix}}
\mathbf s_{obs}
\xrightarrow{\text{instrument}}
\mathbf y
\xrightarrow{\text{likelihood}}
\mathcal L.
\]

Isso permite testar separadamente:

1. expansão do fundo;
2. propagação da luz;
3. interação com matéria/campo;
4. resposta instrumental;
5. inferência estatística.

## 9. Primeira implementação viável

Começar com uma Matrix 1D espectral, sem coerência quântica e sem campo completo 3D:

\[
\mathsf P[t,z,\lambda,c].
\]

Canais iniciais:

- intensidade;
- transmissão;
- absorção;
- redshift;
- resposta instrumental;
- incerteza;
- máscara de validade.

Somente depois adicionar polarização, espalhamento múltiplo, lenteamento, magneto-óptica e coerência.

## 10. Falsificadores

A arquitetura falha se:

- produz energia sem termo-fonte;
- viola limites de polarização;
- usa zero para dados ausentes;
- mistura unidades;
- altera likelihood sem registrar o operador;
- melhora ajuste apenas pelo aumento de parâmetros;
- não reproduz limites conhecidos de transporte radiativo.

## 11. Bibliografia-base

- Chandrasekhar, S. *Radiative Transfer*. Dover.
- Rybicki, G. B.; Lightman, A. P. *Radiative Processes in Astrophysics*. Wiley.
- Born, M.; Wolf, E. *Principles of Optics*. Cambridge University Press.
- Mishchenko, M. I. et al. *Multiple Scattering of Light by Particles*. Cambridge University Press.
- Hovenier, J. W. et al. *Transfer of Polarized Light in Planetary Atmospheres*. Springer.
- Schneider, P.; Ehlers, J.; Falco, E. E. *Gravitational Lenses*. Springer.

## 12. Estado atual

- arquitetura: `DECLARED_BY_AUTHOR` / proposta técnica;
- operadores implementados: `TOKEN_VAZIO` até inspeção de código específico;
- validação física: `TOKEN_VAZIO`;
- integração com likelihood real: `TOKEN_VAZIO`;
- valor imediato: separação formal entre emissão, propagação, detecção e inferência.
