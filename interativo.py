"""
Modo interativo: o braço robótico segue o mouse em tempo real.

Uso:
    python interativo.py

Mova o mouse dentro da janela. O anel cinza é a área de trabalho:
os pontos que a garra consegue alcançar.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from robo import BracoRobotico

robo = BracoRobotico()
alvo = list(robo.posicoes()[2])
rastro = []

fig, ax = plt.subplots(figsize=(7, 7))
fig.canvas.manager.set_window_title("Braço Robótico 2-DOF")
limite = robo.l1 + robo.l2 + 0.2
ax.set_xlim(-limite, limite)
ax.set_ylim(-limite, limite)
ax.set_aspect("equal")
ax.set_title("Mova o mouse: a garra vai atrás")
ax.grid(alpha=0.2)

# Área de trabalho
ax.add_patch(plt.Circle((0, 0), robo.l1 + robo.l2, color="0.85", zorder=0))
ax.add_patch(plt.Circle((0, 0), abs(robo.l1 - robo.l2), color="white", zorder=0))

(linha_rastro,) = ax.plot([], [], "-", color="#e07a5f", lw=1.5, alpha=0.6)
(linha_braco,) = ax.plot([], [], "-o", color="#3d405b", lw=6, ms=12,
                         markerfacecolor="#81b29a")
(ponto_alvo,) = ax.plot([], [], "x", color="#e07a5f", ms=12, mew=2)
texto = ax.text(-limite + 0.1, limite - 0.25, "", family="monospace")


def ao_mover_mouse(evento):
    if evento.inaxes == ax:
        alvo[0], alvo[1] = evento.xdata, evento.ydata


def atualizar(_):
    for _ in range(4):  # 4 sub-passos por quadro deixam a física mais estável
        base, cotovelo, garra = robo.passo(*alvo, dt=0.005)

    rastro.append(garra)
    del rastro[:-150]
    pontos = np.array(rastro)

    linha_braco.set_data(*np.array([base, cotovelo, garra]).T)
    linha_rastro.set_data(pontos[:, 0], pontos[:, 1])
    ponto_alvo.set_data([alvo[0]], [alvo[1]])
    q1, q2 = np.degrees(robo.q)
    texto.set_text(f"ombro:    {q1:7.1f}°\ncotovelo: {q2:7.1f}°")
    return linha_braco, linha_rastro, ponto_alvo, texto


fig.canvas.mpl_connect("motion_notify_event", ao_mover_mouse)
anim = FuncAnimation(fig, atualizar, interval=20, blit=True, cache_frame_data=False)
plt.show()
