# Cefalopodes, genômica comparativa e falsificabilidade — protocolo RLL
Status: EXPERIMENTAL; claim_allowed=false. Independente da cosmologia RLL.
## Escopo
Comparar cromatóforos, papilas, pelos, tricomas, hifas, cílios e flagelos,
escamas, filamentos de cnidários, Golgi, mitocôndrias, cloroplastos,
melanina, reflectinas e suckerinas.
## Hipóteses adversariais
H1: todos os filamentos são homólogos — refutar com filogenias, arquitetura proteica
e controles negativos; semelhança de forma não é homologia.
H2: camuflagem depende exclusivamente de crescimento — refutar com séries temporais
de alterações rápidas no mesmo indivíduo.
H3: pigmentos usam o mesmo mecanismo energético — comparar espectroscopia,
fotofísica e balanços energéticos; absorção não prova conversão metabólica.
H4: papilas exigem disparo neural contínuo — testar manutenção de tensão após
interrupção controlada da estimulação em dados experimentais publicados.
H5: Golgi tem origem endossimbiótica equivalente a mitocôndria e cloroplasto —
comparar evidência filogenômica e genomas organelares.
H6: circuitos da pupila humana e cromatóforos são homólogos — exigir homologia
neuroanatômica e filogenética, não analogia funcional.
## Hierarquia de testes
1. Invariantes e entradas impossíveis; 2. controles negativos;
3. permutação; 4. validação fora da amostra; 5. filogenia com modelos
concorrentes; 6. análise de sensibilidade; 7. intervenção causal;
8. replicação independente; 9. tentativa de refutação adversarial;
10. revisão metodológica e ética.
## Limites
O script test_gates.py executa apenas os três primeiros níveis, em fixtures
sintéticas, e verifica o bloqueio de alegações. Não executa alinhamento de
sequências, experimentos animais, inferência causal nem validação biomédica.
Nenhum resultado sintético pode ser descrito como observação real.
## Aceitação
CI verde + artefato JSON + SHA256 = somente PASS estrutural.
Hipótese científica aceita provisoriamente somente após dados independentes,
pré-registro, controles e revisão. Falta de dados => TOKEN_VAZIO_UNMEASURED.
