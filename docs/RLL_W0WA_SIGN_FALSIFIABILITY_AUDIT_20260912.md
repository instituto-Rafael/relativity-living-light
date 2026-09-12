# RLL — Auditoria de sinal (w0, wa) e falsificabilidade · 2026-09-12

## Estado

**Conclusão segura:** a forma logística canônica atual do RLL possui uma restrição estrutural local importante: sob `Omega_s0 >= 0`, `Omega_Lambda >= 0` e `wt > 0`, o seu mapeamento tangente para coordenadas CPL em `a=1` satisfaz

```text
wa_eff >= 0
```

Isso cria uma **tensão estrutural de sinal** com ajustes externos que preferem valores centrais/posteriores de `wa < 0`. Ainda não autoriza declarar o RLL falsificado: o passo decisivo é um teste de sobreposição posterior com likelihood, priors e datasets explicitamente correspondentes.

## 1. Correção da derivação do setor RLL

A transição canônica é:

```text
f(z) = 1 / (1 + exp((z-zt)/wt)),  wt > 0
```

Para o setor de superposição:

```text
g(a) = f(a) + (1-f(a)) a^-3
w_s(a) = -f(a)/g(a)
```

Em `a=1`, `g(1)=1`, então:

```text
w0_s = -f0
```

Como `z=1/a-1`:

```text
df/da | a=1 = f0(1-f0)/wt
dg/da | a=1 = -3(1-f0)
```

Portanto:

```text
wa_s = -dw_s/da | a=1
     = f0(1-f0)(3 + 1/wt)
```

e **não** `3+2/wt`.

Para `0<f0<1` e `wt>0`, temos `wa_s>0`.

## 2. O comparador correto inclui Omega_Lambda

O código canônico já distingue o setor isolado do **setor escuro total**:

```text
w_dark(a) =
 -(Omega_Lambda + Omega_s0 f(a))
 /(Omega_Lambda + Omega_s0 g(a))
```

Logo:

```text
w0_eff =
 -(Omega_Lambda + Omega_s0 f0)
 /(Omega_Lambda + Omega_s0)
```

e:

```text
wa_eff =
 Omega_s0(1-f0)/(Omega_Lambda+Omega_s0)^2
 *
 [ f0(Omega_Lambda+Omega_s0)/wt
   + 3(Omega_Lambda+Omega_s0 f0) ]
```

Sob os bounds canônicos atuais, todos os fatores são não negativos:

```text
wa_eff >= 0
```

Se `Omega_s0=0`:

```text
w0_eff = -1
wa_eff = 0
```

e `zt,wt` tornam-se inativos/não identificáveis no background.

## 3. Correções ao texto recebido

### 3.1 O par 0.49, -1.52 tem identidade específica

A versão **peer-reviewed publicada** em JCAP 2026(06) 043, DOI `10.1088/1475-7516/2026/06/043`, reporta:

```text
w0 = -0.49 +/- 0.25
wa = -1.52 +/- 0.77
```

para **DESI DR1 Full-Shape + DESI DR2 BAO**.

Há uma discrepância de versão que precisa permanecer auditável: o abstract arXiv atualmente indexado para arXiv:2602.18761 mostra `w0=+0.49`, enquanto a versão publicada mostra `w0=-0.49`. Para benchmark, o RLL passa a usar a versão publicada e registra explicitamente a divergência em vez de apagá-la.

Portanto, nesse ponto específico, o texto recebido estava correto quanto ao sinal da versão publicada.

O estudo relata melhoria de aproximadamente 30% nas restrições em relação à análise análoga anterior e uma discrepância com LambdaCDM reduzida a cerca de 1.4 sigma no contexto descrito pelo próprio trabalho. Ele não é o mesmo produto científico que o DESI DR2 Results IV.

### 3.2 Atualização Ly-alpha full-shape de 2026

O DESI DR2 Results IV, arXiv:2607.27410, acrescenta informação full-shape/AP do Ly-alpha e reporta preferência por `w0waCDM` sobre LambdaCDM de aproximadamente 2.7 sigma para DESI+CMB e 3.2 sigma incluindo SN.

Portanto não há um número único e universal que os "dados DESI exigem" para `wa`.

### 3.3 Sistemáticas de SN

A revisão de Turyshev, arXiv:2602.05368, publicada em 26 de maio de 2026, caracteriza a preferência por energia escura evolutiva como dependente do dataset e particularmente sensível a resíduos de calibração/seleção de supernovas na escala de poucos `10^-2 mag`.

Isso reforça que o **sinal de um best-fit CPL é benchmark de tensão, não observável direto**.

## 4. Falsificabilidade: correção epistemológica

A frase "o RLL falha no teste de falsificabilidade porque implica wa>0" está invertida.

Uma restrição estrutural como:

```text
wa_eff >= 0
```

é justamente uma previsão arriscada e torna a forma canônica **mais falsificável**.

O fluxo correto é:

```text
previsao de sinal
 -> posterior externo
 -> teste de sobreposicao
 -> tensao/compatibilidade OU falsificacao no escopo declarado
```

Não se deve declarar falsificação usando somente um ponto central CPL.

## 5. TOKEN_VAZIO que agora importa

O gap operacional passa a ser:

```text
TOKEN_VAZIO_POSTERIOR_OVERLAP_RLL_WA_DOMAIN
```

Pergunta executável:

> Qual é a sobreposição posterior de uma análise DESI precisamente identificada com o domínio local 2D acessível ao RLL em `(w0_eff,wa_eff)`? `P(wa>=0|D)` é apenas um pré-gate 1D, não o teste decisivo.

Esse teste é de maior informação que introduzir imediatamente um novo parâmetro para permitir `wa<0`.

Modificar a logística **antes** desse teste seria uma extensão pós-hoc e deve permanecer bloqueado.

## 6. Mapeamento local não é equivalência global

O par `(w0_eff,wa_eff)` é a tangente local em `a=1`. Ele não prova que o background RLL é globalmente equivalente a um CPL com esses dois números.

Devem ser mantidos separados:

```text
LOCAL_CPL_MAP
GLOBAL_H_Z_DISTANCE_LIKELIHOOD
PERTURBATION_GROWTH_MODEL
```

Uma exclusão decisiva deve confrontar o domínio de previsões em observáveis e/ou provar que o mapeamento local usado é suficiente para o escopo de falsificação.

## 7. Licença != falsificabilidade

A licença RAFCODE customizada não possui identificador SPDX padrão/OSI no estado atual de governança do repositório. Isso pode criar fricção de reutilização e reprodução do software.

Mas:

```text
CUSTOM_LICENSE != NON_FALSIFIABLE
```

A testabilidade matemática das equações e a interoperabilidade jurídica do código são gates diferentes. O efeito jurídico completo permanece `TOKEN_VAZIO_QUALIFIED_LEGAL_REVIEW`.

## 8. Próximo experimento de maior informação

1. Fixar uma combinação externa, por exemplo DR1 Full-Shape + DR2 BAO ou DR2 BAO+CMB.
2. Para DR1 Full-Shape + DR2 BAO, usar como fonte de reprodução o suplemento público Zenodo DOI `10.5281/zenodo.18629072` (`paper_data.tar.gz`, MD5 `ff5e5ec8c844a36ffa30b93216a5c740`). A existência do pacote está confirmada; a identidade interna da chain `w0wa` continua `TOKEN_VAZIO_CHAIN_CONTENT_NOT_YET_INSPECTED` até inspeção.
3. Materializar a chain posterior exata e sua proveniência.
4. Calcular:
   - pré-gate: `P(wa>=0 | D)`;
   - gate decisivo: massa/HPD posterior que intersecta o domínio RLL 2D `(w0_eff,wa_eff)` amostrado sob os bounds canônicos;
   - massa HPD que intersecta o domínio RLL;
   - sensibilidade a SN on/off;
   - sensibilidade ao Ly-alpha full-shape 2026;
   - sensibilidade aos priors.
5. Em paralelo, comparar globalmente `H(z), D_M, D_H, mu(z)`.
6. Só depois decidir entre:
   - manter a logística canônica;
   - declarar a forma canônica falsificada naquele escopo;
   - propor uma extensão **pré-registrada**, penalizada por complexidade.

## R3

```text
F_ok   = teorema de sinal identificado; formula corrigida; bounds atuais implicam wa_eff>=0; divergencia arXiv/JCAP de w0 registrada e publicada priorizada.
F_gap  = TOKEN_VAZIO_CHAIN_CONTENT_NOT_YET_INSPECTED + TOKEN_VAZIO_POSTERIOR_OVERLAP_RLL_W0WA_DOMAIN; P(wa>=0) e apenas pre-gate; mapeamento CPL e local, nao equivalencia global.
F_next = cadeia posterior publica DESI -> massa em wa>=0 -> ablacões SN/Ly-alpha -> decisao fail-closed.
claim_allowed=false
```
