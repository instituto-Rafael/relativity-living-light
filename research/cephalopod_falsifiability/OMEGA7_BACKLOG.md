# Ω7 — Registro de hipóteses esquecidas, abortadas e antiderivadas
Estado: PROPOSTO; não é descoberta, nem alegação de causalidade.
Vinculado ao PR #1136. Escopo: cefalópodes, genômica comparativa, biofísica,
química molecular, desenvolvimento, biomedicina e epistemologia.

## Sete direções DISTINTAS (não equivalentes)
D1 ORIGEM: homologia genética/filogenia; controle: convergência morfológica.
D2 MECANISMO: proteínas, organelas, metabolismo e eletroquímica; controle: correlação sem mecanismo.
D3 ESCALA: átomo→molécula→célula→tecido→organismo; controle: extrapolação entre escalas.
D4 TEMPO: milissegundos→ontogenia→evolução; controle: confundir contração com crescimento.
D5 CAUSALIDADE: intervenção, contrafactual e confundidores; controle: associação espúria.
D6 CONTEXTO: ambiente, microbioma, simbiose, cultura de laboratório e viés amostral; controle: transferência de contexto.
D7 EPISTEMOLOGIA ADVERSARIAL: nulos, antiderivações, alternativas, limites físicos e replicação; controle: hipótese impossível.

## Estados que NÃO podem desaparecer
OMITIDO (não avaliado); ESQUECIDO (perdido do inventário); SUGERIDO (não priorizado);
IGNORADO (sem justificativa); OBVIO_NAO_TESTADO; MENOSPREZADO (descartado sem evidência);
ABORTADO (interrompido, com causa); ANTIDERIVADO (consequência invertida ou
negação derivada explicitamente); REFUTADO; INCONCLUSIVO; TOKEN_VAZIO.
Esses estados descrevem o processo, não a verdade biológica.

## Backlog recuperado e falsificadores
| ID | Direção | Hipótese ou lacuna | Teste refutador |
|---|---|---|---|
| G01 | D1 | pelo e tricoma são homólogos | filogenia e reguladores do desenvolvimento |
| G02 | D1 | cílio e flagelo bacteriano têm ancestral estrutural direto | ortologia e arquitetura do motor |
| G03 | D1 | suckerina, queratina e quitina são equivalentes | química, sequência e estrutura |
| G04 | D2 | melanina fúngica converte radiação em energia útil | balanço energético com controles de radiação |
| G05 | D2 | Golgi tem genoma endossimbiótico | sequenciamento, evidência de genoma próprio |
| G06 | D2 | neurotransmissão é puramente elétrica | farmacologia e registro eletrofisiológico |
| G07 | D3 | cromatóforos sobrepostos explicam todo padrão óptico | microscopia + iridóforos/leucóforos |
| G08 | D3 | aparência de filamento basta para homologia | estruturas convergentes como negativos |
| G09 | D4 | aumento de área pigmentada exige crescimento celular | vídeo de expansão em segundos |
| G10 | D4 | aprendizado de arrepio cria novos nervos motores | anatomia longitudinal e controle autonômico |
| G11 | D5 | relaxamento lento implica osmose como causa única | bloqueios farmacológicos e dinâmica de cálcio |
| G12 | D5 | pupila voluntária implica comando direto de todo músculo liso | neuroimagem, autonomismo e controles |
| G13 | D6 | efeitos de fungos melanizados independem do meio | meios nutritivos e doses comparáveis |
| G14 | D6 | camuflagem é invariante à luz e escala do substrato | estímulos cruzados e contrabalançados |
| G15 | D7 | qualquer correlação multiescalar prova uma lei universal | permutações, nulos e validação externa |
| G16 | D7 | antiderivação: negar uma consequência invalida toda premissa | testar lógica, condições necessárias/suficientes |
| G17 | D7 | hipóteses absurdas devem ser rejeitadas pelo mesmo gate | inserir controles impossíveis pré-registrados |
| G18 | D7 | sobrevivência a testes equivale a prova definitiva | replicação adversarial independente |

## Esquema mínimo de cada entrada
id, direcao, estado, enunciado, origem, evidencia_positiva, evidencia_negativa,
refutador, controle, dados, licenca, versao, responsavel, data, proxima_acao.
Nenhuma ausência é zero: usar TOKEN_VAZIO com motivo.
## Critério de aceitação
Cobertura de D1..D7; todo item com refutador; estados preservados;
nenhum resultado de fixture sintética como prova; CI e execução real separados.
## Fronteiras
Não executar intervenções humanas/animais nem experimentos de radiação sem
aprovações institucionais, biossegurança e ética. Respeitar privacidade,
licenças, proveniência e direito de revisão independente.
