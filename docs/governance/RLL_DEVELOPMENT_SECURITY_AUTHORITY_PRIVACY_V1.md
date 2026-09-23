# RLL — Segurança, Autoridade, Privacidade e Auditoria de Desenvolvimento V1

**Estado:** ACTIVE_GOVERNANCE_CONTRACT  
**Modo:** desenvolvimento permitido / autoridade fail-closed  
**claim_allowed:** false

## 1. Regra principal

O RLL é software em desenvolvimento. Desenvolvimento pode avançar, testar, calcular, refatorar e produzir artefatos. Isso não concede ao programa autoridade autônoma sobre pessoas, contas, credenciais, infraestrutura ou dados sensíveis.

```text
CAPACIDADE != PERMISSAO
EXECUCAO != AUTORIDADE
ACESSO != PROPRIEDADE
AUTOMACAO != AUTONOMIA DE GOVERNANCA
```

A pergunta antes de qualquer efeito é:

```text
quem -> para qual finalidade -> sobre quais dados -> com qual autoridade
    -> em qual escopo -> por quanto tempo -> com qual registro -> com qual rollback
```

## 2. Envelope obrigatório de execução

Toda mecânica com efeito material deve poder declarar:

- **actor** — pessoa/processo que iniciou;
- **purpose** — finalidade específica;
- **authority_level** — A0..A5;
- **data_classes** — D0..D4;
- **inputs/outputs** — o que entra e sai;
- **network_mode** — desligada, leitura ou escrita;
- **write_scope** — destinos permitidos;
- **secrets_required** — nomes das credenciais, nunca valores;
- **retention** — quanto tempo os dados/artefatos permanecem;
- **audit_receipt** — onde fica a evidência;
- **rollback** — como desfazer;
- **expiry** — quando a autorização deixa de valer.

Campo necessário desconhecido = `TOKEN_VAZIO`; para autoridade elevada isso bloqueia a execução.

## 3. Níveis de autoridade

| nível | significado | regra |
|---|---|---|
| A0 | cálculo puro | permitido dentro do runtime |
| A1 | escrita no workspace | somente escopo de projeto autorizado |
| A2 | leitura externa | fonte e classe de dado declaradas |
| A3 | escrita externa | autorização humana |
| A4 | sensível/privilegiado | autorização humana + revisão adicional |
| A5 | destrutivo/irreversível | DENY por padrão |

Nenhum módulo pode aumentar seu próprio nível.

## 4. Classes de dados

| classe | exemplo | padrão |
|---|---|---|
| D0 | dados públicos | ALLOW |
| D1 | artefato interno do projeto | ALLOW + provenance |
| D2 | confidencial | REVIEW |
| D3 | dado pessoal | DENY salvo finalidade/autoridade explícita |
| D4 | dado pessoal sensível, segredo, credencial | DENY por padrão |

Receipts devem preferir hash, ID e decisão. Não devem copiar segredo nem conteúdo pessoal desnecessário.

## 5. Fronteira de segurança

O desenvolvimento deve parar antes do efeito quando houver:

1. ator/finalidade desconhecidos;
2. autoridade necessária não declarada;
3. dado não classificado;
4. segredo prestes a entrar em código, log ou receipt;
5. escrita fora do escopo;
6. destino de rede não autorizado;
7. entrada não confiável tentando introduzir código/comando;
8. tentativa de desligar auditoria ou reduzir controles;
9. ação destrutiva sem autorização e rollback;
10. `TOKEN_VAZIO` em condição obrigatória de segurança.

## 6. Separação de planos

```text
DATA PLANE
dados científicos e artefatos

COMPUTE PLANE
Rx / C / Q16 / Structure-D

CONTROL PLANE
jobs, parâmetros, rotas, limites

AUTHORITY PLANE
quem pode autorizar qual efeito

AUDIT PLANE
receipts, hashes, eventos, incidentes

CLAIM PLANE
o que a evidência permite afirmar
```

O Compute Plane não pode conceder autoridade ao próprio Control Plane.

## 7. Segurança por construção

Para cada componente:

```text
INPUT
 -> classify
 -> validate
 -> constrain
 -> compute
 -> validate output
 -> write only declared target
 -> receipt
```

Controles mínimos:

- validação de tamanho, tipo, unidade e faixa;
- caminhos normalizados e limitados ao workspace;
- nenhuma execução de texto recebido como código;
- rede desligada por padrão em gates determinísticos;
- credenciais mínimas e de curta autoridade;
- permissões de workflow mínimas;
- ações externas imutavelmente pinadas quando aplicável;
- artefatos com hash;
- outputs sem dados sensíveis;
- rollback antes de mutação importante.

## 8. Exploits e vulnerabilidades

O projeto pode **detectar, classificar, testar defensivamente e corrigir** vulnerabilidades dentro de ativos autorizados.

A existência de um bug não concede autorização para explorar terceiros.

Fluxo:

```text
finding
 -> reproduce in authorized/sandbox scope
 -> severity/context
 -> evidence
 -> containment
 -> patch
 -> regression test
 -> receipt
 -> disclosure/communication only through authorized route
```

PoC deve usar fixture/sandbox quando isso for suficiente. Credenciais, dados reais sensíveis ou alvos externos não entram por conveniência.

## 9. Privacidade

A privacidade não é apenas esconder nome.

Aplicar:

```text
finalidade
 -> minimizacao
 -> necessidade
 -> acesso
 -> retencao
 -> auditoria
 -> descarte/supersessao
```

Rastreamento padrão é **operacional**, não comportamental: registrar execução, origem, alteração, erro e autoridade necessários para segurança/reprodução. Não construir perfil de pessoa por padrão.

## 10. Incidente

Estados:

```text
SUSPECTED
 -> CONTAINED
 -> EVIDENCE_PRESERVED
 -> ASSESSED
 -> REMEDIATED
 -> CLOSED
```

Primeiro: interromper efeitos, preservar evidência e limitar acesso. Rotação/revogação de credenciais pertence ao responsável autorizado. Correção silenciosa sem receipt é proibida.

## 11. Relação com a governança já existente

Este contrato complementa:

- `governance/rll-governance-profile.v1.json`;
- `.github/workflow-contract.yml`;
- credential authority;
- operational gap ledger;
- receipts e `claim_allowed=false`.

O repositório já declara leitura por padrão para workflows de governança, minimização de segredos, ações imutáveis, cadeia de custódia e autorização humana para enforcement externo. Este documento organiza essas peças em uma única fronteira de desenvolvimento.

Uma lacuna importante já observada no contrato do repositório permanece: **branch protection/rulesets não estão aplicados/observados como proteção ativa**. Portanto governança documental não deve ser confundida com enforcement da plataforma.

## 12. Última peça que se sustenta

A menor arquitetura sustentável é:

```text
              HUMAN PURPOSE
                   |
                   v
             AUTHORITY GATE
                   |
        +----------+----------+
        |                     |
        v                     v
    DATA GATE             ACTION GATE
        |                     |
        +----------+----------+
                   |
                   v
              RLL PROGRAM
                   |
                   v
              EVIDENCE
                   |
                   v
               RECEIPT
                   |
                   v
            AUDIT / ROLLBACK
```

O programa pode avançar sozinho **dentro de uma autorização já delimitada**. Ao alcançar uma nova classe de autoridade, dado ou efeito, ele para e pede decisão humana.

Essa é a fronteira entre automação útil e autoridade indevida.

## 13. Gates de desenvolvimento

`G0 PURPOSE` — finalidade conhecida.  
`G1 SOURCE` — origem e licença/uso conhecidos.  
`G2 DATA` — classificação e minimização.  
`G3 COMPUTE` — execução determinística/limitada.  
`G4 SECURITY` — entrada, segredo, filesystem e rede controlados.  
`G5 AUTHORITY` — efeito permitido pelo nível atual.  
`G6 EVIDENCE` — resultado observável e hash/receipt.  
`G7 CLAIM` — afirmação não excede evidência.  
`G8 ROLLBACK` — retorno/revogação possíveis quando aplicável.

Todos os gates necessários devem passar para a ação correspondente; um gate não aplicável deve ser explicitamente `N/A`, não presumido.

## R3

**F_ok:** existe agora uma fronteira única entre desenvolvimento, autoridade, dados, segurança, privacidade, auditoria e claim.

**F_gap:** enforcement real de branch protection/rulesets permanece aberto; classificação automática de todas as rotas existentes ainda não foi executada; revisão jurídica/regulatória específica não é inferida por este contrato.

**F_next:** ligar este policy a um validador stdlib-only que receba um execution envelope e retorne ALLOW / REVIEW / DENY antes de rotas com efeitos.
