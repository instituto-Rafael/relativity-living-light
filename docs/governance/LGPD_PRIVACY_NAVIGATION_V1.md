# LGPD, Privacidade e Navegação — Mapa de Conformidade Técnica V1

**Data:** 2026-09-29  
**Estado:** `ENGINEERING_MAP / LEGAL_COMPLIANCE_NOT_CLAIMED`  
**compliance_claim:** `false`

## 1. Escopo

Este documento compara controles existentes do repositório com obrigações e princípios relevantes da Lei 13.709/2018 (LGPD) e regulamentação da ANPD. Ele serve para engenharia, triagem e navegação.

Não é parecer jurídico, certificação nem declaração de conformidade integral.

Fontes oficiais consultadas:

- Lei 13.709/2018 — texto compilado: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm
- Regulamentações ANPD: https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd
- Materiais e guias ANPD: https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes

## 2. Regra central do repositório

```text
PUBLIC_NON_PERSONAL_* → rota normal governada
PERSONAL / PRIVATE / UNKNOWN → STOP + HUMAN_REVIEW + QUARANTINE
```

Essa fronteira já existe em `RLL_DATA_USE_PURPOSE_REGISTRY_V1.json`, no development guard e no runbook de incidentes.

## 3. Matriz LGPD → controle RLL

| Tema | Referência LGPD/ANPD | Controle existente | Estado técnico |
|---|---|---|---|
| Finalidade, adequação e necessidade | art. 6 | `RLL_DATA_USE_PURPOSE_REGISTRY_V1.json`; operação declara purpose/data classes | `IMPLEMENTED_GOVERNANCE` |
| Transparência / informação | arts. 9 e 18 | README, Navigation Hub, registries, receipts | `PARTIAL` |
| Direitos do titular | art. 18 | tratamento pessoal é bloqueado por padrão | `TOKEN_VAZIO_DATA_SUBJECT_CHANNEL_IF_PERSONAL_PROCESSING` |
| Registro de operações | art. 37 | purpose registry + receipts por rota | `PARTIAL_STRUCTURED` |
| Segurança desde a concepção | arts. 46 e 49 | deny-by-default, data-class gate, network/write limits, incident runbook | `IMPLEMENTED_TECHNICAL` |
| Incidente com dado pessoal | art. 48 + Res. ANPD 15/2024 | `RLL_INCIDENT_RESPONSE_V1.md` | `PARTIAL`; decisão/notificação legal exige responsável humano |
| Encarregado | art. 41 + Res. ANPD 18/2024 | nenhum papel jurídico é inferido do código | `TOKEN_VAZIO_ROLE_AND_APPLICABILITY` |
| Pequeno porte | Res. ANPD 2/2022 | não inferido automaticamente | `TOKEN_VAZIO_APPLICABILITY` |
| Transferência internacional | LGPD + Res. ANPD 19/2024 | repositório público usa infraestrutura externa; avaliação jurídica não fechada | `TOKEN_VAZIO_TRANSFER_ASSESSMENT` |
| Crianças/adolescentes | art. 14 | dado pessoal é proibido nas rotas científicas padrão | `FAIL_CLOSED`; qualquer nova rota exige revisão própria |
| Retenção | princípios + art. 16 | várias rotas declaram retention; não existe política única completa | `PARTIAL` |
| Prestação de contas | art. 6, X | hashes, receipts, provenance, claim boundaries | `IMPLEMENTED_TECHNICAL` |

## 4. Verificação do estado atual

### F_ok

- O runtime científico padrão declara dados públicos não pessoais.
- Dados pessoais/privados inesperados são bloqueados e enviados para revisão humana.
- O repositório possui registro de finalidade por rota.
- Há controles técnicos de rede, escrita, credenciais, logs e proveniência.
- Existe runbook específico para `IR-PRIVACY`.
- Há regra explícita `PRIVACY_BY_DESIGN != LEGAL_COMPLIANCE_CERTIFICATION`.

### F_gap

- papel jurídico controlador/operador ainda não está determinado por este repositório;
- aplicabilidade de encarregado/dispensa não está determinada;
- canal de exercício de direitos só é necessário/definível se houver tratamento pessoal autorizado;
- transferência internacional precisa avaliação contextual;
- retenção ainda não tem uma política única para todas as superfícies;
- revisão jurídica independente continua `TOKEN_VAZIO`;
- varredura técnica nunca prova ausência total de dados pessoais.

## 5. Política para arquivos soltos

Antes de mover um arquivo:

1. classificar `CANONICAL | ACTIVE | LEGACY | INGESTION | ARTIFACT`;
2. classificar dados `PUBLIC_NON_PERSONAL | PERSONAL | PRIVATE | UNKNOWN`;
3. verificar backlinks;
4. preservar proveniência/hash quando aplicável;
5. se `PERSONAL`, `PRIVATE` ou `UNKNOWN`: não promover nem publicar automaticamente;
6. só então migrar caminho e manter stub/redirect documental quando necessário.

## 6. Conforto de navegação também é privacidade

Uma árvore compreensível reduz tratamento acidental: o usuário consegue distinguir dados públicos, resultados, legacy, receipts, segurança e ingestão antes de abrir ou executar algo.

Por isso o fluxo canônico passa a ser:

```text
README → docs/navigation/README.md
       → INDICE_MESTRE
       → índice especializado
       → arquivo
```

## 7. Não-claims

```text
TECHNICAL_PRIVACY_GATE != LGPD_CERTIFICATION
NO_SEARCH_HIT != NO_PERSONAL_DATA
PUBLIC_REPOSITORY != LEGAL_BASIS_FOR_ANY_PERSONAL_DATA
ANONYMIZED_CLAIM != PROVEN_ANONYMIZATION
TOKEN_VAZIO != COMPLIANT
```
