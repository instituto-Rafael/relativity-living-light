# RLL Rx — Physics Contract Ledger V1

**status:** ACTIVE / FAIL-CLOSED  
**training:** false  
**ai_runtime:** false  
**claim_allowed:** false

Este ledger separa refatoração de software de mudanças que alterariam a semântica científica.

## Regra

```text
software_refactor != physics_contract_change
numerical_parity != scientific_validation
TOKEN_VAZIO != 0
```

## Contratos atualmente coexistentes

| eixo | Structure-D / Rx parity mode | FASE18E / freestanding | estado |
|---|---|---|---|
| H(z) independente | 28 linhas | 33 linhas canônicas | DATA_SURFACE_DIVERGENCE |
| Ωr | 9.0e-5 | 9.18e-5 | CONTRACT_DIVERGENCE |
| fechamento | ΩΛ derivado na rota flat Rx | ΩΛ=1-Ωm-Ωr-Ωs0 | COMPATIBLE_FORM, constant differs |
| growth | σ8·Ωm(z)^0.55 | f·σ8·D(z), f=Ωm(z)^0.55 | CONTRACT_DIVERGENCE |
| BAO r_d | power-law calibrada em H0, Ωm, Ωb h² | integral c_s/H a partir de z_drag EH98 | CONTRACT_DIVERGENCE |
| CMB l_A | π D_M / r_d | π D_M / r_s(z*) | CONTRACT_DIVERGENCE |
| r_s(z*) | não separado no legado Structure-D | integral sonora + calibração Planck documentada | CONTRACT_DIVERGENCE |
| DESI covariance | 13x13 commitada | pares correlacionados / rota canônica | IMPLEMENTATION_VARIANT |
| CMB covariance | 3x3 | 3x3 | SHARED |
| optimizer | SciPy differential_evolution | perfis fixos no kernel C; otimizações históricas separadas | EXECUTION_DIVERGENCE |
| runtime | NumPy/Pandas/SciPy legado | C freestanding | RUNTIME_DIVERGENCE |
| Rx | stdlib-only, modos explícitos | projeção parcial disponível | MIGRATION_BRIDGE |

## O que pode ser feito automaticamente

Estas mudanças são engenharia e não escolhem nova física:

1. substituir IO NumPy/Pandas por CSV/JSON Rx;
2. substituir álgebra SciPy/NumPy por `rx/kernel.py`;
3. preservar matriz de covariância e ordem dos observáveis;
4. derivar N diretamente dos arquivos;
5. preservar parâmetros, bounds e seeds em receipts;
6. criar paridade por componente;
7. separar perfis históricos e resultados novos;
8. remover dependência externa do runtime ativo;
9. manter `claim_allowed=false`;
10. registrar rollback.

## O que NÃO deve ser unificado silenciosamente

### 1. Ωr

```text
Structure-D / Rx parity: 9.0e-5
FASE18E / freestanding: 9.18e-5
```

Escolher um valor único muda E²(z), sobretudo em alta redshift.

### 2. Crescimento

```text
Structure-D:
fσ8(z) = σ8 · Ωm(z)^0.55

freestanding:
fσ8(z) = Ωm(z)^0.55 · σ8 · D(z)
```

A segunda possui evolução de amplitude D(z). Isso não é uma mera troca de biblioteca.

### 3. Horizonte sonoro

Structure-D usa uma aproximação power-law para `r_d`.

FASE18E possui:

[
z_{drag}=z_{drag}^{EH98}(omega_m,omega_b)
]

[
r_d=int_{z_{drag}}^infty rac{c_s(z)}{H(z)}dz
]

e separa:

[
r_s(z_*)=int_{z_*}^infty rac{c_s(z)}{H(z)}dz.
]

Portanto `r_d` e `r_s(z*)` não devem ser tratados como sinônimos.

### 4. CMB acoustic scale

[
l_A=pi D_M(z_*)/r_s(z_*).
]

Usar `r_d` no denominador é uma aproximação histórica do Structure-D e permanece identificada como tal.

## Contratos versionados propostos

### RX-STRUCTURE-D-PARITY-V1

Objetivo: reproduzir a semântica atual do Structure-D sem NumPy/Pandas/SciPy.

- Ωr = 9.0e-5
- growth = proxy sem D(z)
- r_d = power-law
- CMB l_A usa r_d
- H(z) = arquivo independente atual
- DESI = matriz 13x13
- CMB = matriz 3x3
- runtime = Rx stdlib-only

Estado: `CI_VERIFIED_ENGINEERING_PARITY` (workflow `Validacao Real RLL`, run `35817865087`, head `4eecebb180467500f7bd32cca4e09d1efe92004f`).

### RX-FREESTANDING-PROJECTION-V1

Objetivo: medir aproximação em direção ao kernel C sem alegar paridade binária.

- growth com D(z)
- r_d de perfil freestanding quando usado pelo ledger
- r_s(z*) separado para CMB
- Ωr ainda não alterado automaticamente no Rx comum

Estado: `PARTIAL_PROJECTION / CONTRACT_DIVERGENCE`.

### RX-PHYSICS-CANONICAL-V2

Objetivo futuro: uma única semântica física compartilhada entre Rx e C.

Requer antes:

1. decisão/versionamento de Ωr;
2. implementação stdlib da integral sonora;
3. definição documentada de z_drag;
4. definição de r_s(z*) e sua calibração;
5. definição final de growth/D(z);
6. vetores de referência Rx↔C;
7. tolerâncias numéricas por observável;
8. nova execução independente.

Estado: `TOKEN_VAZIO_CONTRACT`.

## Critério para aposentadoria do Structure-D externo

O legado NumPy/Pandas/SciPy só pode deixar de ser referência quando:

```text
RX_SELFTEST=PASS
AND RX_MULTIPROBE=PASS_EXECUTION
AND SAME_INPUT_HASHES
AND SAME_PHYSICS_CONTRACT
AND COMPONENT_PARITY_WITHIN_TOLERANCE
AND RECEIPT_COMPLETE
AND ROLLBACK_AVAILABLE
```

Não basta o script Rx rodar.

## Condição de parada desta rodada

A engenharia pode avançar até o ponto em que a próxima alteração escolheria física entre contratos divergentes.

Esse ponto foi alcançado.

O sistema agora possui:

- runtime Rx;
- pipeline simples;
- multiprobe;
- selftest;
- semantic parity ledger;
- dependency audit;
- aggregate development gate;
- one-command development chain;
- contagem atual derivada dos dados;
- divergências físicas explicitadas.

A próxima mudança científica deve nascer como novo contrato versionado, não como refatoração silenciosa.

## R3

**F_ok:** desenvolvimento dependency-free estruturado até o gate de contrato físico.

**F_gap:** Ωr, growth, r_d/r_s e superfície H(z) ainda diferem entre famílias históricas.

**F_next:** implementar `RX-PHYSICS-CANONICAL-V2` somente com cada decisão física explicitamente versionada e validada contra vetores de referência.


## Fechamento de dependência validacao_real — 2026-09-23

A família de serialização/apresentação do bundle legado `validacao_real` foi migrada sem alterar as equações fixed-point históricas:

- PyYAML -> JSON stdlib/versionado;
- Matplotlib -> renderer SVG de `rx.kernel`;
- YAMLs históricos preservados;
- paridade YAML->JSON validada ponto a ponto;
- core `fetch_real_data.py + compute_validation.py + make_figures.py + render_report.py` com zero imports Python de terceiros;
- CI run `35817865087`: PASS;
- migration plan: `closed_families=1`;
- aggregate: `PASS_WITH_OPEN_CONTRACT_DIVERGENCES`.

Isto fecha uma família de engenharia, não escolhe física e não promove claim.
