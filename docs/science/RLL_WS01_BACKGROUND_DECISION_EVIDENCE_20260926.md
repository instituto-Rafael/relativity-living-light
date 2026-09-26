# RLL WS01 Background Decision Evidence — 2026-09-26

**Autor:** RAFAEL MELO REIS  
**PR:** #993  
**Workflow run:** `36236992273`  
**Artifact:** `10904487612`  
**Artifact digest:** `sha256:6a8fd6416d29fa57f12211ff7930abdf6dca48f1c4b1ce63fd48f840ecb68f60`  
**Estado:** `EVIDENCE_REDUCED_WS01_PARTIAL`  
**claim_allowed:** `false`

## Resultado

O experimento preregistrado reduziu quatro eixos WS01 para dois eixos terminais e dois ainda abertos.

| eixo | resultado |
|---|---|
| H(z) dataset | `PASS_IDENTICAL_PURE_CC_SURFACE` |
| distance integration | `PASS_PREREGISTERED_DISTANCE_TOLERANCE` |
| Omega_r | `MEASURED_NO_PHYSICAL_SELECTION` |
| growth mode | `TOKEN_VAZIO_UNTIL_WS06` |

### H(z): 28 versus 33

O arquivo bruto de 33 linhas contém 28 cosmic chronometers puros e 5 linhas rotuladas BAO ou CC+BAO. Sob a regra canônica de evitar double counting com DESI, as 28 linhas selecionadas são exatamente as mesmas do arquivo independente de 28 linhas.

Portanto o aparente conflito de superfícies é reduzido sem escolher pelo ajuste:

```text
raw 33 -> anti-double-count selection -> 28 pure CC
independent surface             -> 28 pure CC
row-level equality              -> PASS
fixed-vector H(z) chi2 equality -> PASS
```

A superfície científica canônica pode usar `data/real/cosmology/Hz_cosmic_chronometers_independent.csv`; a superfície 33 permanece como projeção/paridade nomeada.

### Integração de distância

Gate preregistrado:

```text
method = log1p_simpson
steps = 2048
max rel error vs scipy.quad <= 1e-8
max rel delta 2048->4096   <= 1e-8
```

Observado:

```text
max rel error vs scipy.quad = 6.185615356109645e-13
max rel delta 2048->4096    = 5.820642422073455e-13
```

O método passa com ampla margem no domínio testado.

### Omega_r

As duas convenções existentes foram comparadas sem seleção por fit:

```text
9.00e-5
9.18e-5
```

Máximos observados no grid declarado:

```text
relative delta H  = 0.0024736895137296927  (~0.24737%)
relative delta DM = 9.420746846093331e-05 (~0.00942%)
```

O limite nulo RLL `Omega_s0=0` permanece compatível com LCDM nos dois braços, mas a sensibilidade em alta-z é real. Por isso `Omega_r` continua `TOKEN_VAZIO` até existir autoridade física explícita para a convenção.

### Growth

Nenhum proxy de background foi promovido. `growth_mode` continua bloqueado até WS06.

## Estado depois do Δ

```text
hz_dataset           = EVIDENCE_TERMINAL
distance_integration = EVIDENCE_TERMINAL
omega_r              = TOKEN_VAZIO_PHYSICAL_AUTHORITY_REQUIRED
growth_mode           = TOKEN_VAZIO_UNTIL_WS06

RX-PHYSICS-CANONICAL-V2 = TOKEN_VAZIO_CONTRACT
claim_allowed = false
```

## Próximo Δ

O próximo ponto de maior alavancagem dentro de WS01 é `omega_r`: substituir a escolha entre dois números fixos por uma convenção física derivada/provenance-backed, com parâmetros e unidades explícitos. Growth não deve ser tocado antes do backend perturbativo.
