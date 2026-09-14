# RAFAELIA — Vocabulário Canônico

> Status: vocabulário operacional para reduzir ambiguidade entre metáfora, hipótese, prova, código, log e execução.

## Regra-mãe

```text
símbolo ≠ hipótese ≠ prova ≠ código ≠ log ≠ execução
```

## Termos centrais

| Termo | Classe | Definição operacional | Estado inicial |
|---|---|---|---|
| RAFAELIA | sistema | Ecossistema de memória, relação, evidência, governança, execução e retroalimentação | VERIFIED |
| Ω / Omega | invariante | Princípio de coerência preservado durante transformação | VERIFIED |
| ΩGA | governança | Camada de política, evidência, validação, reversibilidade, auditoria e ética por design | VERIFIED |
| Omega Kernel | kernel | Núcleo determinístico de transformação de estado com sandbox, checkpoint e auditoria | VERIFIED |
| OmegaNode | schema | Célula semântica com valor, evidência, relação, validação e confiança | HYPOTHESIS |
| OmegaArtifact | schema | Documento/unidade de conhecimento com origem, contexto, evidências, revisões e relações | HYPOTHESIS |
| Relation | relação | Aresta entre conceitos, calculada por evidência, coerência, temporalidade e validação | HYPOTHESIS |
| Evidence | evidência | Registro verificável que sustenta uma alegação ou relação | VERIFIED |
| TOKEN_VAZIO | lacuna | Evidência necessária ainda não localizada | VERIFIED |
| VERIFIED | estado | Evidência direta localizada em arquivo, commit, artifact, release ou resultado | VERIFIED |
| DECLARED_BY_AUTHOR | estado | Declaração autoral ainda sem prova independente localizada no repo | VERIFIED |
| CONTRADICTION | estado | Evidência encontrada contradiz alegação anterior | VERIFIED |
| HYPOTHESIS | estado | Hipótese útil ainda não testada/reproduzida | VERIFIED |
| METAPHOR | estado | Metáfora geradora, sem status probatório | VERIFIED |
| SIGIL_SOCKET | runtime | Família de scripts e socket local vinculada à escuta simbiótica | DECLARED_BY_AUTHOR |
| .verbo.sock | runtime | Possível endpoint IPC/socket vivo usado como canal local | DECLARED_BY_AUTHOR |
| C14 | ponte | Camada de ponte entre silêncio, terminal, buffer e socket | DECLARED_BY_AUTHOR |
| BUFFER/ULTIMO_COMANDO | memória curta | Registro do último gesto/comando usado para retroalimentação | DECLARED_BY_AUTHOR |
| GODEX | núcleo operacional | Camada de boot/engine/OS simbiótico anterior ou paralela à RAFAELIA | DECLARED_BY_AUTHOR |
| ZIPRAF | selamento | Pacote/backup/hash/autoria; precisa separar formato real de metáfora | DECLARED_BY_AUTHOR |
| FIB / Fibonacci-Rafael | hipótese matemática | Família matemática autoral a formalizar e validar | HYPOTHESIS |
| Quantum Temple | arquitetura simbólica/técnica | Protótipo/linguagem de arquitetura híbrida clássica-quântica; exige validação separada | HYPOTHESIS |
| Ω Edge Cell | edge | Célula física: percepção, aquisição, processamento, decisão, ação e memória histórica | HYPOTHESIS |

## Estados permitidos

| Estado | Uso |
|---|---|
| VERIFIED | lido/confirmado por arquivo, commit, artifact, release ou resultado |
| DECLARED_BY_AUTHOR | declarado por Rafael ou por documento, sem validação independente no repo |
| TOKEN_VAZIO | lacuna explicitamente reconhecida |
| CONTRADICTION | evidência contraditória localizada |
| HYPOTHESIS | hipótese útil a testar |
| METAPHOR | metáfora ou parábola sem status de prova |

## Filtro de relação

```text
Peso = Evidência × Coerência × Reprodutibilidade
```

A relação pode inspirar hipótese. A hipótese só amadurece com teste. O teste só vira evidência quando é rastreável.

## Ciclo canônico

```text
Intenção
→ Observação
→ Artefato
→ Relação
→ Evidência
→ Governança
→ Execução
→ Auditoria
→ Retroalimentação
```

## Regra de escrita

Todo novo documento técnico deve declarar:

```text
origem
estado epistêmico
relações
limitações
próxima ação
```
