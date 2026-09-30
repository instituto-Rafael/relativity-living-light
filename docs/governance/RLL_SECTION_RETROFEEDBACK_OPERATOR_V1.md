# §Retroalimentação — operador mestre de evolução Ω³

**Estado:** executable governance contract  
**Claim allowed:** false  
**Data:** 2026-09-26

## Núcleo

```text
§Ω(Xn) = V(Xn, En, Δn, Gn, Pn, Rn, Fn, Tn) -> Xn+1
```

O operador não substitui os produtores de evidência existentes. Ele consome
Atlas, receipts, gap ledgers, workstreams e gates e registra uma transição
mínima auditável.

A extensão de qualidade é `DMAIC+R`, onde `R = Retroalimentação`.

## Regra de não regressão

Uma execução adversa pode ser evolução epistemológica:

```text
FAIL + uncertainty_reduced -> epistemic_evolution
```

mas isso nunca implica:

```text
FAIL -> PASS
FAIL -> scientific_claim
TOKEN_VAZIO -> 0
```

Promoção exige gate PASS, receipt presente, proveniência, falsificador não
violado, rollback pronto e ausência de regressão declarada de direitos e
auditabilidade. Mesmo assim, promoção científica depende de gate científico
separado.

## Unidade mínima do Atlas

Cada evento carrega:

`§ID §ANTES §INTENÇÃO §ENTRADA §EXECUÇÃO §OBSERVAÇÃO §RESULTADO §Δ
§INCERTEZA_ANTES §INCERTEZA_DEPOIS §FALSIFICADOR §TOKEN_VAZIO
§PROVENIÊNCIA §HASH §RECEIPT §GATE §BOUNDARY §ROLLBACK §URGÊNCIA
§F_NEXT §DEPOIS`

Campos complementares `§H §A §S §μ §Ω §∞` tornam explícitas
não-regressão humana, auditabilidade, zero trust, escrita mínima, posição no
Atlas e continuidade.

## Primeiro evento real

`SECTION-DELTA-WS01-20260926-001` preserva o FAIL observado no workflow
WS01. O teste unitário passou, mas a materialização falhou porque o executor
direto não via o pacote local `rx`.

Isso é classificado como evolução epistemológica limitada: a causa foi
localizada e corrigida, mas a promoção permanece bloqueada até um novo receipt
de execução.

## Validação

```bash
python3 tools/validate_rll_section_retrofeedback.py \
  --output artifacts/governance/RLL_SECTION_RETROFEEDBACK_RECEIPT.json
python3 -m unittest -v tests.test_rll_section_retrofeedback
```

## Boundary

Este operador é uma infraestrutura de governança e engenharia do projeto.
Não certifica física, ética, conformidade legal, segurança, Six Sigma ou
replicação independente.

## Delta WS01 — tolerância de integração

Após fechar o eixo H(z) por independência de probes, o próximo eixo numérico foi
pré-registrado em `data/contracts/rll_ws01_distance_integration_tolerance.v1.json`.
O limiar é congelado **antes da execução sucessora** (`rtol=1e-6`,
`atol=0.001 Mpc`) e será testado em 33 combinações modelo×redshift por três
comparações independentes/semindependentes. Falha preserva o TOKEN_VAZIO;
PASS autoriza somente congelar o método numérico, nunca uma claim física.
