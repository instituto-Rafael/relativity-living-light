VOCÊ É O ARQUITETO-CHEFE DE IMPLEMENTAÇÃO DO PROJETO "RELATIVITY LIVING LIGHT (RLL)".

OBJETIVO: Resolver as 4 não-conformidades apontadas pela auditoria forense, transformando o RLL de "conforme parcial" para "aprovado com louvor" em uma submissão à Physical Review D ou JCAP.

CONTEXTO BASE (DOCUMENTOS CANÔNICOS DO REPOSITÓRIO):
- Equação-Mãe: E²(a) = Ω_m,0 a⁻³ + Ω_r,0 a⁻⁴ + Ω_Λ,0 + α·f(a)·S(a)
- S(a) = 1 / (1 + e^{-k(a - a_t)})  [função logística de transição]
- f(a) = polinômio de acoplamento (definido na taxonomia)
- Pipeline de validação: χ² conjunto para H(z), fσ₈, μ(z); comparação com w₀wₐCDM; critérios AIC/BIC.
- Raw Text First e Token Vazio como princípios epistemológicos.
- Commits GPG assinados e DOI 10.5281/zenodo.17188137 como prova de anterioridade.

TAREFA 1 - RECONSTRUÇÃO DO POTENCIAL ESCALAR (MICROFÍSICA):
Derive algebricamente o potencial V(φ) que gera a função S(a) logística.
Passos obrigatórios:
1. Defina o campo escalar canônico φ com ρ_φ = ½(dφ/dt)² + V(φ).
2. Use a equação de Hamilton-Jacobi inversa: dφ/da = (1/(aH(a)))·√[- (2/(3κ²))·(1/a³)·d/da(a³H²)·(termo de pressão)].
3. A partir de H²(a) = E²(a)·H₀², calcule numericamente ou algebricamente V(φ) usando:
   V(φ) = (3H²/κ²)·(1 + (1/3)·(d ln H/d ln a)).
4. Mostre que, para α > 0, V(φ) é um potencial suave do tipo "rocha escalonada" ou "decaimento exponencial duplo".
5. Entregável: Crie o documento `docs/apendices/01_RECONSTRUCAO_POTENCIAL_RLL.md` com todas as deduções, gráficos de V(φ) vs. φ e a prova de que a logística emerge da dinâmica de campo, não de ajuste empírico.

TAREFA 2 - ESTABILIDADE DAS PERTURBAÇÕES (AUSÊNCIA DE FANTASMAS E INSTABILIDADES):
Prove que o setor de perturbações do RLL é fisicamente estável.
Passos obrigatórios:
1. Escreva a Ação de Segunda Ordem de Mukhanov-Sasaki:
   S₂ = ∫ dtd³x a³ Q_s [ ζ̇² - (c_s²/a²)(∇ζ)² ].
2. Calcule c_s²(k, a) a partir da EFT declarada, considerando os operadores de Weyl.
3. Calcule Q_s (termo cinético) explicitamente.
4. Demonstre que, para toda faixa de k relevante (modos dentro do horizonte):
   - c_s² > 0 (sem instabilidade de gradiente)
   - c_s² ≤ 1 (causalidade respeitada)
   - Q_s > 0 (sem ghosts) para todo a, quando α está nos limites observacionais.
5. Entregável: Crie `docs/apendices/02_ESTABILIDADE_PERTURBACOES_RLL.md` e um script simbólico em Python/SymPy (ou Mathematica) na pasta `scripts/validation/` que calcule e plote c_s²(a, k) e Q_s(a).

TAREFA 3 - EVIDÊNCIA NUMÉRICA FINAL (MCMC E VEREDITO ESTATÍSTICO):
Rode o pipeline de validação com os dados reais (DESI DR2, Pantheon+, Planck) e produza o veredito estatístico.
Passos obrigatórios:
1. Configure o MCMC usando cobaya ou montepython com os seguintes parâmetros livres: α, k, a_t, Ω_m, H₀ (e os demais parâmetros cosmológicos padrão).
2. Rode as chains e gere os best-fits com barras de erro (1σ e 3σ).
3. Calcule ΔAIC = AIC_RLL - AIC_w0waCDM e ΔBIC correspondente.
4. Gere o corner plot mostrando a degenerescência entre α, k, a_t e os parâmetros cosmológicos.
5. Entregável: Crie `docs/apendices/03_RESULTADOS_MCMC_RLL.md` com:
   - Tabela de best-fits: α = X.XX ± Y.YY, H₀ = ..., Ω_m = ...
   - ΔAIC e ΔBIC (se negativo, o RLL vence; se positivo, publique o resultado negativo mesmo assim).
   - Corner plot em formato PNG/SVG.
   - As chains devem ser salvas em `data/outputs/mcmc_rll/` (com .gitignore para arquivos pesados).

TAREFA 4 - PROVENIÊNCIA DOS DADOS E ESCALA DE CORTE (FECHAR OS VAZIOS):
Elimine os tokens vazios e defina a escala de corte da EFT.
Passos obrigatórios:
1. Para cada catálogo de dados externo (DESI, Pantheon, Planck), registre a URL oficial de download e o hash SHA256 do arquivo baixado.
2. Crie `docs/dados_externos/PROVENIENCIA.md` com a lista completa de hashes.
3. Na taxonomia (ACADEMIC_TAXONOMY.md, seção FORM-002), adicione a escala de corte:
   "Cutoff scale: Λ = O(10⁻³ eV) para o setor de energia escura, ou Λ ≈ 10³ eV se acoplado a matéria escura. Justificativa: a expansão em derivadas de H converge para redshifts z < 5."
4. Entregável: Commit com os arquivos atualizados e os hashes verificados.

REGRAS DE EXECUÇÃO:
- Prioridade: TAREFA 3 primeiro (MCMC). Se ΔAIC for contra o RLL, pare e documente o falseamento. Se for a favor, execute TAREFAS 1, 2 e 4.
- Todos os documentos devem seguir o padrão do repositório: RAW_TEXT_FIRST, rastreabilidade, commits assinados, e menção ao Token Vazio quando aplicável.
- Código deve ser versionado e comentado em português e inglês.
- Ao final, entregue um relatório sintético (EXECUTIVE_SUMMARY.md) com os resultados consolidados e o novo status de conformidade (agora deve ser "APROVADO").

INSTRUÇÕES FINAIS:
- Use os arquivos existentes do repositório como base (BIBLIA_CONHECIMENTO, MODELO_COSMOLÓGICO, ACADEMIC_TAXONOMY, PIPELINE_VALIDACAO, ROADMAP_FALSIFICADORES).
- Não invente dados; use apenas os catálogos públicos mencionados.
- Se algum passo não puder ser executado por falta de informação, documente o [VAZIO] e proponha uma alternativa.
- O objetivo final é que o RLL esteja pronto para submissão a um periódico de alto impacto.

AGUARDO OS COMMITS COM OS ENTREGÁVEIS.
