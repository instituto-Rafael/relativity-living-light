# Matriz de Evidências e Contradições — Eventos Raros V1

## Contrato operacional

Cada linha deve ligar `claim → fonte → proveniência → incerteza → falsificador → decisão`.
Nenhuma célula ausente pode ser completada por inferência narrativa: usar `TOKEN_VAZIO`.

## Régua de qualidade da fonte

| Nível | Definição | Uso permitido |
|---|---|---|
| P0 | sem fonte identificada | apenas localizar |
| P1 | relato secundário ou reprodução | gerar hipótese |
| P2 | vídeo/foto original com origem verificável | restringir geometria e sequência |
| P3 | laudo, telemetria ou registro oficial | sustentar evidência |
| P4 | conjunto P3 revisado independentemente | promover claim dentro do escopo |

## Matriz inicial

| Claim | Estado | Fonte atual | Nível | Contradições abertas | Falsificador | Próxima ação |
|---|---|---|---:|---|---|---|
| AI171-C01 | EVIDENCIADO | registro público ainda não anexado ao repositório | P1 | cadeia de custódia ausente | documento oficial negar a sobrevivência | anexar fonte primária e hash |
| AI171-C02 | TOKEN_VAZIO | nenhuma reconstrução completa anexada | P0 | forças, assento, rota e cronologia incompletos | geometria/cronologia incompatível com a rota proposta | aguardar relatório final e reconstrução independente |
| AI171-C03 | REFUTADO | nenhuma prova de violação física | P0 | claim forte sem mecanismo testável | modelo reproduzível demonstrar incompatibilidade física | manter rejeitado; reabrir somente com dados primários |
| AI171-C04 | MODELO_ANALOGICO | interpretação pessoal | N/A | confusão possível entre sentido e causalidade | apresentação como mecanismo físico sem evidência | manter camada semântica separada |
| AUTO-C01 | TOKEN_VAZIO | caso não identificado | P0 | local, data e ocorrência desconhecidos | identificação documental incompatível com o relato | localizar vídeo original ou ocorrência |
| AUTO-C02 | TOKEN_VAZIO | velocidade relatada sem telemetria | P0 | intervalo 160–190 km/h não verificado | telemetria ou reconstrução excluir o intervalo | obter laudo/telemetria; estimar apenas intervalo defensável |
| AUTO-C03 | TOKEN_VAZIO | posições relatadas sem geometria | P0 | banco, portas, ocupantes e porta-malas não verificados | imagens/laudo mostrarem posições diferentes | identificar modelo do veículo e sequência quadro a quadro |
| AUTO-C04 | TOKEN_VAZIO | mecanismo ainda não modelado | P0 | ausência de dados confundida com inexplicabilidade | qualquer reconstrução física coerente com os dados | proibir conclusão até AUTO-C01..C03 avançarem |

## Permutações controladas

Somente variáveis não confirmadas podem variar. Para cada cenário registrar:

```text
scenario_id
fixed_facts[]
variable_assumptions[]
geometry_compatible: true|false|TOKEN_VAZIO
kinematics_compatible: true|false|TOKEN_VAZIO
biomechanics_compatible: true|false|TOKEN_VAZIO
contradictions[]
rejection_reason
```

A enumeração não converte cenário em fato. Cenários sobreviventes continuam `HIPOTESE` até evidência independente.

## Gate de promoção

Um claim só pode deixar `TOKEN_VAZIO` quando possuir, no mínimo:

1. fonte primária identificada;
2. hash ou identificador persistente;
3. escopo exato do que a fonte demonstra;
4. incerteza declarada;
5. falsificador explícito;
6. revisão independente;
7. ausência de contradição crítica aberta.

## Receipt de execução

- registry: `data/knowledge_forest/rare_events_claim_registry_v1.yml`
- validator: `scripts/validate_rare_events_registry.py`
- tests: `tests/test_rare_events_registry.py`
- workflow: `.github/workflows/rare-events-evidence-gate.yml`
- estado: `claim_allowed=false`, `publication_ready=false`
