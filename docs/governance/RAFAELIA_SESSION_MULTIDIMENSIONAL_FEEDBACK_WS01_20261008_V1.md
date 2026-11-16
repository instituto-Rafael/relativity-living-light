# RAFAELIA — retroalimentação multidimensional, métodos e falsificadores WS01 (V1)

**Estado:** `EVIDENCE_BOUNDED / SOURCE_SNAPSHOT / HOLD`  
**Data do snapshot:** 2026-10-08  
**claim_allowed:** `false`  
**Domínio produtor:** RLL, observação científica e engenharia de gates.  
**Alvo observado:** [PR #1076](https://github.com/instituto-Rafael/relativity-living-light/pull/1076) no HEAD exato `67140f891a7cfabd929f010e0a3940fda50ceaaa`.  
**Base desta nota:** `rll/lab@5b641510afd62abab5a98ad17019d361d621478c`; nota documental *não* executa/transplanta o código do PR observado.

## 0. Retroalimentação antes de agir — contrato de sessão

A sequência obrigatória para um novo problema é:
`INTENT → CURRENT_STATE → μREAD(source mínimo) → formalismo → falsificador pré-declarado → execução → evidência → μWRITE → R3`.

1. Ler fonte atual e histórico apenas se houver contradição, falta de proveniência ou lacuna de autoridade.
2. Distinguir `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`; `TOKEN_VAZIO != 0`; `IMPLEMENTED_UNTESTED != PASS`.
3. Para cada família Π e variação Δ, registrar uma unidade μ com referência imutável, estado anterior/posterior, hipótese, método, falsificador, sinal de decisão, risco P0, rollback e `F_next`.
4. `‰` designa *taxa descritiva por mil* apenas quando numerador, denominador e população estão evidenciados. `‡` é o gate de prova; `†` é o falsificador/impedimento; `★` é a prioridade (P0/P1/P2). Nenhum símbolo promove um PASS.
5. Usar append-only e successor, não sobrescrever evidência negativa. Uma falha que esclarece a causa reduz incerteza sem virar sucesso.

### Mudança da sessão, antes/depois

- **RafPolimata #426:** anteriormente `OPEN` no índice, observado agora como `MERGED` no HEAD `4cb7c305d26dd0decba244901981c3cf87864f90`; cinco workflows associados a esse commit: `SUCCESS` observados. Não se infere receipt Android.
- **RLL #1076:** anteriormente indexado em `8647a5df...`, observado no HEAD `67140f89...` como `OPEN`. Na primeira página de runs para o commit: 22 concluídos, 17 `SUCCESS`, 5 `FAILURE`. Taxa descritiva observada 17/22 = **772,73‰** e 5/22 = **227,27‰**; a população é somente o conjunto retornado, não todos os requisitos de validação.
- **Drive:** a reconstrução prévia guardou sete observações em `MuDelta_Attention` e 13 microregistros Π/Δ/μ/‰/‡/†/★ em `START HERE μWRITE LEDGER Ω V2`. Uma tentativa posterior de expandir a planilha e o HOTSTATE foi bloqueada pela ferramenta; não foi considerada gravação.
- A presente nota é um *sucessor documental*. Não corrige falhas numéricas, jurídicas ou de provedor.

## 1. Fórmula, domínio, método e comparação WS01

O contrato versionado no HEAD do PR é
[`data/contracts/rll_ws01_distance_integration_tolerance.v1.json`](https://github.com/instituto-Rafael/relativity-living-light/blob/67140f891a7cfabd929f010e0a3940fda50ceaaa/data/contracts/rll_ws01_distance_integration_tolerance.v1.json).
O executor do mesmo HEAD é [`tools/rll_ws01_distance_integration_tolerance.py`](https://github.com/instituto-Rafael/relativity-living-light/blob/67140f891a7cfabd929f010e0a3940fda50ceaaa/tools/rll_ws01_distance_integration_tolerance.py).

A distância comóvel de fundo é definida, dentro da convenção do executor, por:

\[
D_C(z) = \frac{c}{H_0}\int_0^z \frac{dz'}{E(z')},\qquad
E(z)=\sqrt{\mathrm{e2}(\mathrm{modelo},z,\mathrm{parâmetros})}.
\]

Na variável \(\xi=\ln(1+z)\), a integral numérica torna-se:

\[
D_C(z)=\frac{c}{H_0}\int_0^{\ln(1+z)}
\frac{\exp(\xi)}{E(\exp(\xi)-1)}\,d\xi.
\]

São duas representações da mesma integral na hipótese de domínio numérico válido. Concordância entre implementações testa consistência numérica, não explica a física de `E(z)`, nem valida os parâmetros do modelo.

**Protocolos congelados na fonte (não alterar para obter verde):**

- 3 instâncias: `LCDM`, `RLL_NULL`, `RLL_PROBE`.
- 11 redshifts: `0.01,0.1,0.3,0.5,1,1.5,2,3,5,10,1100`; total de 33 linhas.
- Simpson em \(\ln(1+z)\) com passos grosseiros `1024` e finos `4096`; Simpson direto em \(z\) com `4096`; referência trapezoidal na variável log com `16384`.
- Testes: `fine_vs_trapezoid_reference`, `fine_vs_direct_z_simpson`, `coarse_vs_fine`.
- Critério conjunto *pré-registrado* por par:

\[
|D_{\rm candidato}-D_{\rm referência}|
\le 0{,}001\,\mathrm{Mpc}+10^{-6}|D_{\rm referência}|.
\]

**Falsificador † WS01:** FAIL se ao menos um dos 33 × 3 confrontos violar o limite conjunto. O run `37845205220`, job `113544244444`, reportou `FAIL_PREREGISTERED_DISTANCE_TOLERANCE`, máximo relativo `fine_vs_direct=1.530850273969348e-05` e exit code `2`. O número relativo máximo sozinho não substitui a checagem com tolerância absoluta; a decisão FAIL provém do avaliador do contrato no log.

Comandos **para reprodução futura no checkout exato do HEAD do PR**, não executados por esta nota:

```bash
python3 -m unittest -v tests.test_rll_ws01_distance_integration_tolerance
python3 tools/rll_ws01_distance_integration_tolerance.py --write
```

Um unit-test PASS verifica invariantes do contrato e formato do resultado; o segundo comando pode sair com código `2` para preservar evidência negativa. Não é permissão para reduzir `rtol`, elevar `atol` ou mudar a grade *depois* do resultado. A base `rll/lab` desta nota não contém necessariamente o executor: usar o commit exato acima, e não supor presença por nome de arquivo.

## 2. Cinco gates falhos do HEAD observado — causas distintas

| ‡ Gate | Run / job | † Evidência de bloqueio | Estado |
|---|---|---|---|
| Branch Maturity V2 | 37845205864 / 113544247812 | `INVALID_BRANCH_TRANSITION` no caminho de promoção até `main` | `BLOCKED_TOPOLOGY` |
| RLL Governance Quality | 37845205220 / 113544244444 | WS01 com tolerância pré-registrada violada | `SOURCE_SIDE_NUMERIC_FAIL` |
| Six Sigma Real Data Controls | 37845204939 / 113544244136 | `docs_inventory.py` gerou diferenças rastreáveis e `git diff --exit-code` falhou | `GENERATED_INVENTORY_DRIFT` |
| GitHub Platform Assurance V2 | 37845204702 / 113544528817 | `protection_detail_complete=false`, `resolution_eligible=false` | `PROVIDER_AUTHORITY_PARTIAL` |
| Transit Tower Ω | 37845204789 / 113544244161 | `GOVERNANCE_CONTRACT_TOUCH_REQUIRED`; revisão da maturidade/contrato | `PROMOTION_BLOCKED` |

No mesmo commit, `Python tests` run `37845204668` foi `SUCCESS`. Um PASS em Python não anula os cinco FAIL. Há 1 thread de revisão não resolvida observada no PR. Não alterar o código de WS01 sem reproduzir o falsificador e identificar mudança mínima causal; não modificar configurações externas sem autoridade e readback.

## 3. Ordem de investigação com alto valor de informação

1. **★ P0 / WS01:** identificar quais pares modelo×z e quais métricas absolutas disparam †; produzir tabela de diferenças com referência de linha e comparar implementações, sem alterar o contrato.
2. **★ P0 / Direitos:** há divergência de `LICENSE.md` entre `rll/lab@5b641510...` e `main/PR#1076`. A licença de documentação autoral em `main` aponta `CC BY-SA 4.0`; o manifesto em `rll/lab` apresenta outra formulação. Nenhum texto de terceiro foi transcrito nesta nota. Compatibilidade, titularidade e promoção de licença ficam `TOKEN_VAZIO / HUMAN_REVIEW_REQUIRED`. Não reescrever licenças por inferência.
3. **★ P1 / Inventário:** comparar apenas arquivos gerados pelo script e origem rastreada, preservando as fontes e evitando rebuild global.
4. **★ P1 / Topologia/contrato:** não promover uma work branch diretamente para `main`; validar cada salto `work→lab→integration→release→main` separadamente e sem merge cego.
5. **★ P0 / Provedor:** obter prova autorizada de settings/rulesets/protection, sem concluir `disabled` a partir de erro de leitura.
6. **★ P1 / Revisão:** tratar thread pendente antes de qualquer proposta de promoção.
7. **★ P0 / Ciência:** reprodução independente, verossimilhança/covariância e testes retidos são exigências separadas; nenhum run CI sozinho certifica cosmologia.

## 4. Semântica tipada das lacunas

- `NUMERIC_ZERO` é resultado medido zero; `TOKEN_VAZIO` significa evidência requerida ainda ausente; `MISSING_OBSERVATION` significa observação não obtida; `NOT_APPLICABLE` significa que a métrica não cabe à família; `UNDEFINED` denota expressão/variável indefinida. Não usar uma dessas como sinônimo da outra.
- `‰` só pode ser calculado quando `n/N` e janela de observação são conhecidos. Taxa CI descritiva não é chance de correção, maturidade ou qualidade científica.
- Fórmula candidata ≠ fórmula demonstrada ≠ método aplicado ≠ teste reproduzido ≠ resultado científico.
- `claim_allowed=false` é obrigatório neste estágio; nenhuma decisão de publicação, merge ou mérito cosmológico é autorizada.

## 5. Custódia e retroalimentação

**Produtor:** RLL governa o contrato, o executor e os resultados WS01.  
**Papers:** é camada de síntese de métodos/proveniência e *não* transfere prova; o índice formal de matemática pode residir em `Matem-tica-`.  
**Drive:** ledger e HOTSTATE são memória documental, não execução.

`μID | source/ref exata | Δ | Π | fórmula/método | ‡ gate | † falsificador | execução | receipt | TOKEN_VAZIO | ★ | F_next | rollback`.

### R3

- `F_ok`: critérios WS01 e HEAD readbacks localizados; causalidade de cinco gates individualizada; negativa preservada; 17/22 sucessos delimitados.
- `F_gap`: WS01, cinco workflows falhos, proveniência de licença por branch, review, provider enforcement, execução física e replicação independente.
- `F_next`: reproduzir † WS01 com granularidade modelo×z, classificar a diferença, corrigir *somente* falsificador source-side demonstrado e reexecutar o gate dedicado no HEAD seguinte.
- `rollback`: fechar/reverter exclusivamente esta branch documental; não alterar snapshots do PR, arquivos originais, contratos ou limiares.

**Publicação, certificação e promoção:** `claim_allowed=false`.