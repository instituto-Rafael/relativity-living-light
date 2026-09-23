# RLL — Mecânicas de Ligação e Funcionamento Canônico V1

**status:** ACTIVE / ARCHITECTURE_CONTRACT  
**claim_allowed:** false  
**scope:** modelo físico, dados, observáveis, runtimes, evidência e gates  
**principle:** SOURCE != ARTEFATO != EXECUÇÃO != EVIDÊNCIA != CLAIM

## 1. O que significa "RLL funcionando"

RLL funcionando não é apenas possuir uma equação RLL nem apenas executar um script.

O ciclo funcional mínimo é:

```text
SOURCE
  -> INGESTAO
  -> NORMALIZACAO/TIPAGEM
  -> MODELO
  -> OBSERVAVEL
  -> INCERTEZA/COVARIANCIA
  -> METRICA
  -> AJUSTE OU PERFIL
  -> COMPARACAO COM BASELINE
  -> EVIDENCIA
  -> RECEIPT
  -> CLAIM GATE
```

Se uma ponte material estiver ausente, ela permanece `TOKEN_VAZIO`.

## 2. Núcleo físico implementado

A mecânica cosmológica central do RLL é:

```text
z
 -> f(z)
 -> setor de superposição
 -> E²(z)
 -> H(z)
 -> distâncias/crescimento/CMB
 -> comparação com observação
```

A transição é:

[
f(z)=rac{1}{1+exp((z-z_t)/w_t)}
]

e o background RLL usado pelas rotas atuais é:

[
E^2_{RLL}(z)=
Omega_m(1+z)^3+
Omega_r(1+z)^4+
Omega_Lambda+
Omega_{s0}left[f(z)+(1-f(z))(1+z)^3ight].
]

Na rota de fechamento plano:

[
Omega_Lambda=1-Omega_r-Omega_m-Omega_{s0}.
]

Interpretação operacional do termo de superposição:

- para `z >> z_t`, `f(z) -> 0` e o setor tende a escalar como `(1+z)^3`;
- para `z << z_t`, `f(z) -> 1` e o setor tende a contribuição aproximadamente constante;
- `z_t` localiza a transição;
- `w_t` controla sua largura;
- `Omega_s0` controla a amplitude.

Isso é uma parametrização testável. Não constitui, por si só, uma demonstração do mecanismo microscópico que produziria essa transição.

## 3. Invariante de baseline

A ligação estrutural mais importante é:

[
oxed{Omega_{s0}=0 Rightarrow RLL 	o Lambda CDM	ext{-like background}}
]

Logo:

```text
LCDM
  is nested in
RLL background space
```

Uso do invariante:

1. regressão: RLL deve reproduzir o caminho LCDM quando `Omega_s0=0`;
2. otimização: um ajuste RLL que inclui exatamente esse limite não deve ter mínimo de chi² pior apenas por construção do espaço;
3. AIC/BIC: mesmo quando chi² não piora, parâmetros extras continuam penalizados;
4. ciência: melhor chi² sozinho não autoriza claim.

## 4. Da equação aos observáveis

### 4.1 Expansão

[
H(z)=H_0 E(z).
]

Entrada observacional:
- cronômetros cósmicos / H(z).

Saída:
- residual;
- pull;
- contribuição para chi².

### 4.2 BAO

A expansão gera distância comóvel:

[
D_M(z)=cint_0^z rac{dz'}{H(z')}.
]

A partir dela:

[
D_H/r_d = rac{c}{H(z)r_d},
]

[
D_M/r_d = rac{D_M(z)}{r_d},
]

[
D_V/r_d =
rac{left[z,c,D_M^2(z)/H(z)ight]^{1/3}}{r_d}.
]

Entrada observacional:
- DESI DR2 BAO.

Mecânica:
- previsão -> residual vetorial -> matriz de covariância -> chi².

### 4.3 Crescimento

A rota conjunta atual possui `f sigma8` por aproximação de índice de crescimento.

Estado:
`IMPLEMENTED_APPROXIMATION`.

Gap:
uma evolução validada de `D(z)`/perturbações RLL permanece necessária para promoção científica mais forte.

### 4.4 CMB comprimido

A rota conjunta possui:
- `R`;
- `l_A`;
- `Omega_b h²`;
- covariância 3x3.

Estado:
`IMPLEMENTED_COMPRESSED_PRIOR`.

Boundary:
não substitui a likelihood completa do Planck.

## 5. Mecânica estatística

Para residual `r = observado - previsto`:

[
chi^2=r^T C^{-1}r.
]

Comparação de complexidade:

[
AIC=chi^2_{min}+2k,
]

[
AIC_c=AIC+rac{2k(k+1)}{N-k-1},
]

[
BIC=chi^2_{min}+kln N.
]

Regra:

```text
chi2 menor != modelo confirmado
AIC/BIC menor != mecanismo físico provado
execução reproduzível != validação independente
```

## 6. As quatro rotas que hoje ligam o RLL

### Rota A — Rx / Termux mínimo

```text
JSON/CSV reais
 -> Rx stdlib-only
 -> 32 H(z) + 13 BAO
 -> covariância DESI
 -> LCDM fit
 -> RLL fit
 -> AIC/AICc/BIC
 -> SVG + JSON + CSV
 -> receipt
```

Arquivo:
`validacao_real/run_rx_pipeline.py`

Runtime:
- Python standard library only;
- zero pacote Python de terceiro;
- álgebra, Simpson, busca limitada, IO e SVG em `rx/kernel.py`.

Contagem:
`32 + 13 = 45 observações`.

Estado:
`IMPLEMENTED_UNTESTED_ON_TARGET` até execução observada no Termux após a migração Rx.

### Rota B — H(z) freestanding C

```text
data/real/Hz_data_real.csv
 -> digest/custódia
 -> 33 linhas Q16.16
 -> H_LCDM / H_RLL
 -> residual/sigma
 -> chi²
 -> receipt determinístico
```

Características:
- C freestanding;
- sem heap;
- sem libc no kernel;
- sem `math.h`;
- fixed-point/Q16;
- builds/objetos para x86_64, ARMv7 e AArch64 documentados.

Contagem:
`33 H(z)`.

Estado:
`IMPLEMENTED / VERIFIED_LOCAL`.

### Rota C — Joint freestanding 65

```text
33 H(z)
+ 13 DESI BAO
+ 16 f sigma8
+ 3 CMB
= 65 observações
        |
        v
strict parser + source hashes
        |
        v
typed quantity router
        |
        v
LCDM/RLL evaluator
        |
        v
covariance-aware canonical gate
        |
        v
Q16 receipt
```

Essa rota liga 65/65 observações a previsões de modelo.

Importante:
- usa perfis de parâmetros já registrados;
- não executa nova otimização dentro do callback;
- `model_bound_rows=65` prova ligação executável, não confirmação científica.

Estado:
`IMPLEMENTED / EXECUTABLE / FAIL_CLOSED`.

### Rota D — Structure-D científico amplo

```text
28 H(z)
+ 13 BAO
+ 16 f sigma8
+ 3 CMB
= 60 observáveis atuais
 -> likelihood
 -> LCDM / wCDM / CPL / RLL
 -> optimizer
 -> chi²/AIC/AICc/BIC
 -> evidence scan
```

Hoje essa rota histórica usa:
- NumPy;
- Pandas;
- SciPy.

A sucessora de fechamento plano garante `E(0)=1` por construção.

Foi corrigido um erro de contagem: o código somava apenas `+2` para um vetor CMB de três parâmetros. O `N` atual é derivado como `28+13+16+3=60`.

Estado:
`LEGACY_ACTIVE / RX_MIGRATION_PENDING`.

Ela não deve ser confundida com a rota Rx já dependency-free.

## 7. Por que aparecem 45, 60, 64 histórico e 65 observações

Não são automaticamente a mesma superfície.

```text
Rx inicial:
32 H(z) + 13 BAO = 45

Rx multiprobe / Structure-D atual:
28 H(z) + 13 BAO + 16 f sigma8 + 3 CMB = 60

Structure-D histórico documentado:
N=64 em artefatos anteriores — preservar como histórico; não usar como contagem do snapshot atual

Freestanding joint:
33 H(z) + 13 BAO + 16 f sigma8 + 3 CMB = 65
```

O conjunto freestanding usa o arquivo canônico de 33 linhas H(z). A rota Structure-D atual usa o arquivo independente com 28 linhas. A rota Rx inicial usa o payload de 32 cronômetros da validação simples.

A contagem sempre deve viajar junto com a identificação e o hash do dataset.

## 8. Mecânica de custódia

Antes do número existir como evidência:

```text
arquivo bruto
 -> hash
 -> schema/tipagem
 -> unidade
 -> incerteza
 -> calibração/covariância
 -> modelo registrado
 -> cálculo
 -> receipt
```

Um dado sem unidade, fonte, incerteza ou ligação de modelo não deve entrar silenciosamente no chi².

## 9. Mecânica de claim

Estados:

```text
SOURCE
  -> MATERIALIZED
  -> MODEL_BOUND
  -> EXECUTED
  -> REPRODUCED
  -> INDEPENDENTLY_REPRODUCED
  -> CLAIM_ELIGIBLE
```

Esses estados não são equivalentes.

Hoje:

```text
RLL_EXECUTABLE                    = SIM
REAL_DATA_BINDING                 = SIM
H(z)_FREESTANDING                = PASS_LOCAL
JOINT_65_MODEL_BINDING            = PASS_IMPLEMENTATION
RX_ZERO_DEPENDENCY_ROUTE          = IMPLEMENTED_UNTESTED_ON_TARGET
STRUCTURE_D_RX_MIGRATION          = TOKEN_VAZIO_MIGRATION
FULL_PERTURBATION_RLL             = TOKEN_VAZIO
FULL_PLANCK_LIKELIHOOD            = TOKEN_VAZIO
INDEPENDENT_REPLICATION           = TOKEN_VAZIO
CLAIM_ALLOWED                     = false
```

## 10. O RLL como sistema, não como arquivo

A arquitetura correta é:

```text
                 +------------------+
                 |   REAL SOURCES   |
                 +---------+--------+
                           |
                           v
                 +------------------+
                 | CUSTODY / TYPING |
                 +---------+--------+
                           |
                           v
+-----------+     +------------------+     +-------------+
| LCDM NULL | --> | RLL MODEL SPACE  | --> | OBSERVABLES |
+-----------+     +------------------+     +------+------+
                                                  |
                    +-----------------------------+
                    |
                    v
            +---------------+
            | UNCERTAINTY C |
            +-------+-------+
                    |
                    v
            +---------------+
            | chi2 / AIC/BIC|
            +-------+-------+
                    |
          +---------+----------+
          |                    |
          v                    v
      +------+              +------+
      |  Rx  |              | C/Q16|
      +--+---+              +---+--+
         |                      |
         +----------+-----------+
                    |
                    v
               +---------+
               | RECEIPT |
               +----+----+
                    |
                    v
               +---------+
               |  GATE   |
               +----+----+
                    |
         claim_allowed=false
```

## 11. Definição canônica curta

[
oxed{
RLL_{funcional}
=
Modelo
	imes Dados
	imes Observáveis
	imes Incerteza
	imes Runtime
	imes Baseline
	imes Evidência
	imes Custódia
}
]

Se qualquer elo necessário for ausente, ele não vira zero:

[
elo_{ausente}=TOKEN_VAZIO.
]

## 12. Próxima convergência técnica

A rota natural é fazer o Rx absorver, sem regressão semântica:

1. executar e estabilizar o multiprobe Rx de 60 observações;
2. medir paridade semântica por componente;
3. reconciliar o contrato de crescimento (proxy Structure-D vs D(z) freestanding);
4. reconciliar o contrato acústico CMB (r_d vs r_s(z_star));
5. promover paridade numérica Rx <-> Structure-D na mesma semântica;
6. promover paridade Rx <-> freestanding em uma semântica explicitamente comum;
7. somente depois substituir a dependência externa do Structure-D.

O objetivo não é reescrever matemática acadêmica; é possuir a implementação, a cadeia de custódia e a execução do pipeline.

---

## R3

`F_ok`: modelo RLL, baseline LCDM, H(z), BAO, covariância, Rx e kernels freestanding estão ligados por rotas executáveis/documentadas.

`F_gap`: Rx ainda não cobre todo o multiprobe; perturbações RLL, Planck completo, posterior robusto e reprodução independente continuam abertos.

`F_next`: executar o Rx multiprobe de 60 observações e fechar os contratos de paridade growth/CMB antes de substituir o Structure-D legado.
