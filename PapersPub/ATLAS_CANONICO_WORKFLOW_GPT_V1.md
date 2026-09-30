# Atlas Canônico Numerado para um Workflow Conversacional de Matemática, Geometria e Modelos RLL

**Versão:** 1  
**Data:** 2026-09-22  
**Autor registrado no projeto:** RAFAEL MELO REIS

## Resumo
Este documento formaliza uma arquitetura de indexação para conhecimento distribuído em conversas de projeto. O objetivo não é transformar recorrência narrativa em prova, mas preservar identidade, proveniência, contradição, incerteza, reprodução e rollback. O snapshot V1 contém 280 itens classificados como expressões exatas, teoremas clássicos, modelos, hipóteses, execuções, refutações, índices, relações, gaps e questões abertas.

## Arquitetura
O corpus é modelado como grafo tipado:

`G_project=(C,R)`, onde `C` representa conversas/fontes e `R` relações entre elas.

Objetos matemáticos e científicos recebem identidade independente da conversa:

`e_i --[relation,evidence]--> e_j`.

A navegação usa um router único, mas evita um arquivo monolítico como unidade de autoridade. A identidade reside no ID canônico; URLs são rotas.

## Separação epistêmica
1. matemática clássica permanece atribuída ao corpo clássico;
2. derivações do projeto são marcadas como derivadas;
3. hipóteses permanecem hipóteses até gate suficiente;
4. execução computacional não implica mecanismo físico;
5. `TOKEN_VAZIO` não é convertido em zero nem completado por invenção;
6. correções usam `supersedes` sem apagar versões anteriores.

## Compatibilidade
Registries existentes (`TH-*`, `PRM-*`, Ω300, GETP-369 e outros) não são renumerados. O novo Atlas atua como camada de reconciliação, com relações `same_as`, `derived_from`, `tested_by`, `contradicts`, `supersedes` e `has_gap`.

## Falsificabilidade e reprodução
O gate mínimo do snapshot V1 verifica:
- exatamente 280 endereços legados numerados;
- sequência 1..280 sem buracos;
- relações com quatro colunas;
- referências `ITEM-xxxxxx` dentro do intervalo;
- presença de invariantes epistêmicos fundamentais;
- compatibilidade entre tipos de relação usados e schema.

## Limites
Este Atlas não demonstra universalidade física, superioridade de compressão, autoria sobre teoremas clássicos ou validade cosmológica por analogia geométrica. Resultados RLL permanecem subordinados às evidências observacionais e aos critérios AIC/BIC/likelihood registrados.

## Conclusão
A principal contribuição operacional é separar URL, identidade, fonte, evidência e claim enquanto mantém reconstruibilidade do workflow. O crescimento posterior deve ocorrer por append-only e relações tipadas, não por renumeração destrutiva.
