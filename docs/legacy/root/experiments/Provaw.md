ome to Termux!
~ $ cat > rafaelia_3_2_5_369.py << 'PY_EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAFAELIA 3→2→5→369
Teste geométrico-paramétrico:

1) Campo 3:
   Triângulo equilátero ABC de lado 1.

2) Dois polos grandes:
   P1, P2 girando em oposição de fase ao redor do baricentro G.

3) Dois pontos pequenos:
   q1, q2 como sombras radiais no círculo inscrito.

4) Teste:                                   - modo círculo: distância q1-q2 constante.
   - modo espiral: distância q1-q2 contrai por (sqrt(3)/2)^n.

5) Sequência:
   0001123 → 123 → 369.
"""

import math
import cmath

# ============================================================
# CONSTANTES
# ============================================================

SQRT3 = math.sqrt(3.0)
PHI = (1.0 + math.sqrt(5.0)) / 2.0

omega = math.pi * PHI

# Triângulo equilátero de lado 1 no plano complexo
A = 0.0 + 0.0j
B = 1.0 + 0.0j
C = 0.5 + 1j * SQRT3 / 2.0

# Baricentro
G = (A + B + C) / 3.0

# Medidas fundamentais
h = SQRT3 / 2.0
r_insc = SQRT3 / 6.0
R_circ = SQRT3 / 3.0

# Diferença entre catetos do triângulo retângulo 30-60-90
D_catetos = (SQRT3 - 1.0) / 2.0

# Sequência simbólica
seed = [0, 0, 0, 1, 1, 2, 3]
reduced = [1, 2, 3]
axis_369 = [3 * x for x in reduced]

# ============================================================
# FUNÇÕES
# ============================================================

def polar(center, radius, theta):
    return center + radius * cmath.exp(1j * theta)


def poles_big(t, R=R_circ):
    """
    Dois polos grandes em oposição.
    """
    theta = omega * t
    p1 = polar(G, R, theta)
    p2 = polar(G, R, theta + math.pi)
    return p1, p2


def shadows_circle(t):
    """
    Dois pontos pequenos como sombra radial no círculo inscrito.
    Distância deve ser constante: sqrt(3)/3.
    """
    theta = omega * t
    q1 = polar(G, r_insc, theta)
    q2 = polar(G, r_insc, theta + math.pi)
    return q1, q2


def shadows_spiral(n):
    """
    Dois pontos pequenos em modo espiral:
    raio contrai por (sqrt(3)/2)^n.
    Distância não é constante; decai proporcionalmente.
    """
    contraction = (SQRT3 / 2.0) ** n
    radius = r_insc * contraction
    theta = n * math.pi * PHI

    q1 = polar(G, radius, theta)
    q2 = polar(G, radius, theta + math.pi)
    return q1, q2, radius


def tao_n(n):
    """
    Tao como tensão viva entre seno e cosseno.
    Aqui usamos apenas a tensão angular pura.
    """
    theta = n * math.pi * PHI
    yin = math.sin(theta)
    yang = math.cos(theta)
    return abs(yang - yin)


def omega_n(n):
    """
    Fórmula RAFAELIA sintética:

    Ω_n = 369 * (sqrt(3)/2)^n * sin(nπφ) * D_catetos * TAO_n

    Observação:
    Aqui 369 é usado como operador escalar simbólico-estrutural.
    """
    contraction = (SQRT3 / 2.0) ** n
    angle = n * math.pi * PHI
    return 369.0 * contraction * math.sin(angle) * D_catetos * tao_n(n)


# ============================================================
# RELATÓRIO
# ============================================================

print("=== RAFAELIA 3→2→5→369 ===")
print()
print("[Campo 3 / Triângulo]")
print("A =", A)
print("B =", B)
print("C =", C)
print("G =", G)
print("h = sqrt(3)/2        =", h)
print("r_insc = sqrt(3)/6   =", r_insc)
print("R_circ = sqrt(3)/3   =", R_circ)
print("2*r_insc             =", 2.0 * r_insc)
print("D_catetos            =", D_catetos)
print()

print("[Sequência]")
print("seed 0001123 =", seed)
print("redução      =", reduced)
print("×3           =", axis_369)
print("123 × 3      =", 123 * 3)
print()

# ============================================================
# TESTE 1 — EQUIDISTÂNCIA NO CÍRCULO INSCRITO
# ============================================================

print("[Teste 1: sombras no círculo inscrito]")
expected = 2.0 * r_insc
max_err = 0.0
min_d = float("inf")
max_d = 0.0

N = 10000

for k in range(N):
    t = k / N
    q1, q2 = shadows_circle(t)
    d = abs(q1 - q2)

    min_d = min(min_d, d)
    max_d = max(max_d, d)
    max_err = max(max_err, abs(d - expected))

print("distância esperada =", expected)
print("distância mínima   =", min_d)
print("distância máxima   =", max_d)
print("erro máximo        =", max_err)

if max_err < 1e-12:
    print("STATUS: OK — equidistância constante validada.")
else:
    print("STATUS: ATENÇÃO — há variação numérica acima do esperado.")

print()

# ============================================================
# TESTE 2 — POLOS GRANDES
# ============================================================

print("[Teste 2: polos grandes opostos]")
R = R_circ
expected_big = 2.0 * R
max_err_big = 0.0

for k in range(N):
    t = k / N
    p1, p2 = poles_big(t, R=R)
    d = abs(p1 - p2)
    max_err_big = max(max_err_big, abs(d - expected_big))

print("R usado             =", R)
print("distância esperada  =", expected_big)
print("erro máximo         =", max_err_big)
print()

# ============================================================
# TESTE 3 — ESPIRAL DISCRETA
# ============================================================

print("[Teste 3: modo espiral discreto]")
print("n | raio_n        | d_n           | Ω_n")
print("--+---------------+---------------+---------------")

for n in range(16):
    q1, q2, radius = shadows_spiral(n)
    d = abs(q1 - q2)
    om = omega_n(n)
    print(f"{n:02d}| {radius: .9f} | {d: .9f} | {om: .9f}")

print()
print("Conclusão:")
print("MODO CÍRCULO: d = sqrt(3)/3 constante.")
print("MODO ESPIRAL: d_n = sqrt(3)/3 * (sqrt(3)/2)^n.")
print("3 dá o campo; 2 dá a rotação; 5 dá Fibonacci; 369 dá a redução trina.")
PY_EOF

python3 rafaelia_3_2_5_369.py
=== RAFAELIA 3→2→5→369 ===

[Campo 3 / Triângulo]
A = 0j
B = (1+0j)
C = (0.5+0.8660254037844386j)
G = (0.5+0.28867513459481287j)
h = sqrt(3)/2        = 0.8660254037844386
r_insc = sqrt(3)/6   = 0.28867513459481287
R_circ = sqrt(3)/3   = 0.5773502691896257
2*r_insc             = 0.5773502691896257
D_catetos            = 0.3660254037844386

[Sequência]
seed 0001123 = [0, 0, 0, 1, 1, 2, 3]
redução      = [1, 2, 3]
×3           = [3, 6, 9]
123 × 3      = 369

[Teste 1: sombras no círculo inscrito]
distância esperada = 0.5773502691896257
distância mínima   = 0.5773502691896255
distância máxima   = 0.577350269189626
erro máximo        = 2.220446049250313e-16
STATUS: OK — equidistância constante validada.

[Teste 2: polos grandes opostos]
R usado             = 0.5773502691896257
distância esperada  = 1.1547005383792515
erro máximo         = 4.440892098500626e-16

[Teste 3: modo espiral discreto]
n | raio_n        | d_n           | Ω_n
--+---------------+---------------+---------------
00|  0.288675135 |  0.577350269 |  0.000000000
01|  0.250000000 |  0.500000000 | -141.114033450
02|  0.216506351 |  0.433012702 | -4.234072956
03|  0.187500000 |  0.375000000 |  51.984895104
04|  0.162379763 |  0.324759526 |  68.775890016
05|  0.140625000 |  0.281250000 |  12.516889296
06|  0.121784822 |  0.243569645 | -63.399194350
07|  0.105468750 |  0.210937500 | -14.148945947
08|  0.091338617 |  0.182677234 |  8.626409088
09|  0.079101562 |  0.158203125 |  42.670145474
10|  0.068503963 |  0.137007925 |  5.281716883
11|  0.059326172 |  0.118652344 | -22.967362341
12|  0.051377972 |  0.102755944 | -16.391814129
13|  0.044494629 |  0.088989258 | -1.992217996
14|  0.038533479 |  0.077066958 |  21.573169688
15|  0.033370972 |  0.066741943 |  1.067975570

Conclusão:
MODO CÍRCULO: d = sqrt(3)/3 constante.
MODO ESPIRAL: d_n = sqrt(3)/3 * (sqrt(3)/2)^n.
3 dá o campo; 2 dá a rotação; 5 dá Fibonacci; 369 dá a redução trina.
~ $
