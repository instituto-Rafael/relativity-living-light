# NÃO PROMOVER — hipótese de fase e aleatoriedade quântica (Melkikh, 2026)

**Estado:** EXTERNAL_SCIENCE_INTAKE / DOCUMENTED_NOT_TESTED  
**Claim gate:** `claim_allowed=false`  
**Data de intake:** 2026-10-12  
**Domínio:** fundamentos quânticos; **não** constitui validação da teoria RLL, nem modificação de seus parâmetros físicos.  
**Produtor documental:** `instituto-Rafael/relativity-living-light`; bootstrap: [START HERE RLL](../presentation/00_START_HERE_RLL.md).  
**Rota federada:** [Mapa — Atlas/Leaders/Gates](https://github.com/rafaelmeloreisnovo/Mapa/blob/main/data/routes/RAFAELIA_PHASE_INTEGRATION_ATLAS_GATES_20261010.json).  
**Autoridade do conteúdo:** fonte externa, sem transferência de autoria ou validade científica para RLL.

## 1. SOURCE e proveniência

- Notícia: Alexey V. Melkikh, *De onde vem a aleatoriedade na mecânica quântica?*, Inovação Tecnológica, 09/10/2026. https://www.inovacaotecnologica.com.br/noticias/noticia.php?artigo=aleatoriedade-mecanica-quantica&id=010165261009
- Artigo científico identificado **na bibliografia da notícia**, sem revisão integral do PDF nesta rodada: A. V. Melkikh, *Generalized quantum computing and the problem of randomness origin in quantum mechanics*, *Quantum Research*, 1(1), 2026. DOI https://doi.org/10.55092/qr20260003.
- `SOURCE_STATUS=NEWS_READ_AND_PAPER_IDENTIFIED`; `PRIMARY_FULL_TEXT_REVIEW=TOKEN_VAZIO`; `INDEPENDENT_REPLICATION=TOKEN_VAZIO`.
- `ARTIFACT=this intake`; `EXECUTION=NOT_RUN`; `EVIDENCE=source_readback+repo_documentation_only`; `SCIENTIFIC_CLAIM=NOT_PROMOTABLE`.
- Não tratar a hipótese do artigo como formulação científica autoral RLL nem retrodatá-la para 2025.

## 2. Hipótese externa e separação epistemológica

A notícia apresenta a possibilidade de que variáveis de fase e dinâmica caótica determinística deem origem à aleatoriedade aparente de medições quânticas; propõe também uma estrutura topológica com relações não locais.

**Questões distintas, não intercambiáveis:**
1. Fase **relativa** entre componentes do estado: já possui consequências interferométricas na teoria padrão.
2. Fase **global** `|ψ⟩ → e^{iθ}|ψ⟩`: não muda probabilidades observáveis na mecânica quântica padrão; transformá-la em variável causal mensurável requer nova estrutura física explícita e teste.
3. Um processo caótico determinístico pode produzir sequências aparentemente aleatórias; isso, por si só, **não** demonstra que o colapso quântico é determinístico.
4. Teoremas/desigualdades de Bell restringem combinações de localidade, independência das configurações de medição e estrutura de variáveis ocultas. Chamar um espaço de “topológico” **não suspende** essas hipóteses matemáticas; uma teoria não local precisa declarar quais hipóteses modifica e preservar as restrições operacionais de sinalização.
5. Rejeitar um gerador aleatório por teste estatístico não identifica, sozinho, a causa quântica; ruído, deriva, viés e pós-processamento podem explicar desvios.

## 3. Contrato de reconstrução verificável

```text
INTENT=avaliar hipótese externa de origem da aleatoriedade quântica
CURRENT_STATE=RLL docs/presentation/05_CURRENT_STATE_RLL.md
SOURCE_MIN=notícia (lida), DOI (identificado), RLL_TRACEABILITY_MAP (lido)
AUTHORITY=autor científico para a hipótese; RLL apenas para intake/testes próprios
ROUTE=START_HERE -> CURRENT_STATE -> EXTERNAL_INTAKE -> FALSIFIER
EVIDENCE_RULE=previsão exclusiva + protocolo pré-registrado + dados/receipts independentes
CLAIM_ALLOWED=false
```

Não importar o modelo de fase como componente da equação cosmológica do RLL. Uma ponte RLL↔fundamentos quânticos só é discutível após uma derivação física específica (campo, ação/Hamiltoniano, dimensões, observável, causalidade e likelihood).

## 4. Hipóteses e falsificadores

| Item | Contrato | Estado |
|---|---|---|
| H0 | Estatísticas observadas são compatíveis com previsões quânticas convencionais e modelo calibrado de detector | BASELINE_TO_SPECIFY |
| H1 | Uma dinâmica explícita de variável de fase faz previsão quantitativa exclusiva e reproduzível | HYPOTHESIS_NOT_FORMALIZED |
| F1 | Testar invariância sob mudança de fase global; exigir previsão diferente da teoria padrão com operacionalização inequívoca | TOKEN_VAZIO_MODEL |
| F2 | Derivar correlações tipo CHSH com parâmetros e independências explicitados; verificar condições de Bell e não sinalização operacional | TOKEN_VAZIO_DERIVATION |
| F3 | Predizer contraste, regime e tamanho do desvio antes de acessar dados, com poder estatístico, vieses, multiplicidade e controles instrumentais | TOKEN_VAZIO_PREDICTION |
| F4 | Reproduzir dados brutos e pipeline de entropia/randomness: NIST SP 800-90B, controles de fonte, autocorrelação, perdas, condições e drift | TOKEN_VAZIO_DATA |
| F5 | Replicação independente em equipamento/laboratório diferente e relatório de resultados negativos | TOKEN_VAZIO_REPLICATION |

**Condição de falha da hipótese operacional:** depois de especificar o modelo e uma região pré-registrada de parâmetros, dados com precisão suficiente excluem a previsão diferenciadora de H1. Sem previsão diferenciadora, H1 permanece interpretação não discriminada, não evidência física.

**Precaução metodológica:** mesmo testes estatísticos bem-sucedidos não provam aleatoriedade fundamental; testes falhos não provam uma variável oculta particular.

## 5. Acoplamentos com RAFAELIA

- **Mapa/Atlas:** registrar `EXTERNAL_LITERATURE_ADJACENT`, não `CONFIRMED_PHYSICS`; herdar proveniência **sem** herdar verdade.
- **RLL:** `docs/RLL_TRACEABILITY_MAP.md` é a entrada de claims; não alterar `VALIDATION_STATUS.md` nem registrar aprovação de cosmologia por notícia externa.
- **Computação C freestanding/Q16.16:** uso potencial como laboratório de PRNG determinístico/caos e comparação de testes; simular caos não implementa mecanismo de colapso quântico.
- **Corpus/Drive:** Ledger append-only documenta intake e lacunas; não é prova experimental. Preservar receita de rollback/successor.

## 6. Gate de promoção e rollback

```text
G0 source locator / autoria           = PASS_SCOPED (notícia)
G1 paper integral lido/verificado     = TOKEN_VAZIO
G2 modelo dinâmico explícito          = TOKEN_VAZIO
G3 previsão diferente da MQ padrão   = TOKEN_VAZIO
G4 teste preregistrado + dados reais  = NOT_RUN
G5 revisão independente              = TOKEN_VAZIO
G6 RLL cosmological relevance         = NOT_ESTABLISHED
PROMOTION=BLOCKED
```

Documentação em branch/PR isolada; reversão via fechamento de PR ou commit sucessor/revert se futuramente houver merge autorizado. **Não há execução de CI ou experimento físico nesta rodada.**

## R3

- **F_ok:** notícia identificada; vínculo à rota START HERE/Mapa/RLL e limite entre hipótese, evidência e claim reconstruído; falsificadores tipados.
- **F_gap:** PDF integral, modelo formal, previsão exclusiva, dados, teste adversarial, revisão independente e qualquer ponte física para RLL.
- **F_next:** ler artigo primário integralmente e extrair suas equações/hipóteses; só então decidir se existe simulação reproduzível de baixo custo e um discriminador empiricamente testável.

*SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM. IMPLEMENTED_UNTESTED ≠ PASS.*
