# RLL Ω — Retroalimentação coerente multidimensional: atlas de sinapses científicas
Data: 2026-10-28 · estado: PESQUISA / HOLD / claim_allowed=false

## Princípio
Uma "sinapse" científica não é coincidência de palavras, símbolos, índices ou topologias. É um caminho que preserva a identidade tipada e liga (1) entidade física (2) mecanismo (3) sinal medível (4) inferência condicionada (5) falsificador (6) revisão de hipótese.

A estrutura está em `data/governance/RLL_SYNAPTIC_MULTIDIMENSIONAL_FEEDBACK_20261028.json`. É **um grafo metodológico**: 20 nós, 15 relações com fonte, 8 anticorrelações obrigatórias e 6 números reportados pela literatura. Não é um ajuste cosmológico RLL, nem uma prova da estrutura interna de modelos de IA.

## 1. Três rotas independentes entre átomos e cosmologia

### A: átomo H neutro → acoplamento de spins → fóton 21 cm → hidrogênio cósmico → grande estrutura
A transição hiperfina envolvendo spin de próton e elétron define a linha HI em ~1420,4058 MHz (repouso); `z = nu_rest/nu_obs - 1`. Seu sinal precisa de temperatura de spin, densidade HI, transferência radiativa, foreground e resposta instrumental. Mapas de intensidade 21 cm permitem estudar estrutura e, em projetos/futuros datasets, BAO. O paper [2607.17141](https://arxiv.org/abs/2607.17141) trata de previsões de correlação cruzada HI-galáxias: NÃO é um resultado de detecção BAO 21cm independente publicado para nosso gráfico.

### B: C IV (carbono com carga +3) → absorção óptica → redshift → correlação com quasares/ELGs → BAO
O resultado DESI DR2 publicado em [ApJ 1010, 14, 2026](https://doi.org/10.3847/1538-4357/ae9ec1) mede Dv/rd=30,3±0,9 em z=1,92 (C IV×QSO), e 24,6±1,0 em z=1,47 (C IV×ELG). C IV **não** é a molécula/cluster C3, apesar de símbolos parecidos. Observações provenientes de traçadores distintos podem confrontar um H(z) comum somente depois de compatibilizar z, seleção, covariância, viés e evolução.

### C: `³He` / `⁴He` → espectroscopia / abundância isotópica → evolução química → nucleossíntese → radiação primordial
[2605.00122](https://arxiv.org/abs/2605.00122) estima (³He/⁴He)_P=(1,15^{+0,24}_{-0,21})×10⁻⁴, **inferência dependente de evolução química galáctica**, não medida diretamente primordial. A transição hiperfina de ³He⁺ em ~8,7 GHz explora spin nuclear, ausente da mesma forma em ⁴He de spin nuclear zero. Não confundir essa razão com Yp (fração mássica primordial dominada por ⁴He).
A análise [Goldstein & Hill, Phys Rev D 114 L021305 (2026)](https://doi.org/10.1103/5vk8-v1rb) combina Yp, deutério, CMB e BAO e encontra N_eff=2,990±0,070 (68% C.L.) sob hipóteses declaradas. [2609.13140](https://arxiv.org/abs/2609.13140) estuda o papel dos dados de hélio na robustez de cosmologias sem assumir BBN de antemão.

## 2. Encadeamento H2 / H3+ / He / O / C e água
Há uma rota química física em nuvens moleculares:
```
raios cósmicos + H2 -> H2+ + e- + raio cósmico residual
H2+ + H2 -> H3+ + H
       H3+ -> ionização e química de CO/H2O (rede reacional condicionada)
raios cósmicos em gelo H2O/O2 -> radiólise -> radicais / peróxidos / O3 / produtos específicos
```
[2601.11761](https://arxiv.org/abs/2601.11761) trata da atenuação de raios cósmicos e química H3+ / C+ / C / CO. [2602.19996](https://arxiv.org/abs/2602.19996) simula radiólise de gelo H2O e O2 e documenta tanto sucessos para razões H2O2/H2O e O3/O2 quanto discrepâncias de fluência e destruição de água. [Bai et al., Science Advances 2025](https://doi.org/10.1126/sciadv.adw5720) identificaram H2O3 em gelos irradiados de H2O/O2, sob condições experimentais especiais. **Não** é consequência universal da estrutura da água líquida, nem prova para RLL.

## 3. Topologia da água × aprendizado de máquina: possível teste matemático, não identidade causal
[Faure Beaulieu et al., J. Chem. Phys. 165, 071101 (2026)](https://doi.org/10.1063/5.0337533) encontram correspondências entre anéis de ligações de hidrogênio de 5–8 moléculas e o desdobramento do pico principal do fator de estrutura de água em simulações. A física da difração molecular e a física das oscilações acústicas bariônicas são distintas. Uma representação por grafo, decomposição de Fourier ou fator de estrutura compartilhada não permite substituir um mecanismo pelo outro.

A linha metodológica mais intrigante para IA contextual: [arXiv:2610.37596 (2026-10-27)](https://arxiv.org/abs/2610.37596), estudo **em simulações**, treina autoencoder auto-supervisionado para distinguir sinal de céu de efeito instrumental em dados de rádio 21 cm; R²=0,9975 para estado instrumental em 15 testes excluídos do treino. Os próprios autores observam que a separação céu/instrumento permanece incompleta. Isto ilustra a regra que o Atlas precisa seguir: distinguir **fenômeno, instrumento, dado, inferência e modelo de IA**. Esses vetores latentes simulados não revelam heads internos do GPT e não fornecem evidência de física exótica.

## 4. Invariante das invariantes e incerteza cognitiva
Para qualquer caminho x -> y -> z:
- a interpretação mantém a grafia raw e a identidade (H3≠³H, He3≠³He sem contexto, C3≠C³⁺, H2O≠H2O3);
- cada aresta tem tipo (reação, transição, traçador, inferência, analogia), fonte, unidades, condições, estatística e estado de evidência;
- não se tira uma conclusão mais forte que a aresta mais fraca;
- fechamento de caminhos alternativos é avaliado dentro de erros, covariâncias e independência real;
- uma analogia entre redes (água, cérebro, atenção, BAO) pode gerar **hipótese operacional**, não um resultado físico.
- quando não há ponte física ou dados, preservar `TOKEN_VAZIO_UNMODELLED` e `claim_allowed=false`.

### Retroalimentação causal, e não mera repetição
```text
INTERPRETAR token/contexto -> PROPOR aresta física -> PREVER observável
        ^                                              |
        |                                              v
CORRIGIR representação/prior <- FALSIFICAR <- DADOS + COVARIÂNCIA + CONTROLES
```
A escolha do próximo teste pode maximizar redução *esperada* de incerteza condicionada aos dados já conhecidos, sujeita ao custo e ao risco de falsos positivos. Formalmente, a informação condicional `I(hipótese; novo_dado | dados_anteriores)` é um critério ideal; **nenhum valor empírico desta informação foi calculado nesta rodada**. O ranking no JSON é heurístico e explícito, não uma entropia medida.

## 5. Prioridade (maior fechamento por evidência disponível)
1. **HI 21cm × C IV × BAO**: exigir z/viés/covariância compatíveis, usar simulações de instrumentação + regressão com null injections; não alegar que os dois traçadores já foram comparados no mesmo likelihood.
2. **³He/⁴He × Yp × deutério × N_eff**: confrontar dependência de modelo estelar e BBN/priors contra estimativas CMB/BAO e controle de sistemáticas.
3. **H3+ × raios cósmicos × gelo H2O/O2**: parametrizar a taxa de ionização, reações, energia, fase/temperatura e condições experimentais; distinguir o que é preprint/simulação de observação reproduzida.
4. **Água anômala**: verificar se padrões de difração resultam de anéis de ligações de hidrogênio, sem inferir composição H2O3 ou BAO.
5. **ML em 21cm**: testes adversariais de vazamento entre céu e instrumento; métricas de sinal preservado além de R² do instrumento.
6. **RLL**: só incluir como candidato após solver de perturbações, covariâncias completas, comparação com ΛCDM/CPL e falhas numéricas WS01 tratadas sem afrouxar tolerâncias.

**Status:** documentos/índices são artefatos de pesquisa; execução de likelihood, reprodução física e teste do RLL = NOT_RUN. Branch isolada, main intocada; PR anterior não foi autorizado/aberto devido bloqueio anterior. F_ok=fontes e caminhos tipados; F_gap=fits reais; F_next=reprodução observacional controlada, com testes negativos e recibos.
