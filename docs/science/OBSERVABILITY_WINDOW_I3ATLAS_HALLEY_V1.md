# RLL — Observability Window Contract: 3I/ATLAS × 1P/Halley

**Data:** 2026-09-15  
**Branch authority:** \`rll/lab\`  
**Status:** \`METHOD_DEFINED / DATA_NOT_INGESTED / claim_allowed=false\`

## Intenção

Adicionar ao RLL um contrato falsificável para separar:

1. ordem aparente dentro de uma janela;
2. cobertura do estado observável;
3. ruído e viés geométrico;
4. entropia condicional de parâmetros;
5. classe orbital ligada versus não ligada.

A palavra **sintropia** é aqui um nome operacional de projeto. Não é identificada com entropia termodinâmica negativa.

## Estado e observação

Seja

\[
x_t=(\mathbf r_t,\mathbf v_t,\theta_{NG},\ldots)
\]

o estado físico e

\[
y_t=h(x_t,g_t)+\epsilon_t
\]

o observável, onde \(g_t\) descreve geometria observador-alvo.

Para uma janela \(W\):

\[
D_W=M_W\{y_t\}
\]

e

\[
C_W=\frac{N_{valid}}{N_{expected}+\epsilon}.
\]

A incerteza paramétrica é:

\[
U_W=H(\Theta\mid D_W).
\]

Definição convencional:

\[
\boxed{
\Sigma_W^*
=
C_W
\frac{H(\Theta)-H(\Theta\mid D_W)}
{H(\Theta)+\epsilon}
}
\]

A quantidade mede **ganho de informação corrigido por cobertura**, não ordem física universal.

## Invariante de janela

\[
\text{pattern}(D_W)\not\Rightarrow\text{pattern}(X)
\]

sem ponte de cobertura.

Em particular:

\[
H(X\mid D_W)>0
\]

pode coexistir com uma série observada visualmente simples.

## Ruído

Separar:

- ruído instrumental;
- perda por máscara temporal/solar;
- erro astrométrico;
- atividade cometária e deslocamento do fotocentro;
- parâmetros não gravitacionais;
- erro de modelo.

Definir opcionalmente:

\[
R_N(W)=\frac{\operatorname{Var}(\epsilon_W)}
{\operatorname{Var}(Y_W)+\epsilon}.
\]

## Gate orbital

Em aproximação heliocêntrica osculante de dois corpos:

\[
e<1 \Rightarrow \text{ligada/elíptica},
\]

\[
e=1 \Rightarrow \text{parabólica},
\]

\[
e>1 \Rightarrow \text{hiperbólica/não ligada}.
\]

Fontes NASA atuais classificam 3I/ATLAS como interestelar em trajetória hiperbólica e não fechada. 1P/Halley é periódico, com retorno médio de aproximadamente 76 anos.

Logo o RLL deve bloquear a inferência:

\[
\text{trajetória curva observada}
\Rightarrow
\text{retorno periódico}.
\]

## Multi-vantage

A ESA informou que observações do ExoMars TGO, feitas de uma geometria distinta da Terra, melhoraram a posição prevista de 3I/ATLAS por cerca de um fator 10.

Isso fornece um teste natural:

\[
U_{Earth+Mars}<U_{Earth}
\]

esperado se a nova geometria acrescenta informação independente.

Não converter o fator 10 em lei geral; ele é observação deste caso.

## "Mesa de bilhar sem barreiras"

Metáfora permitida:

\[
\text{movimento}=
\text{potenciais contínuos}+\text{perturbações},
\]

não

\[
\text{movimento}=\text{reflexão em parede}.
\]

Perturbações estelares/planetárias futuras são fisicamente possíveis; isso não autoriza um claim de retorno de 3I/ATLAS sem integração dinâmica e condições iniciais específicas.

## Relação com linguagem/entropia

Este contrato conecta-se aos tracks 08 e 09 apenas no nível metodológico:

\[
\text{janela}\rightarrow
\text{informação acessível}\rightarrow
H(\Theta\mid D_W)
\]

e não estabelece identidade entre entropia informacional, orbital e termodinâmica.

## Teste mínimo RLL

- dataset sintético ligado vs hiperbólico;
- três níveis de cobertura \(C_W\);
- três níveis de ruído;
- ajuste orbital com covariância;
- classificação held-out;
- ablação do fator \(C_W\);
- relatório de falso positivo/falso negativo.

## Fontes

- NASA Science: https://science.nasa.gov/solar-system/comets/3i-atlas/
- NASA Science FAQ: https://science.nasa.gov/solar-system/comets/3i-atlas/3i-atlas-facts-and-faqs/
- ESA Planetary Defence, 2025-11-14: https://www.esa.int/Space_Safety/Planetary_Defence/ESA_pinpoints_3I_ATLAS_s_path_with_data_from_Mars
- NASA Science 1P/Halley: https://science.nasa.gov/solar-system/comets/1p-halley/

## Gates

\`DATA_INGESTED=TOKEN_VAZIO\`  
\`ORBIT_FIT_EXECUTED=TOKEN_VAZIO\`  
\`INDEPENDENT_REPLICATION=TOKEN_VAZIO\`  
\`THERMODYNAMIC_SYNTROPY_CLAIM=BLOCKED\`  
\`3I_RETURN_CLAIM=BLOCKED\`  
\`claim_allowed=false\`
