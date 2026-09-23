# RLL — Incident Response Runbook V1

**Estado:** ACTIVE_GOVERNED_DRAFT  
**Escopo:** execução local, Termux, CI, dados, credenciais, privacidade e integridade do repositório  
**Princípio:** conter primeiro; preservar evidência não sensível; não ampliar exposição.

## 1. Classificação mínima

| Código | Evento | Primeira ação |
|---|---|---|
| IR-SECRET | segredo/token/credencial exposto | parar e revogar/rotacionar no provedor |
| IR-PRIVACY | dado pessoal/privado inesperado | parar e quarentenar localmente |
| IR-POLICY | execução fora do envelope | bloquear execução e preservar receipt |
| IR-INTEGRITY | fonte/hash/artefato alterado inesperadamente | bloquear promoção e comparar proveniência |
| IR-NETWORK | destino/redirect/rede não autorizada | encerrar requisição e bloquear operação |
| IR-WRITE | escrita fora da superfície permitida | parar, identificar mutação e avaliar rollback |
| IR-SUPPLY | dependência/artefato externo inesperado | isolar rota e não promover resultado |
| IR-CLAIM | runtime promove conclusão indevida | bloquear publicação/claim e corrigir append-only |

## 2. Regra STOP

STOP EXECUTION → não ampliar investigação com credenciais/dados reais → preservar logs não sensíveis e hashes → classificar → conter → rollback se houve mutação → registrar incident receipt → corrigir por novo commit → revalidar gates.

## 3. Segredo ou token

Não colocar o valor em issue, commit, chat operacional, receipt ou hash.

1. parar o processo;
2. impedir novo commit/publicação;
3. revogar ou rotacionar a credencial no sistema que a emitiu;
4. identificar somente nome lógico/superfície, sem valor;
5. remover exposição pública quando aplicável, preservando cadeia de auditoria separada;
6. registrar causa, janela temporal conhecida e artefatos afetados;
7. reexecutar gates sem o segredo;
8. marcar validade anterior como potencialmente comprometida quando necessário.

## 4. Dado pessoal ou privado inesperado

1. parar ingestão;
2. não commitar;
3. manter somente em quarentena local com acesso mínimo enquanto a decisão é tomada;
4. registrar a classe detectada sem reproduzir o conteúdo;
5. confirmar autorização, finalidade e necessidade;
6. se não houver base/necessidade declarada, descartar pela superfície autorizada;
7. se houver uso legítimo futuro, criar operação separada com revisão humana antes de qualquer processamento.

## 5. Política/bypass

Se código executar capability não declarada: resultado = POLICY_VIOLATION; execução não herda PASS anterior; claim continua false; a mudança deve ser revertida ou receber nova operação/política revisada. Não relaxar a allowlist apenas para o teste passar.

## 6. Rede

Destino não allowlisted, porta customizada, query inesperada, userinfo ou redirect cross-host: BLOCK.

Não seguir o destino para 'ver o que acontece'. Registrar apenas URL sanitizada/hostname quando não contiver informação sensível.

## 7. Integridade científica

SOURCE_CHANGED != MODEL_FAILED != SECURITY_INCIDENT.

Primeiro identificar se a mudança é legítima/versionada. Não reutilizar automaticamente resultados anteriores contra um input novo.

## 8. Escrita inesperada

1. parar;
2. listar arquivos afetados;
3. não apagar logs necessários à auditoria;
4. usar Git/backup para comparar estado anterior;
5. rollback apenas da mutação atribuível ao evento;
6. registrar o commit/receipt de correção.

## 9. Reporte de vulnerabilidade

Seguir `.github/SECURITY.md`.

Issue pública deve conter somente resumo não sensível. Não publicar exploit funcional, credencial, dado privado ou instrução operacional que aumente risco.

## 10. Fechamento

Incidente só fecha quando existem: classificação + contenção + causa conhecida ou TOKEN_VAZIO + escopo afetado + correção + teste + rollback/status + receipt + gaps residuais.

## 11. Não-claims

Este runbook é governança interna. Não constitui certificação ISO/NIST/LGPD/GDPR, parecer jurídico ou garantia de ausência de vulnerabilidades.
