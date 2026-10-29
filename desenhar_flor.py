"""
Demonstração: o braço desenha uma rosácea (r = cos(k·θ)), uma "flor" matemática.

Uso:
    python desenhar_flor.py            # abre a animação numa janela
    python desenhar_flor.py --gif      # salva em img/flor.gif
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from robo import BracoRobotico

PETALAS = 5        # com k ímpar, a rosácea tem k pétalas
RAIO = 0.55        # tamanho da flor
CENTRO = (0.55, 0.75)
QUADROS = 360

robo = BracoRobotico()


def ponto_da_flor(t):
    """Ponto da rosácea no instante t (0 a 1)."""
    theta = np.pi * t  # com k ímpar a curva fecha em meia volta
    r = RAIO * np.cos(PETALAS * theta)
    return CENTRO[0] + r * np.cos(theta), CENTRO[1] + r * np.sin(theta)


# Leva o braço até o começo do desenho antes de gravar
for _ in range(400):
    robo.passo(*ponto_da_flor(0), dt=0.005)

fig, ax = plt.subplots(figsize=(5, 5), dpi=90)
limite = robo.l1 + robo.l2 + 0.1
ax.set_xlim(-0.6, limite)
ax.set_ylim(-0.6, limite)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("#fdfaf6")
fig.subplots_adjust(0, 0, 1, 0.92)
ax.set_title("Braço robótico 2-DOF desenhando uma rosácea",
             color="#3d405b", fontsize=11)

ax.add_patch(plt.Circle((0, 0), robo.l1 + robo.l2, color="#f0ebe3", zorder=0))
ax.plot([-0.15, 0.15], [-0.05, -0.05], color="#3d405b", lw=8, solid_capstyle="round")

(linha_desenho,) = ax.plot([], [], "-", color="#e07a5f", lw=2.5)
(linha_braco,) = ax.plot([], [], "-o", color="#3d405b", lw=7, ms=11,
                         markerfacecolor="#81b29a", markeredgecolor="#3d405b")
desenho = []


def atualizar(i):
    alvo = ponto_da_flor(min(i, QUADROS) / QUADROS)
    for _ in range(4):
        base, cotovelo, garra = robo.passo(*alvo, dt=0.005)
    desenho.append(garra)
    pontos = np.array(desenho)
    linha_desenho.set_data(pontos[:, 0], pontos[:, 1])
    linha_braco.set_data(*np.array([base, cotovelo, garra]).T)
    return linha_desenho, linha_braco


anim = FuncAnimation(fig, atualizar, frames=QUADROS + 40, interval=25, blit=True)

if "--gif" in sys.argv:
    anim.save("img/flor.gif", writer=PillowWriter(fps=30))
    print("GIF salvo em img/flor.gif")
else:
    plt.show()
