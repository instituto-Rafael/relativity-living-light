# Cânone 29 V2 — Espectrometria Cosmológica da Matéria e Ambientes Planetários

**Status:** contrato estrutural público, auditável e `claim_allowed=false`  
**Data:** 2026-07-30  
**Repositório canônico:** `instituto-Rafael/relativity-living-light`  
**Escopo:** integrar observação remota e *in situ* da composição de atmosferas, superfícies, plasmas e ambientes planetários sem confundir sinal, reconstrução, modelo e matéria física.

---

## 1. Correção de linguagem

**Fotônico não significa apenas fotografia ou luz visível.** Rádio, micro-ondas, infravermelho, visível, ultravioleta, raios X e raios gama pertencem ao espectro eletromagnético e podem ser tratados como radiação fotônica. A faixa visível é apenas uma janela pequena.

Unidades não podem ser confundidas:

| Valor | Região aproximada |
|---|---|
| `350 nm = 0,35 µm` | ultravioleta próximo, fora do visível usual |
| `450 nm = 0,45 µm` | azul visível |
| `350 µm = 350 000 nm` | infravermelho distante/submilimétrico |

As fronteiras variam por convenção instrumental; toda classificação deve registrar a régua utilizada.

## 2. Invariante material

\[
\boxed{
\text{objeto físico}
\neq
\text{radiação/partícula emitida}
\neq
\text{sinal recebido}
\neq
\text{dado calibrado}
\neq
\text{parâmetro recuperado}
\neq
\text{composição inferida}
}
\]

Uma linha espectral não é, sozinha, a substância inteira. Ela é uma assinatura condicionada por abundância, temperatura, pressão, ionização, velocidade, geometria, opacidade, instrumento e modelo.

## 3. Ubiquidade de observação

A logística passa a ter quatro famílias separadas.

### 3.1 Espectrometria eletromagnética remota

- rádio e linhas hiperfinas;
- micro-ondas/submilimétrico e transições rotacionais;
- infravermelho e transições vibracionais/ro-vibracionais;
- visível/UV e transições eletrônicas;
- raios X e estados altamente ionizados/fluorescência;
- raios gama e processos nucleares/altas energias;
- fotometria, espectroscopia, polarimetria, interferometria e imagem hiperespectral.

### 3.2 Sensoriamento eletromagnético ativo

- radar e radar de abertura sintética;
- altimetria;
- lidar;
- laser de ablação e LIBS;
- Raman;
- fluorescência de raios X.

Esses métodos emitem energia conhecida e medem a resposta do alvo.

### 3.3 Espectrometria de partículas e nuclear

- espectrometria de massa de íons e neutros;
- analisadores de plasma;
- poeira e grãos;
- raios cósmicos;
- espectrometria gama e de nêutrons para abundâncias elementares de superfícies;
- detectores de partículas energéticas.

Neutrinos e ondas gravitacionais são mensageiros físicos, mas não devem ser renomeados como espectrometria fotônica.

### 3.4 Provas de campo, estrutura e interior

- massa e raio;
- campo gravitacional e harmônicos;
- sismologia;
- campo magnético e indução;
- dinâmica orbital;
- marés;
- densidade média e equação de estado.

Essas provas restringem o interior, mas normalmente não fornecem uma composição química direta e única.

## 4. O que pode ser inferido

| Camada | Observáveis principais | Inferências possíveis | Limite |
|---|---|---|---|
| Atmosfera | transmissão, emissão, reflexão, ocultação, linhas Doppler, polarização | espécies, abundâncias, razão isotópica, temperatura, pressão, vento, ionização, nuvens/aerossóis | degenerescência entre composição, nuvens, temperatura, estrela e modelo |
| Superfície | refletância VIS/NIR/SWIR, emissão térmica, Raman, LIBS, XRF, gama/nêutrons, radar | minerais, elementos, gelo, hidratação, rugosidade, propriedades térmicas | mistura de pixels, intemperismo espacial, profundidade limitada |
| Plasma/magnetosfera | rádio, UV, X, partículas, rotação de Faraday | densidade eletrônica, energia, composição iônica, campos e aceleração | forte dependência de geometria e não equilíbrio |
| Interior | massa-raio, gravidade, sismologia, magnetismo | densidade, camadas, núcleo, estado térmico, famílias de composição | solução geralmente não única |

## 5. Física das assinaturas

A interação dominante deve ser registrada:

```text
rotacional         → rádio/micro-ondas/submilimétrico
vibracional        → infravermelho
eletrônica         → visível/ultravioleta
ionização interna  → raios X
nuclear            → raios gama
espalhamento       → contínuo, polarização, tamanho de partículas
absorção colisional→ pressão/densidade
Doppler            → velocidade/temperatura
Zeeman/Faraday     → campo magnético
```

O fluxo detectado é uma composição de operadores:

\[
D =
\mathcal R_{\rm inst}
\circ
\mathcal T_{\rm meio}
\circ
\mathcal E_{\rm fonte}
(\theta_{\rm físico})
+
N
\]

e a recuperação é um problema inverso:

\[
p(\theta_{\rm físico}\mid D,M)
\propto
p(D\mid\theta_{\rm físico},M)\,
p(\theta_{\rm físico}\mid M)
\]

O modelo \(M\), os *priors* e as degenerescências devem acompanhar qualquer composição publicada.

## 6. Temperatura, pressão e fase

A temperatura pode ser restringida por:

- forma do contínuo térmico e temperatura de brilho;
- razão entre linhas;
- largura Doppler;
- equilíbrio de excitação/ionização;
- curvas de fase e eclipses;
- perfis verticais em ocultações.

A pressão pode ser restringida por alargamento colisional, absorção induzida por colisão, escala de altura e modelos radiativos.

A fase sólida, líquida ou gasosa não deve ser declarada apenas pela presença de um elemento. Exige combinação de temperatura, pressão, química, equilíbrio/não equilíbrio e contexto dinâmico.

O exemplo de ferro é fisicamente fértil: ferro neutro/ionizado pode ser detectado como gás em atmosferas muito quentes; em regiões mais frias, modelos e observações podem sustentar condensação. Porém, “ciclo completo sólido–líquido–gasoso” exige evidência específica por objeto.

## 7. Atmosferas de exoplanetas

Os modos canônicos são:

1. **transmissão:** luz estelar filtrada pela atmosfera durante o trânsito;
2. **emissão/eclipses secundários:** radiação térmica e refletida do planeta;
3. **reflexão e imagem direta:** albedo, nuvens, moléculas e superfície quando acessível;
4. **alta resolução:** linhas individuais, velocidades, ventos e rotação;
5. **curvas de fase:** contraste dia-noite e transporte térmico;
6. **ocultações e trânsito de alta precisão:** perfis e escalas de altura.

Cada recuperação deve declarar:

```yaml
stellar_model:
instrument_response:
wavelength_or_energy_axis:
spectral_resolution:
line_database:
radiative_transfer_model:
temperature_pressure_profile:
cloud_aerosol_model:
priors:
covariance:
systematics:
retrieval_code_version:
posterior:
alternative_models:
falsifier:
```

## 8. Composição de planetas do Sistema Solar

A composição pode combinar:

- espectroscopia remota de refletância e emissão;
- câmeras multiespectrais/hiperespectrais;
- radares de superfície e subsuperfície;
- espectrômetros gama/nêutrons;
- XRF, APXS, LIBS e Raman;
- espectrometria de massa;
- cromatografia e análise de gases;
- medições meteorológicas;
- gravidade, sismologia e magnetismo.

A palavra “toda” significa **cobertura por camadas e réguas**, não promessa de reconstrução total. Cada técnica vê uma profundidade, resolução e conjunto de espécies diferente.

## 9. Visualização e renderização

\[
\text{hipercubo espectral}
\rightarrow
\text{seleção de bandas}
\rightarrow
\text{normalização}
\rightarrow
\text{mapeamento de canais}
\rightarrow
\text{imagem}
\]

RGB é uma projeção de três canais. Uma câmera hiperespectral pode ter dezenas ou centenas de bandas por pixel. Falsa cor é válida quando a transformação é declarada.

Obrigatório para uma imagem científica pública:

```yaml
source_dataset:
license:
instrument:
observation_time:
spectral_bands:
physical_units:
calibration:
psf_lsf:
reprojection:
background:
normalization:
transfer_function:
clipping:
smoothing:
channel_mapping:
color_space:
uncertainty_mask:
provenance_hash:
```

## 10. Setor escuro

Espectrometria da matéria bariônica pode fornecer redshifts, velocidades, temperaturas, massas de gás e traçadores da estrutura. Esses dados restringem modelos cosmológicos.

Ainda assim:

```yaml
dark_matter_direct_chemical_spectrum: NOT_ESTABLISHED
dark_energy_as_photon_destination: NOT_ESTABLISHED
authorial_source_receiver_analogy: HYPOTHESIS
operational_prediction: TOKEN_VAZIO
claim_allowed: false
```

Para sair de hipótese, é necessária uma previsão quantitativa que difira de \(\Lambda\)CDM/controles, um observável, um dataset e um falsificador.

## 11. Segurança de publicação e CI

### Público no Instituto Rafael

Pode conter:

- contratos, schemas e validadores;
- taxonomias científicas;
- exemplos sintéticos;
- referências públicas;
- resultados reproduzíveis sem segredos;
- receipts e hashes;
- limitações e resultados negativos.

### Privado/local

Deve permanecer fora do CI público:

- credenciais;
- dados pessoais;
- exportações de conversa;
- datasets restritos;
- estratégia autoral ainda não divulgável;
- caminhos locais;
- resultados sem revisão que possam ser confundidos com descoberta.

A ausência de crédito em CI privado não é prova científica nem falha do código. O estado deve ser:

```text
PRIVATE_CI_NOT_EXECUTED_BILLING_CONSTRAINT
```

e a validação pode ocorrer localmente no Termux com receipt, sem fingir execução remota.

## 12. Gates

Uma inferência de composição só avança quando:

\[
G =
G_{\rm provenance}
\land
G_{\rm license}
\land
G_{\rm calibration}
\land
G_{\rm response}
\land
G_{\rm units}
\land
G_{\rm uncertainty}
\land
G_{\rm model}
\land
G_{\rm alternatives}
\land
G_{\rm falsifier}
\]

Falha em qualquer gate produz `TOKEN_VAZIO` ou `claim_allowed=false`.

## 13. Falsificadores mínimos

- a espécie desaparece ao trocar banco de linhas;
- o sinal é explicado por contaminação estelar;
- a abundância depende somente do *prior*;
- a linha não sobrevive à resposta instrumental;
- nuvens/aerossóis reproduzem o mesmo espectro;
- a temperatura muda fora da incerteza ao alterar o contínuo;
- a composição muda materialmente após covariância e sistemáticos;
- a associação espacial desaparece ao equalizar PSF;
- a fase proposta viola o diagrama pressão–temperatura;
- a hipótese cosmológica não supera controles ou não gera previsão distinta.

## 14. Referências públicas de base

- NASA Science, *Spectroscopy 101 — Light and Matter*.
- NASA Science, *Spectroscopy 101 — Types of Spectra and Spectroscopy*.
- NASA/ESA/CSA Webb, espectros de transmissão de atmosferas de exoplanetas.
- ESA, CIRS/Cassini: composição, temperatura e perfis atmosféricos no infravermelho.
- NASA Dawn, VIR e GRaND: mineralogia, temperatura e abundância elementar.
- NASA Planetary Data System, espectrometria gama/nêutrons.
- ESO ESPRESSO, ferro gasoso e condensação em WASP-76 b.
- IVOA Spectrum Data Model; FITS e WCS.

## Ω — fechamento

```yaml
F_ok:
  - repositório canônico movido para instituto-Rafael
  - fotônico separado de visível/fotografia
  - métodos remotos, ativos, nucleares, de partículas e de interior separados
  - atmosfera, superfície, plasma e interior tratados por réguas próprias
  - temperatura, pressão, fase e composição possuem gates
  - 350_nm e 350_um não são confundidos
F_gap:
  - datasets reais por missão
  - matrizes de resposta
  - bancos de linhas fixados por versão
  - retrievals e covariâncias reais
  - revisão científica independente
F_next:
  - selecionar um dataset público pequeno
  - executar uma recuperação sintética controlada
  - comparar modelos alternativos
claim_allowed: false
```

*O espectro é a pegada da matéria, não a matéria inteira. A régua correta transforma a pegada em hipótese testável.*
