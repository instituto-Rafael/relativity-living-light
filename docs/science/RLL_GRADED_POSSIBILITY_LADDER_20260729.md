# RLL — Escada Graduada de Possibilidades Teoria–Prática

**Status:** experimental shadow  
**Claim policy:** `claim_allowed=false`  
**Publication effect:** `NONE`

## Correção de arquitetura

A ciência não precisa esperar uma validação absoluta para registrar, comparar ou explorar uma hipótese. Ela precisa usar linguagem proporcional ao estado da evidência.

Existem dois ordenamentos independentes:

1. **Promoção científica:** segue dependência de evidência.
2. **Prioridade de exploração:** segue a menor distância atual entre teoria e prática.

Uma hipótese pode receber alta prioridade experimental sem ser chamada de verdadeira. Também pode permanecer teoricamente interessante depois de um resultado negativo, desde que seu escopo seja reduzido e o falsificador seja preservado.

## Escada

| Nível | Nome | Interpretação operacional |
|---|---|---|
| P5 | `NEAR_OPERATIONAL` | equação, observável, falsificador e rota executável já existem |
| P4 | `FORMALIZABLE_NEAR` | família teórica e observável existem; falta backend completo |
| P3 | `TESTABLE_HYPOTHESIS` | claim falsificável existe; falta fechamento ou implementação |
| P2 | `BRIDGE_CANDIDATE` | mecanismos existem em domínios distintos; falta ponte exclusiva |
| P1 | `SPECULATIVE_SEED` | semente coerente e referenciada; falta modelo específico |
| P0 | `UNRANKABLE_TOKEN_VAZIO` | ainda faltam identidade, escopo ou referência mínima |

O nível mede **tratabilidade atual**, não probabilidade de verdade.

## Método não compensatório

A classificação considera:

- proximidade da fonte;
- fechamento teórico;
- acesso ao observável;
- prontidão de implementação;
- clareza do falsificador;
- reprodução independente.

Uma média ponderada não pode esconder a ausência de uma dimensão obrigatória. Primeiro aplica-se o gargalo categórico. Dentro do mesmo nível, usa-se comparação de Pareto e registra-se explicitamente o bloqueador.

## Portfólio inicial

- **P5:** RLL de fundo — já possui equação, código, testes e observáveis; falta robustez multi-seed e replicação.
- **P4:** setor escuro interagente — família física e observáveis existem; falta selecionar e implementar uma interação covariante completa.
- **P4:** reconstrução não paramétrica — método e dados existem; falta congelar kernel, regularização e cobertura em mocks.
- **P2:** gravidade forte/plasma → cosmologia — mecanismos locais são físicos, mas falta operador de ponte e assinatura independente da fonte.
- **P1:** extensões genéricas de Einstein — a categoria é ampla demais; é necessário escolher uma família concreta antes de formalizar.

## Regra de linguagem

```text
alta prioridade de exploração != confirmação
baixa prioridade de exploração != refutação
TOKEN_VAZIO != zero
modelo útil != teoria final
resultado negativo != ausência de valor
```

O objetivo é permitir que pares identifiquem rapidamente:

- quais possibilidades já podem ser executadas;
- quais precisam de uma única ponte;
- quais ainda são sementes;
- qual artefato move cada item para o nível seguinte.

## Calibração associada

A escada P0–P5 agora é interligada ao contrato:

```text
data/contracts/theory_practice_calibration.v1.yml
```

A integração acrescenta uma terceira ordem independente:

```text
S0–S9  → promoção por dependência de evidência
P0–P5  → prioridade por proximidade teoria–prática
C0–C5  → maturidade da ligação teoria–execução–residual–recibo
```

Cada item do portfólio precisa possuir exatamente um perfil de calibração com seis deltas:

```text
escopo teórico → modelo específico
equação/algoritmo → código
observável → medição
parâmetro → configuração
previsão → recibo
falsificador → decisão
```

O validador cruzado bloqueia divergência entre o estado da fila, o nível de exploração e o perfil de calibração. Assim, uma alteração textual não consegue promover a hipótese, esconder um `TOKEN_VAZIO` ou declarar aproximação limitada sem recibo e decisão adversarial.
