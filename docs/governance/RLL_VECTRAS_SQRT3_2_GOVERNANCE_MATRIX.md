# Governance Matrix: RLL ↔ Vectras ↔ sqrt(3)/2

## Status

`governance_record / friction_map / claim_boundary / no_claim_promotion`

Last updated: 2026-07-11

## Purpose

Este documento mapeia a invariante estrutural em fricção entre a camada científica do
RLL, a camada runtime do Vectras e o kernel `sqrt(3)/2`, preservando o que é mensurável,
separando o que é hipótese e documentando o que ainda está sem forma.

Este documento de governança organiza responsabilidades e define guardas epistemológicas.
Ele **não** valida RLL como teoria física nem promove o kernel a constante universal.

## Pergunta-raiz

Como transformar `sqrt(3)/2` de insight geométrico em arquitetura verificável sem misturar
indevidamente cosmologia, runtime Android, heurística operacional e prova matemática?

## Eixo central

```text
h = sqrt(3)/2
  -> geometria 30°/60°/120°
  -> malha hexagonal/triangular
  -> filtro recursivo
  -> projeção angular
  -> pivô cosmológico diagnóstico
  -> kernel runtime Q16.16
```

## Separação de responsabilidades

### RLL (este repositório)

Responsável por:

- invariante matemático documentado em `docs/invariants/sqrt3_2_kernel.md`;
- limites epistemológicos explícitos;
- pivô cosmológico `a_h = sqrt(3)/2` como operador diagnóstico, não constante fundamental;
- `z_h = 2/sqrt(3)-1 ≈ 0.154700538379`;
- comparação `flat_lcdm` / `cpl` / `rll_rafaelia`;
- métricas `delta_chi2`, AIC/BIC, resíduos;
- falsificabilidade com dados reais (BAO/SNe/CMB).

O que **não** pertence ao RLL:

- execução de kernel Android ARM32/ARM64;
- branchless/no-heap freestanding em hot-path de produção;
- saturação e rollback de sinal em tempo real.

### Vectras (repositório externo)

Responsável por:

- execução runtime Android/ARM;
- Q16.16 `H_Q16 = 56756` freestanding;
- branchless/no-heap/freestanding ARM32/ARM64;
- filtros e projeções em hot-path;
- saturação, rollback, overflow e testes de sequência monotônica.

O que **não** pertence ao Vectras:

- afirmações cosmológicas com dados;
- cálculo de chi-quadrado, AIC, BIC sobre dados de survey;
- pivô `a_h` como constante cosmológica universal.

## Matriz de compatibilidade

| Elemento | Fica em RLL | Fica em Vectras | Observação |
|---|:---:|:---:|---|
| `h=sqrt(3)/2` | sim | sim | constante comum |
| prova geométrica | sim | referência | RLL documenta |
| Q16.16 | referência | sim | Vectras executa |
| cosmology pivot | sim | não, só link | evitar acoplamento indevido |
| testes de dados reais | sim | não | BAO/SNe/CMB/RLL |
| branchless/no heap | não | sim | runtime Android |
| rollback/saturação | referência | sim | hot-path |
| `delta_chi2` | sim | não | validação científica |

## Guardas epistemológicas

As guardas a seguir são **obrigatórias** em qualquer PR que mencione `sqrt(3)/2` como
invariante em fricção entre os dois repositórios:

1. **Operador, não constante universal:** `sqrt(3)/2` é uma constante de engenharia e
   geometria. Não é constante cosmológica fundamental. Qualquer uso cosmológico deve ser
   rotulado como pivô diagnóstico (`TOKEN_VAZIO` até comparação reprodutível com dados).

2. **Pivô, não afirmação:** `a_h = sqrt(3)/2` e `z_h ≈ 0.1547` são candidatos para
   comparação de modelos. Um resultado `Delta_chi2 > 0` melhora o modelo no conjunto
   testado; não transforma `sqrt(3)/2` em descoberta física.

3. **Filtro, não prova:** o uso em filtro recursivo, malha hexagonal ou hot-path runtime
   é heurística de engenharia documentada, não derivação física.

4. **Separação de camadas:** mudanças no Vectras que removem material cosmológico/pivô são
   corretas se o mesmo material (testes incluídos) for mantido ou migrado para o RLL.
   Remoção sem migração é regressão.

5. **Teste antes de merge:** nenhum PR que remova testes pode ser mergeado sem um PR
   substituto que implante os mesmos contratos em outro nível.

## Fricções conhecidas e status

| Fricção | Status | Ação requerida |
|---|---|---|
| PR Vectras #1032 remove material cosmológico | CLAIM_BLOCKED / startup_failure | Verificar se testes migram para RLL antes de merge |
| RLL #426 `Real Data Contract CI` falhou | CLAIM_BLOCKED | Investigar falha de CI; ver `docs/HOTFIX_REAL_VALIDATION_DATA_CONTRACT_2026-05-22.md` |
| Pivô cosmológico sem repositório-dono definido | HYPOTHESIS | Definição: RLL documenta, Vectras referencia sem cosmologia |
| Referência cruzada RLL ↔ Vectras ausente | TOKEN_VAZIO → VERIFIED_LIMITED | Ver `docs/audits/CROSS_REPO_RELATIONSHIP_REGISTRY.md` |

## Decisão: onde fica o cosmology_pivot

O pivô cosmológico **fica no RLL** como diagnóstico, com os seguintes artefatos:

- Documentação: `docs/invariants/sqrt3_2_kernel.md` seção "Extensão cosmológica"
- Implementação de referência: `core/lowlevel_runtime/c/pantheon_freestanding.c`
  — função `rll_sqrt3_2_cosmo_pivot_q16()` exportada como diagnóstico, não como API de
  produção cosmológica
- Testes: `tests/test_sqrt3_2_freestanding_kernel.py` — `test_cosmology_pivot_q16_matches_h_redshift_definition`

O Vectras pode usar a constante `H_Q16 = 56756` e o par `(a_h, z_h)` como referência
numérica, mas **não deve conter afirmações cosmológicas**. O link de referência cruzada
deve apontar para este documento e para `docs/invariants/sqrt3_2_kernel.md`.

## Critérios de decisão para PRs

- Se a mudança melhora documentação mas remove teste: **regressão** — bloquear.
- Se a mudança separa responsabilidades e adiciona referência cruzada: **refactor válido** — aprovar.
- Se a mudança declara cosmologia sem dado reprodutível: **bloquear**.
- Se a mudança executa kernel sem saturação/escala declarada: **bloquear**.
- Se a mudança remove testes sem PR substituto identificado: **bloquear**.

## Checklist de saída (issue #427)

- [ ] Real Data Contract CI no RLL explicado — ver `docs/HOTFIX_REAL_VALIDATION_DATA_CONTRACT_2026-05-22.md`
- [ ] startup_failure no Vectras documentado neste arquivo como CLAIM_BLOCKED
- [x] Decisão cosmology_pivot registrada: fica no RLL, Vectras referencia
- [x] Referência cruzada RLL ↔ Vectras adicionada em `docs/audits/CROSS_REPO_RELATIONSHIP_REGISTRY.md`
- [x] Guardas epistemológicas registradas neste documento
- [x] Critérios de decisão para PRs documentados

## Referências cruzadas

- `docs/invariants/sqrt3_2_kernel.md` — kernel técnico freestanding, extensão cosmológica
- `docs/audits/CROSS_REPO_RELATIONSHIP_REGISTRY.md` — registry RLL ↔ Vectras
- `docs/HOTFIX_REAL_VALIDATION_DATA_CONTRACT_2026-05-22.md` — hotfix CI real data
- `core/lowlevel_runtime/include/pantheon_freestanding.h` — API Q16.16
- `core/lowlevel_runtime/c/pantheon_freestanding.c` — implementação pivot
- `tests/test_sqrt3_2_freestanding_kernel.py` — testes freestanding
- `tests/test_sqrt3_2_kernel_contract.py` — contrato do kernel

## Retroalimentação

- **F_ok:** existe núcleo comum forte em `sqrt(3)/2`; documentado como invariante operacional.
- **F_gap:** integração RLL ↔ Vectras ainda não está documentada como arquitetura executável verificada.
- **F_next:** transformar esta matriz em referência estável e abrir PRs pequenos — um para ciência
  (RLL real data validation) e outro para runtime (Vectras kernel sem cosmologia).
