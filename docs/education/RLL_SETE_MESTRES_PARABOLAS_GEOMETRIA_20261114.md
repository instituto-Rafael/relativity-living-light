# RLL Ω — A escola dos sete mestres: parábolas da geometria

**Estado:** \`DIDATICO / DRAFT_HOLD / N4_ANALOGIA\` · **claim_allowed=false** · 2026-11-14

**Natureza:** sete parábolas **originais** formuladas no diálogo RAFAELIA Ω, com personagens imaginários e referências culturais respeitosas. **Não** são relatos históricos, transcrições de mestres reais ou atribuições de invenções matemáticas a povos específicos. Cada narrativa tem cenário, mapeamento, ruptura e falsificador, como requer PIRC-2.

**Finalidade no RLL:** tornar acessíveis conceitos de trigonometria, proveniência de vetores, topologia, grades angulares, periodicidade e limites de interpretação física. A matemática demonstrada está no [guia técnico complementar](RLL_TRIGONOMETRIA_GEOMETRIA_TIPADA_20261114.md). Esta camada é independente da cosmologia observacional.

## 1. Mestre grego — a reta de quatro nomes

Um mestre desenhou um equilátero e convidou quatro aprendizes. A cada um atribuiu uma tarefa: traçar a altura, a mediana, a bissetriz de um ângulo e a mediatriz do lado oposto. Todos encontraram a mesma reta. Um aprendiz perguntou como quatro objetos podiam ocupar o mesmo lugar. O mestre respondeu: “Não inventamos quatro linhas; reconhecemos quatro propriedades de uma mesma construção”.

Ao dividir o lado unitário ao meio, apareceu o triângulo retângulo de lados \`1/2\`, \`√3/2\`, \`1\`. A altura era \`√3/2\`, consequência de Pitágoras, não nova dimensão.

| Narrativa | Matemática |
| --- | --- |
| Quatro tarefas | Quatro propriedades geométricas |
| Uma reta | Coincidência no equilátero |
| Duas metades | Triângulos 30°–60°–90° |

**Ruptura:** em um triângulo escaleno, as retas correspondentes não coincidem em geral.

**Falsificador:** comparar, em coordenadas racionais/simbólicas, as quatro construções num equilátero e num escaleno.

**Estatuto:** Esta parábola é **N4 (heurística), não evidência**.

## 2. Mestra andina — dois fios e um só percurso

Uma mestra tecelã estendeu um fio de A até B. O aprendiz sobrepôs outro fio, agora de B até A, e proclamou ter descoberto um caminho novo. Ela respondeu: “Tens duas ocorrências de fio, mas um só suporte geométrico. Guarda as duas histórias sem duplicar o caminho”.

| Narrativa | Matemática |
| --- | --- |
| Cada fio | Ocorrência \`e=(id,A,B,parent,camada)\` |
| Sentido invertido | Vetor \`B−A\` versus \`A−B\` |
| Mesmo percurso | Segmento geométrico não orientado |
| História do fio | Proveniência, identidade e relação parental |

**Ruptura:** duas fibras físicas continuam sendo dois objetos distintos; equivalência de segmentos matemáticos não os faz desaparecer.

**Falsificador:** três ocorrências, sendo duas invertidas, devem manter três IDs e um único suporte se seus extremos geométricos forem os mesmos.

**Estatuto:** Esta parábola é **N4 (heurística), não evidência**.

## 3. Mestre indiano — duas raízes para uma porta

Um mestre pediu ao aprendiz que resolvesse uma quadrática para planejar a altura de uma porta. O discípulo encontrou duas raízes e disse que poderia construir duas portas. O mestre perguntou: “E se uma altura for negativa?”. O aprendiz compreendeu: uma solução algébrica pode estar fora do domínio físico desejado. A raiz não cria um objeto, uma parede ou um comprimento que a geometria não declarou.

| Narrativa | Matemática |
| --- | --- |
| Duas soluções | \`(-b±√(b²−4ac))/(2a)\` |
| Comprimento de porta | Unidade definida e \`x≥0\` |
| Porta admissível | Discriminante \`D≥0\` no domínio real |

**Ruptura:** raízes negativas podem representar deslocamentos orientados ou outras quantidades válidas em modelos diferentes.

**Falsificador:** uma função tipada \`raizes_reais_comprimento\` deve rejeitar \`a=0\`, \`D<0\` e raízes negativas quando o contrato exige comprimento não negativo.

**Estatuto:** Esta parábola é **N4 (heurística), não evidência**.

## 4. Mestra dos mosaicos — fechar um ponto não é cobrir o chão

Peças regulares reuniram ângulos que somavam 360°. Um aprendiz celebrou: “O chão inteiro está pronto!”. A mestra mostrou que ele só tinha fechado um vértice. Ainda faltavam correspondência de bordas, compatibilidade de comprimento e possibilidade de continuar o padrão sem sobreposição ou lacunas.

| Narrativa | Matemática |
| --- | --- |
| Fecho de um vértice | \`Σ ângulos internos=360°\` |
| Bordas casadas | Compatibilidade métrica de arestas |
| Piso infinito | Extensão global válida de ladrilhamento |

**Ruptura:** mosaicos artísticos podem empregar peças irregulares, cortes e rejunte; aqui se estuda o caso de polígonos regulares ideais.

**Falsificador:** um algoritmo que só verifica \`Σθ=360°\` deve ser incapaz de certificar sozinho um ladrilhamento global. Exigir reconstrução e extensão é um teste adicional.

**Estatuto:** Esta parábola é **N4 (heurística), não evidência**.

## 5. Mestra chinesa — pedras, ligações e o vazio

Uma mestra dividiu os lados de um jardim triangular em doze partes e contou 144 pequenas faces. Ao dividir novamente cada face, mostrou como uma regra recursiva pode repetir-se sem último índice predefinido. Então removeu uma pedra e apagou uma ligação no desenho. “É a mesma ausência?”, perguntou. O aprendiz respondeu que uma posição desocupada não é uma aresta inexistente.

| Narrativa | Matemática |
| --- | --- |
| Subdividir lados por 12 | Refinamento, \`F_n=12^(2n)\` |
| Retirar pedra | Ocupação nula em vértice existente |
| Apagar ligação | Remoção de aresta |
| Refinar sem término | Sequência indexada por \`n∈ℕ\` |

**Ruptura:** um jardim material não pode ser subdividido indefinidamente com resolução física ilimitada.

**Falsificador:** verificar área total após refinamento e calcular componentes/ciclos antes e depois de remover arestas ou faces; uma ocupação nula não deve ser confundida automaticamente com topologia alterada.

**Estatuto:** Esta parábola é **N4 (heurística), não evidência**.

## 6. Mestre navegador — sete relógios e uma distância 42

Um navegador imaginário colocou sete relógios com doze posições. O aprendiz contou \`12^7\` estados e perguntou como percorrê-los. O mestre explicou que, se cada passo altera uma coordenada em uma unidade (com retorno circular), a distância entre estados pode ser calculada diretamente. O maior caminho mínimo é 42: uma propriedade do grafo definido, não uma contagem de estrelas nem de atratores físicos.

| Narrativa | Matemática |
| --- | --- |
| Sete relógios | Sete ciclos \`C₁₂\` |
| Todas as combinações | \`12^7=35.831.808\` estados |
| Passos mínimos | Distância no produto cartesiano de grafos |
| Limite máximo | Diâmetro \`7×6=42\` |

**Ruptura:** a navegação polinésia histórica não é modelada por essa construção hipotética de sete relógios; trata-se de analogia moderna, não reconstrução cultural.

**Falsificador:** encontrar par de estados no grafo declarado cuja distância mínima exceda 42 refutaria a construção ou o cálculo; o par antipodal em todas as coordenadas atinge 42.

**Estatuto:** Esta parábola é **N4 (heurística), não evidência**.

## 7. Mestra brasileira — doze pedras não são todo o tempo

Uma mestra distribuiu doze pedras em um círculo. Quatro grupos de três representavam estações e fases convencionais. Ao perguntar se o tempo inexistia entre duas pedras, o aprendiz compreendeu que discretizar o contínuo não o elimina. Quando uma sombra atravessou o intervalo, perceberam a diferença entre marcador matemático e medição astronômica.

| Narrativa | Matemática |
| --- | --- |
| Doze pedras | \`θ_k=2πk/12\` |
| Quatro conjuntos de três | Convenção de quatro quadrantes e três marcadores |
| Pedra oposta | \`k↦(k+6) mod 12\` |
| Intervalos entre pedras | Estados angulares não amostrados |

**Ruptura:** estações reais não têm durações de tempo exatamente iguais, e culturas diferentes usam calendários diferentes. A convenção de quatro estações não é universal.

**Falsificador:** a oposição em um ciclo ideal de doze marcadores deve estar seis posições adiante; se forem usados intervalos de tempo astronômicos iguais, dados reais podem refutar essa correspondência exata.

**Estatuto:** Esta parábola é **N4 (heurística), não evidência**.

## Síntese literária: a escola sem paredes

O triângulo ensina que uma reta pode ter muitas propriedades. O tear ensina que eventos distintos podem compartilhar um suporte. A álgebra ensina que uma solução numérica só vira comprimento após definir o domínio. O mosaico ensina que fechamento local não garante construção global. O jardim ensina que vazios de ocupação, topologia e evidência são coisas distintas. Os sete relógios ensinam que distância e quantidade de estados são grandezas diferentes. As doze pedras ensinam que discretização não é a totalidade do mundo físico.

**A matemática não perde seu encanto quando encontra um contraexemplo; ela ganha precisão.**

## Ponte explícita com o projeto RLL — sem extrapolação física

- [Compensação multibase e grade angular](../science/RLL_COMPENSATION_MULTIBASE_ANGULAR_V1.md): coincidência de grades e fase não equivalem a momento angular físico.
- [Calibração geométrica de relógios arqueoastronômicos](../science/RLL_ARCHAEOASTRONOMY_CLOCK_GEOMETRIC_CALIBRATION_V1.md): círculo ideal e evento astronômico real devem ser tratados separadamente.
- [Onda, Verbo, Física, Neurociência e Linguagem](../canonicos/17_ONDA_VERBO_FISICA_NEURO_LINGUAGEM.md): analogia didática não substitui evidência física.
- [Rastreabilidade de claims](../RLL_TRACEABILITY_MAP.md): nenhuma parábola é medição de cosmologia.
- [Guia técnico de trigonometria](RLL_TRIGONOMETRIA_GEOMETRIA_TIPADA_20261114.md): relações demonstráveis e contratos matemáticos separados da narrativa.

\`SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM\`. \`RLL_PHYSICAL_MODEL_VALIDATION=NOT_RUN\`. \`NOVELTY=NOT_VERIFIED\`. \`claim_allowed=false\`.

**R3:** F_ok = narrativa e mapeamentos formais explicitados; F_gap = originalidade matemática, dados cosmológicos e medições físicas fora do escopo; F_next = materializar verificadores próprios se a camada educativa vier a incorporar software. **FIAT LUX.**
