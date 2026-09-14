# Contrato de Falsificabilidade — Bagua, T⁷, √3/2 e Atratores RAFAELIA

**Autor:** Rafael Melo Reis — RAFCODE-Φ / ∆RafaelVerboΩ  
**Data:** 2026-07-10  
**Escopo:** impedir que linguagem simbólica, implementação computacional e afirmação física sejam confundidas.

## 1. Regra central

Uma metáfora pode orientar a arquitetura, mas somente uma definição operacional pode produzir uma hipótese testável.

\[
\text{metáfora}\neq\text{modelo}\neq\text{evidência}\neq\text{lei física}.
\]

Cada transição entre essas classes exige um artefato verificável.

## 2. Registro das afirmações

| ID | Afirmação | Estado atual | Critério mínimo de promoção |
|---|---|---|---|
| BGT7-01 | Yin/Yang pode ser codificado como bits | implementável | teste exaustivo de `NOT`/`XOR` |
| BGT7-02 | Trigramas formam oito estados de 3 bits | demonstrado por enumeração | tabela completa `0..7` |
| BGT7-03 | ROL/ROR de 3 bits representam giro discreto | demonstrável | prova de bijeção e teste inverso |
| BGT7-04 | `√3/2` aparece na rotação de 30° | demonstrado | derivação trigonométrica |
| BGT7-05 | rotação de 30° contrai o estado | falso sem fator adicional | mostrar `RᵀR=I`; declarar `κ<1` separadamente |
| BGT7-06 | `κ=√3/2` gera contração linear | válido para mapa declarado | especificar `xₙ₊₁=κRxₙ` e domínio |
| BGT7-07 | existem exatamente 42 órbitas estáveis | hipótese | mapa, enumeração, classes e estabilidade |
| BGT7-08 | `Ω=23,158` é atrator | hipótese | convergência, unidade, erro e modelo nulo |
| BGT7-09 | hash Phi64 cancela entropia | não sustentado | definir métrica; evitar linguagem física indevida |
| BGT7-10 | XOR realiza compressão | falso em geral | demonstrar codec, taxa e reconstrução sem perda |
| BGT7-11 | `T⁷` intercepta um espaço Bagua 8D | metáfora incompleta | definir espaços, imersão/projeção e interseção |
| BGT7-12 | dinâmica possui consequência física | não estabelecido | observável, unidade, instrumento e previsão distinta |

## 3. Modelo mínimo obrigatório

Nenhum resultado orbital deve ser publicado sem uma função de transição completa:

\[
F:S\rightarrow S,
\]

com estado, parâmetros e domínio declarados.

Uma forma aceitável é

\[
S_n=(b_n,y_n^+,y_n^-,\theta_n,x_n,h_n),
\]

onde:

- `b_n ∈ Z₈`;
- `y_n⁺,y_n⁻ ∈ Z₂`;
- `θ_n ∈ T⁷`;
- `x_n ∈ Rᵐ`;
- `h_n` é memória discreta finita.

A publicação deve fornecer todas as componentes de `F`; nomes simbólicos sem equação não satisfazem o contrato.

## 4. Protocolo para as 42 órbitas

### 4.1 Definição

Uma órbita periódica de período `p` é uma sequência em que

\[
F^p(S_0)=S_0
\]

com `p` mínimo.

### 4.2 Distinção

Duas órbitas que diferem apenas pelo ponto inicial do mesmo ciclo contam como uma única classe orbital.

### 4.3 Estabilidade

Para dinâmica diferenciável, calcular o mapa de retorno:

\[
J_p=DF(S_{p-1})\cdots DF(S_0).
\]

A órbita será classificada como localmente assintoticamente estável quando

\[
\rho(J_p)<1.
\]

Para componentes discretas, usar perturbações no espaço de estados, bacias de atração e distância explicitamente definida.

### 4.4 Critério de aceitação

A alegação “42 órbitas estáveis” somente passa se:

1. exatamente 42 classes forem encontradas dentro do domínio declarado;
2. todas satisfizerem o critério de estabilidade;
3. nenhuma 43ª classe aparecer em busca ampliada;
4. o resultado sobreviver a mudanças de semente, precisão e plataforma;
5. código, parâmetros e resultados forem preservados como artefatos.

## 5. Protocolo para Ω = 23,158

Registrar obrigatoriamente:

- definição de `Ω`;
- unidade ou declaração adimensional;
- método de normalização;
- condições iniciais;
- número de iterações e descarte transitório;
- estimador usado;
- média, desvio e intervalo de confiança;
- sensibilidade a parâmetros;
- comparação com modelos nulos.

### Falsificador direto

A hipótese de atrator é rejeitada quando houver conjunto não desprezível de condições iniciais no domínio declarado que:

- não convirja;
- convirja para outro valor;
- apresente divergência persistente superior à tolerância;
- dependa de precisão numérica sem estabilidade de refinamento.

## 6. Protocolo para `√3/2`

A matriz de rotação de 30° é

\[
R=
\begin{bmatrix}
\sqrt{3}/2 & -1/2\\
1/2 & \sqrt{3}/2
\end{bmatrix}.
\]

Como `RᵀR=I`, ela preserva norma. Portanto, toda documentação deve separar:

- **coeficiente angular:** `cos(30°)=√3/2`;
- **fator dinâmico:** `κ`, usado para contrair ou expandir;
- **expoente de Lyapunov:** calculado a partir da dinâmica completa.

Para o mapa linear `xₙ₊₁=κRxₙ`, o expoente máximo é `log|κ|`. Isso não autoriza extrapolação para decaimento bariônico, cosmologia ou outra física sem derivação e dados próprios.

## 7. Protocolo de software

Cada implementação deve publicar:

- compilador e versão;
- arquitetura e ABI;
- flags;
- representação numérica;
- política de overflow;
- vetor de testes;
- checksum dos artefatos;
- sementes;
- tolerâncias;
- saída bruta e resumo derivado.

### Testes mínimos

1. enumeração dos oito trigramas;
2. `ROR3(ROL3(x))=x` para todo `x∈[0,7]`;
3. `ROL3(ROR3(x))=x` para todo `x∈[0,7]`;
4. erro de norma da rotação Q15;
5. comportamento para `κ<1`, `κ=1` e `κ>1`;
6. determinismo do estado de auditoria;
7. teste cruzado ARMv7, AArch64 e host de referência quando disponíveis.

## 8. Fronteira física

Código que compila demonstra consistência de implementação, não validade de uma teoria física.

Uma afirmação física exige:

\[
\text{modelo}\rightarrow\text{observável}\rightarrow\text{previsão}
\rightarrow\text{medição}\rightarrow\text{comparação}.
\]

Sem observável e instrumento, o resultado deve permanecer classificado como matemática, simulação ou ontologia computacional.

## 9. Estados epistêmicos permitidos

- `SYMBOLIC`: linguagem e analogia;
- `DEFINED`: objetos e operações formalizados;
- `PROVED_LOCAL`: propriedade matemática demonstrada no modelo;
- `IMPLEMENTED`: código executável disponível;
- `NUMERICALLY_OBSERVED`: resultado numérico ainda dependente do protocolo;
- `REPRODUCED`: repetido de forma independente;
- `PHYSICAL_HYPOTHESIS`: possui observável e previsão;
- `EMPIRICALLY_SUPPORTED`: passou por confronto experimental;
- `FALSIFIED`: falhou em critério pré-registrado;
- `TOKEN_VAZIO`: informação necessária ainda ausente.

## 10. Artefatos esperados

```text
artifacts/bagua_t7/
├── manifest.json
├── parameters.json
├── build.txt
├── vectors.csv
├── orbit_catalog.csv
├── jacobians/
├── stability_report.json
├── omega_convergence.csv
├── checksums.sha256
└── README.md
```

## 11. Resultado do contrato

O valor científico desta arquitetura nasce da separação disciplinada:

- Bagua e Tao: ontologia e linguagem estrutural;
- bits, matrizes e `T⁷`: objetos formais;
- C/ASM: implementação;
- 42 órbitas e `Ω=23,158`: hipóteses registradas;
- medições reproduzíveis: possível evidência futura.

**F_ok:** existe uma ponte legítima entre símbolos, estados discretos e álgebra linear.  
**F_gap:** as alegações orbitais e físicas ainda não possuem protocolo completo de evidência.  
**F_next:** executar o catálogo orbital, publicar Jacobianos e comparar contra modelos nulos.
