# Topologia Observacional RLL — 2026-08-08 (V1)

## Decisão operacional

Esta topologia integra as lacunas de dados em um contrato append-only e fail-closed. Ela é um mapa de dependências, não uma certificação científica.

- Registro executável: [data/governance/RLL_OBSERVATIONAL_TOPOLOGY_20260808_V1.json](../../data/governance/RLL_OBSERVATIONAL_TOPOLOGY_20260808_V1.json)
- Schema: [schemas/rll_observational_topology.v1.schema.json](../../schemas/rll_observational_topology.v1.schema.json)
- Validador: [tools/validate_rll_observational_topology.py](../../tools/validate_rll_observational_topology.py)
- Testes: [tests/test_rll_observational_topology.py](../../tests/test_rll_observational_topology.py)

O estado global permanece:

~~~text
claim_allowed       = false
publication_ready   = false
default             = TOKEN_VAZIO
~~~

## Precedência de autoridade

1. O reconciliador moderno V2 descreve o estado efetivo e prevalece sobre interpretações de arquivos isolados.
2. A fila V4 e seus sucessores continuam a ser a fonte das contagens e dos tokens já existentes.
3. Esta V1 é apenas um overlay: tokens marcados topology_only não mudam denominadores, prioridade nem encerramento da fila existente.
4. Em conflito, a topologia preserva ambas as fontes e usa INVALIDATED até uma reprodução independente.

A aplicação direta desta regra encontra uma contradição no DESI DR2: um manifesto operacional declara a covariância joint como official_full, enquanto a auditoria canônica registra matriz em blocos/local, cross-block oficial não verificado e claim bloqueado. Por isso OBS-BAO-DESI-DR2 está INVALIDATED, não MATERIALIZED.

## Onde está a deficiência estrutural

~~~text
Fechamento de perturbações RLL
  -> contrato comum de likelihood
     -> vetores + covariâncias + nuisance + priors + backend + recibos
        -> reprodução de baseline
           -> comparação adversarial justa
              -> inferência conjunta (ainda bloqueada)
~~~

O gargalo primário não é somente baixar novas tabelas. Para CMB, fσ8, lenteamento, DES Y6 e Lyα full-shape, falta fechar e testar o setor linear RLL: delta_s, theta_s, c_s^2, pressão não adiabática, anisotropic stress, Q_mu, gauge, condições iniciais e regularização de crossing. Sem isso, um pipeline pode ler dados, mas não produz uma predição RLL que eles possam falsificar.

## Ramos separados

| Ramo | Estado de integração | Regra |
|---|---|---|
| Fundo: DESI BAO, Pantheon+, SH0ES, H(z) | Parcial; DESI joint está invalidado | Nunca reduzir covariância a diagonal nem chamar subconjunto de evidência conjunta |
| Estrutura: fσ8, DES Y6, DESI Lyα full-shape | Bloqueado por perturbações, covariância e nuisance | Exige fechamento físico e baseline reproduzido |
| CMB: Planck PR4/NPIPE, ACT DR6, SPT-3G D1, lensing | Baselines e likelihoods ainda incompletos | Distance priors não são TT/TE/EE completos |
| Comparação: GEDE, Anton-Schmidt, EFT/MG, plasma padrão | Sem paridade experimental formal | Mesmo vetor, prior, nuisance, cortes e backend |
| Propagação: FRB, RM, B-modes magneto-ópticos | Não materializado | Não entram no likelihood cosmológico sem previsão e seleção próprias |

Plasma padrão é mantido como classe de propagação para os ramos FRB/RM/B-modes; não é promovido automaticamente a adversário cosmológico.

## Estados

- MATERIALIZED e VERIFIED_LIMITED registram custódia ou execução limitada; não equivalem a claim.
- OPEN_INTERNAL e OPEN_EXTERNAL identificam trabalho local ou de custódia ainda pendente.
- BLOCKED_DEPENDENCY sinaliza dependência física ou de contrato ausente.
- INVALIDATED registra evidência conflitante que bloqueia promoção.
- TOKEN_VAZIO é o padrão para ausência ou ambiguidade.

Todos os nós nesta V1 têm ready_for_joint_inference = false.

## Execução

~~~bash
python3 -m tools.validate_rll_observational_topology \
  --output artifacts/governance/RLL_OBSERVATIONAL_TOPOLOGY_VALIDATION.json
python3 -m unittest -v tests.test_rll_observational_topology
~~~

A validação verifica o schema mínimo, a existência dos recibos locais citados, a ausência de ciclos, a presença dos nós obrigatórios, o bloqueio global de claim e a contradição DESI. Ela não substitui a reprodução estatística dos dados.

