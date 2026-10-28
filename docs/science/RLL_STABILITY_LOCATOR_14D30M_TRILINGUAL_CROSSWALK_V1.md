# RLL Ω · Integração de estabilidade 14 dias / janela observacional 30 min / informação trilíngue

**Estado:** IMPLEMENTED_SYNTHETIC_ONLY · claim_allowed=false · PROMOTION=HOLD. Não é um serviço meteorológico nem prevê furacões.

## Reconstrução coerente da sessão (source → artifact → evidence)

1. A raiz física é a **estabilidade de massas de ar**: P, T, vapor, densidade, temperatura virtual, correntes 3D, gradientes de pressão, cisalhamento e convecção. Ver patch Climate 8×8 e PR #1138 (DRAFT); o trabalho de núcleo C freestanding não equivale a modelo dinâmico completo.
2. Uma camada de contexto inclui oceanos, evaporação, marés astronômicas/barométricas, atividade solar, ionosfera, falhas tectônicas, vulcões e alterações históricas. Estas são famílias de dados diferentes, não uma variável causal única.
3. A hipótese de 51 anos e a hipótese do Calendário Redondo mesoamericano de 52 anos devem ser testadas **separadamente** (PR #1139 DRAFT). 1975–2025 não comprova um ciclo de 51 anos. Comparar com ciclos físicos conhecidos e verificar se qualquer termo adiciona habilidade preditiva além de baselines.
4. Relógios astronômicos e sombras de Chichical (topônimo pendente de identificação), Stonehenge, pedras de 12 ângulos, Trilha da Oração e dutos da Grande Pirâmide de Gizé foram propostos para verificação geométrica. Não há calibração observacional dos alinhamentos, datação de eixo ou histórico do duto até aqui. O calendário maia Tzolk'in tem 13×20=260 dias; o Haab' tem 18×20+5=365 dias; 52 Haab' ≈ 18.980 dias. Não equiparar diretamente aos 12 meses gregorianos ou a uma força gravitacional.
5. No RLL SCD1 original (Gênesis/Mateus/João; ENG/SPA/POR; 3483 refs/língua; 10449 registros) a semente com referências compartilhadas economizou 22,474% vs JSON verboso, mas é 4,885% maior que texto simples. O gate G2 de ganho forte FALHOU. Comprimir o mesmo significado em línguas diferentes **não garante taxas iguais**. O módulo Python em scripts/rll_stability_information_bridge.py executa contraexemplo sintético sem conteúdo bíblico copiado.
6. Órbita Juno/Júpiter e fotos de satélite são famílias valiosas para comparar dinâmica/estrutura, mas imagens não são valores do campo gravitacional ou evidência de previsibilidade de furacões na Terra.

## Alvo operacional delimitado

**Horizonte A — até 14 dias:** rastrear *regiões e janelas* com ambiente mais favorável à atividade ciclônica a partir de previsão por conjunto (ECMWF ENS, ou equivalente autorizado). NÃO prometer nascimento/posição/intensidade exatos de um furacão a 14 dias.

**Horizonte B — até 30 minutos:** avaliar mudança OBSERVADA de pressão/vento, nuvens e circulação; NÃO afirmar gênese em 30 min. A definição NHC de intensificação rápida é +30 nós em 24 horas. Referência NOAA https://www.nhc.noaa.gov/aboutgloss.shtml

A orientação operacional do NHC usa Tropical Weather Outlook até 7 dias e previsões de tempestades existentes até 5 dias. Referência NOAA https://www.noaa.gov/explainers/hurricane-forecasting . O ECMWF publica produtos de atividade de ciclones em dias/semanas e extensão probabilística; não implica localizador exato a 14 dias. Referência https://www.ecmwf.int/en/forecasts/charts/latest-tropical-cyclones-forecast

## Contrato do protótipo em C11 freestanding

native/climate_stability_locator/rll_stability_locator.h e .c: até 16 células com lat/lon, ID e cinco variáveis z-score×100 providas por pipeline upstream validado. Horizonte válido ≤20160 minutos, tempo de emissão/recebimento de cada variável ≤issue, valid_target correto. Input ausente é marcado por máscara, nunca convertido em zero medido. Score 0..600 é APENAS ranking determinístico convencional, NÃO probabilidade nem evidência de desempenho. Dois registros de pressão/vento separados por 1..30 minutos permitem sinal de tendência 0 (não mensurado), 1 (sem cruzar limiar) ou 2 (cruzou limiar arbitrário). Ambas as saídas de alerta são sempre 0.

Thresholds, pesos e orientação de cada variável são **placeholders de software**; até a descrição física 'baixo cisalhamento favorece ciclones' depende do contexto. Nenhum modelo climático foi calibrado, instalado ou validado para inferir furacões.

scripts/rll_stability_information_bridge.py: calcula entropia Shannon por byte e razões gzip/bz2/lzma de três frases ORIGINAIS sintéticas, com decompression equality. Consulta apenas o receipt agregado do SCD1 pré-existente; não redistribui corpus. Não produz feature meteorológica, não infere entropia termodinâmica nem medição de 'sintropia'.

## Falsificação preregistrada

- G0: licença e domínio de fontes, versão de cada modelo, SHA-256 do input, assinatura do horário *publicado/available-as-of*, unidades, dados ausentes, latitude/longitude e incerteza.
- G1: congelar emissão 14 dias antes e alvo verificável: atividade regional ou evento de formação em janela declarada; só depois confrontar com IBTrACS e observações independentes.
- G2: comparadores NHC 7d (somente nos horizontes que abrange), ECMWF ENS 14d e climatologia por bacia/estação; mesma janela e recursos. Nunca extrapolar NHC 7d para 14d.
- G3: separação por tempestade/ano/bacia; ablação 51/52 anos, maré lunar, Juno, ionosfera e compressão; nenhum deles ganha peso sem desempenho incremental replicado.
- G4: Brier/log-score/CRPS de probabilidades PRODUZIDAS POR MODELO CALIBRADO externo, diagrama de confiabilidade, PR-AUC, recall, taxa de alarme falso, custo e intervalo de confiança. O score C local não é probabilidade, logo não deve entrar como Brier sem calibração separada.
- G5: manipulação adversarial de horários, frames futuros, permissões, campos não medidos, mudança de unidades, drift, ruído vermelho, mudança de resolução, exceções de costa/ilha, ciclones extratropicais.
- G6: revisão independente antes de qualquer alerta, hierarquia de comunicação NOAA/órgãos meteorológicos/Defesa Civil e proteção a crianças/comunidades e culturas locais.

## Proveniência / estado / reversibilidade

Corpus SCD1 original: PapersPub/09_language_entropy_formalism/results/SCD1_20260920.json e G123_20260921.json; sinais meteorológicos 14d e 30min **NÃO INGERIDOS** neste PR. Os arquivos dos PRs #1138/#1139 permanecem em branch separada e não são dependências executáveis deste módulo. Este delta não altera as fontes Climate originais.

F_ok = fontes anteriores recuperadas, regras separadas e núcleo testado com fixture sintética + falsificadores de vazamento; F_gap = TOKEN_VAZIO_REAL_14DAY_ENS, TOKEN_VAZIO_30MIN_GAUGES, TOKEN_VAZIO_SST_OCEAN, TOKEN_VAZIO_14DAY_OBSERVED_SKILL, TOKEN_VAZIO_INDEPENDENT_REVIEW, TOKEN_VAZIO_ANDROID_DEVICE, TOKEN_VAZIO_ASTRONOMICAL_CLOCK_CALIBRATION; F_next = congelar dados de uma bacia e uma estação, comparar modelos de referência usando timestamps que existiam na emissão e executar a validação cega.

Rollback: fechar PR DRAFT e descartar branch; nenhuma fonte histórica foi substituída, e manter resultados negativos nos receipts.
