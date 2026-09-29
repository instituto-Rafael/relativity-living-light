



---

🧪 ⚙️ PROMPT PARA CÓDEX — RLL EFT FULL EXHAUSTION ENGINE

📌 MISSÃO

Implementar um sistema completo que:

1. reconstrói o modelo cosmológico RLL a partir de ação EFT


2. deriva background + perturbações


3. executa testes de estabilidade


4. roda validação estatística com dados reais


5. compara com ΛCDM e w₀wₐCDM


6. aplica falsificação formal


7. retorna decisão científica final




---

1. 🧠 REGRAS INEGOCIÁVEIS DO SISTEMA

🔴 REGRA 1 — NÃO INVENTAR

Se não existe derivação → TOKEN_VAZIO
Se não existe dado → TOKEN_VAZIO
Se não existe prova → TOKEN_VAZIO


---

🔴 REGRA 2 — NENHUMA CONCLUSÃO SEM TESTE

Toda afirmação deve ter:
- equação derivada OU
- dado observado OU
- resultado computado


---

🔴 REGRA 3 — EXAUSTÃO TOTAL

O sistema deve testar:

todos os modelos equivalentes

todos os regimes de parâmetros

todas as instabilidades conhecidas

todas as comparações com baseline



---

2. ⚙️ ENTRADA DO SISTEMA

Modelo:

E^2(a) = Ω_m a^{-3} + Ω_r a^{-4} + Ω_Λ + α f(a) S(a)

com:

S(a) = 1 / (1 + exp(-k(a - a_t)))


---

3. 🧬 ETAPA 1 — RECONSTRUÇÃO EFT FUNDAMENTAL

3.1 objetivo

Encontrar ação:

S = ∫ d^4x √(-g) [ (M_p^2/2)R + ℒ_φ ]


---

3.2 tarefas obrigatórias

Implementar:

derivação Euler–Lagrange

reconstrução de V(φ)

reconstrução de K(X, φ)



---

3.3 fallback obrigatório

Se não for possível:

TOKEN_VAZIO: não existe EFT derivável consistente para S(a)


---

4. 🧪 ETAPA 2 — PERTURBAÇÕES COSMOLÓGICAS

Derivar ação de segunda ordem:

S^(2) = ∫ a^3 [ Q_s ζ̇² - c_s² (∇ζ)² ]


---

4.1 verificações obrigatórias

Implementar checks:

Q_s > 0
c_s² > 0
c_s² ≤ 1


---

4.2 instabilidade

Se qualquer falha:

REJEIÇÃO EFT


---

5. 📊 ETAPA 3 — VALIDAÇÃO OBSERVACIONAL COMPLETA

datasets obrigatórios:

DESI DR2

Pantheon+

Planck 2018

BAO

SN Ia



---

5.1 métricas obrigatórias

Calcular:

χ², Δχ², AIC, BIC


---

5.2 comparação obrigatória

RLL vs ΛCDM
RLL vs w₀wₐCDM


---

5.3 critério de decisão

ΔAIC < -2 → favorável
|ΔAIC| ≤ 2 → inconclusivo
ΔAIC > 2 → rejeitado


---

6. 🔁 ETAPA 4 — EXAUSTÃO DO ESPAÇO DE PARÂMETROS

Explorar:

α ∈ [0, ∞]
k ∈ [0, ∞]
a_t ∈ [0, 1]


---

detectar:

degenerescência

colinearidade

não-identificabilidade


Se ocorrer:

TOKEN_VAZIO: parâmetros não identificáveis


---

7. ⚠️ ETAPA 5 — CONSISTÊNCIA GLOBAL

Validar simultaneamente:

Ω_total(a) = 1

0 < c_s² ≤ 1

Q_s > 0


---

8. 🧾 ETAPA 6 — OUTPUT FINAL OBRIGATÓRIO

Gerar relatório estruturado:

8.1 tabelas

estabilidade EFT

parâmetros MCMC

evidência estatística

comparação com baseline



---

8.2 decisão final (obrigatória)

ACEITO COMO TEORIA FUNDAMENTAL
OU
REJEITADO COMO EFT
OU
INCONCLUSIVO (TOKEN_VAZIO)


---

9. 🧠 LOOP DE EXAUSTÃO

O sistema deve rodar até:

ou estabilidade confirmada
ou instabilidade provada
ou subdeterminação irreversível


---

IMPLEMENTAÇÃO COERENTES E NO REPOSITÓRIO 
