# RLL Operational Governance — implementação executável, sem certificação

## 1. Declaração de fronteira

Este módulo transforma princípios de engenharia, qualidade, governança de dados, segurança e pesquisa em **contratos verificáveis no repositório**. Ele não certifica o RLL, não declara conformidade ISO/IEEE/NIST/OMS, não produz parecer jurídico e não substitui comitê de ética, biossegurança, licenciamento ambiental, responsabilidade profissional ou organismo acreditado.

A expressão **auditoria absoluta** é usada no sentido operacional de cobertura honesta: declarar o que foi observado, medido, não observado, inferido, evidenciado, alterado e deixado aberto. Não significa prova de ausência de falhas.

## 2. Artefatos executáveis

| Artefato | Função |
|---|---|
| `governance/rll-governance-profile.v1.json` | Perfil versionado das seis camadas, referências e limites de alegação |
| `governance/rll-module-contract.schema.json` | Forma mínima de um módulo governado |
| `governance/modules/*.json` | Contratos concretos por domínio |
| `scripts/rll_governance_audit.py` | Validador sem dependências externas e gerador de receipt |
| `tests/test_rll_governance_audit.py` | Testes de promoção de claims, default-deny biomédico e determinismo |
| `.github/workflows/rll-governance-quality-gate.yml` | Gate GitHub Actions com permissão somente leitura |
| `.github/PULL_REQUEST_TEMPLATE.md` | Contrato humano para objetivo, evidência, risco, métrica, aceite, rejeição e rollback |

## 3. Réguas normativas usadas como inspiração

### 3.1 Engenharia e V&V

- IEEE 1012: verificação e validação de sistemas, software e hardware.
- ISO/IEC/IEEE 29148: requisitos e rastreabilidade.
- Família IEEE 730: garantia de qualidade de software.
- IETF BCP 14: vocabulário inequívoco de requisitos (`MUST`, `SHOULD`, `MAY`) quando adotado formalmente.
- W3C PROV-O: representação de proveniência.

### 3.2 Qualidade e evolução

- ISO 9001 como referência de sistema de gestão da qualidade.
- Six Sigma DMAIC para definir, medir, analisar, melhorar e controlar.
- Lean para reduzir espera, retrabalho, duplicação e processamento sem ganho.

O gate não confunde `PASS` com excelência. Um `PASS` significa apenas que o contrato local foi satisfeito na revisão declarada.

### 3.3 Dados

A família ISO 8000, FAIR e W3C PROV inspiram os campos mínimos:

`origem → licença → hash → versão → tempo → unidade → incerteza → proveniência → atualização`

FAIR não é sinônimo de dado aberto, qualidade perfeita, legalidade ou ética. O acesso pode ser restrito e ainda assim possuir metadados e governança adequados.

### 3.4 Segurança

O perfil usa princípios da ISO/IEC 27001/27002, NIST CSF, NIST SSDF, OWASP e GitHub Actions:

- menor privilégio;
- `contents: read` por padrão;
- ausência de segredos no gate;
- actions externas fixadas por SHA completo;
- `persist-credentials: false`;
- entradas, hashes e receipts validados;
- registro de incidente e cadeia de custódia;
- `pull_request_target` proibido por padrão.

A auditoria de workflows é progressiva: o workflow novo é bloqueado se usar referência mutável; referências legadas são registradas como `F_gap` até baseline e correção controlada.

### 3.5 Pesquisa científica

Toda promoção segue:

`hipótese → experimento → dataset → código → receipt → resultado → conclusão`

`claim_allowed=true` exige estado epistemológico compatível e evidência reproduzível. Beleza, repetição, parábola, analogia ou coerência interna não promovem claim.

### 3.6 Biomedicina, biologia, bioquímica, fauna, flora, ecossistemas e engenharia

O contrato multidisciplinar é **default-deny** para dados pessoais e dados sensíveis de saúde, genética ou biometria. Ele exige revisão específica antes de pesquisa com participantes humanos, animais, agentes biológicos, intervenção ambiental ou uso de resultado em engenharia crítica.

O módulo não autoriza:

- diagnóstico ou tratamento;
- recomendação clínica;
- identificação de pessoa por dado genético/biométrico;
- divulgação de localização sensível de espécie ameaçada;
- intervenção ambiental;
- liberação de sistema de segurança crítica;
- substituição de profissional responsável.

## 4. Contrato de um módulo

Cada módulo declara, no mínimo:

1. estado e escopo;
2. camada epistemológica;
3. `claim_allowed` e `certification_claim`;
4. receipts, testes, fontes e limitações;
5. classificação e governança dos dados;
6. segurança e tratamento de incidente;
7. métricas, aceite, rejeição e mudança controlada;
8. riscos e risco residual;
9. rollback verificável;
10. `F_ok`, `F_gap` e `F_next`.

## 5. Saída da auditoria

O script gera:

- `artifacts/governance/rll_governance_receipt.json`;
- `artifacts/governance/RLL_GOVERNANCE_REPORT.md`.

O receipt contém a revisão avaliada, hashes dos contratos, contagens, violações, avisos, estados dos módulos e fechamento Ω. O tempo local padrão permanece `TOKEN_VAZIO_DETERMINISTIC_TIME`; em CI, a revisão vem de `GITHUB_SHA`. Assim, o hash é reprodutível e não depende do relógio para parecer novo.

## 6. Execução local

```bash
python3 scripts/rll_governance_audit.py --strict --write-report
python3 -m unittest -v tests/test_rll_governance_audit.py
```

Nenhuma biblioteca Python externa é necessária.

## 7. Estratégia de implantação

### Ciclo 1 — Fundação

- perfil de governança;
- schema;
- módulos climático e multidisciplinar;
- gate e template de PR.

### Ciclo 2 — Baseline do território

- inventariar actions mutáveis, permissões, segredos e workflows de escrita;
- registrar exceções legadas por arquivo, risco e responsável;
- não quebrar o repositório por uma varredura cega.

### Ciclo 3 — Redução de risco

- fixar actions externas por SHA;
- reduzir permissões;
- separar workflows de leitura e escrita;
- proteger dados sensíveis e artefatos;
- sincronizar receipts com a árvore final.

### Ciclo 4 — Validação por domínio

- escolher datasets públicos e não pessoais;
- declarar unidade, incerteza, escala e mecanismo;
- comparar baseline e alternativa com igual orçamento;
- promover claims somente após evidência reprodutível e revisão adequada.

## 8. Parábola operacional

A biblioteca excelente não afirma que todos os livros são verdadeiros. Ela preserva origem, edição, autor, revisão, dependência, lacuna e histórico. O gate faz o mesmo com cada módulo: **não substitui o pesquisador, o engenheiro, o jurista ou o comitê; impede que a estante esconda de onde veio cada afirmação.**

## 9. Fechamento Ω

- **F_ok:** governança executável, auditável, determinística e sem dependência externa.
- **F_gap:** configurações externas do GitHub, aplicabilidade jurídica, aprovações éticas e validação de domínio não podem ser provadas apenas pelo código.
- **F_next:** executar o gate, registrar o baseline legado e corrigir por risco sem promover certificação ou ciência não demonstrada.
