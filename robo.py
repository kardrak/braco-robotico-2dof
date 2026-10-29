"""
Modelo de um braço robótico planar com 2 graus de liberdade (2-DOF).

Contém:
  - cinemática direta   (ângulos das juntas -> posição da garra)
  - cinemática inversa  (posição desejada -> ângulos das juntas)
  - controlador PD      (faz as juntas chegarem suavemente no alvo)
"""

import numpy as np


class BracoRobotico:
    def __init__(self, l1=1.0, l2=0.8, kp=40.0, kd=9.0):
        self.l1 = l1  # comprimento do "braço" (ombro -> cotovelo)
        self.l2 = l2  # comprimento do "antebraço" (cotovelo -> garra)

        # Ganhos do controlador PD
        self.kp = kp
        self.kd = kd

        # Estado das juntas: ângulo (rad) e velocidade angular (rad/s)
        self.q = np.array([np.pi / 2, -np.pi / 2])
        self.dq = np.zeros(2)

        # Alvo atual das juntas, guardado para manter a mesma configuração
        # (cotovelo para cima ou para baixo) entre um passo e outro
        self.q_alvo = self.q.copy()

    # ------------------------------------------------------------------
    # Cinemática direta
    # ------------------------------------------------------------------
    def posicoes(self, q=None):
        """Retorna as posições (x, y) da base, do cotovelo e da garra."""
        q1, q2 = self.q if q is None else q
        base = np.array([0.0, 0.0])
        cotovelo = base + self.l1 * np.array([np.cos(q1), np.sin(q1)])
        garra = cotovelo + self.l2 * np.array([np.cos(q1 + q2), np.sin(q1 + q2)])
        return base, cotovelo, garra

    # ------------------------------------------------------------------
    # Cinemática inversa (solução analítica pela lei dos cossenos)
    # ------------------------------------------------------------------
    def cinematica_inversa(self, x, y):
        """
        Calcula os ângulos (q1, q2) que levam a garra até (x, y).

        Existem duas soluções (cotovelo para cima / para baixo); escolhemos
        a mais próxima da configuração atual, para o braço não "dar cambalhota".
        Se o ponto estiver fora do alcance, o braço se estica na direção dele.
        """
        alcance_max = self.l1 + self.l2
        alcance_min = abs(self.l1 - self.l2)
        r = np.hypot(x, y)

        # Limita o alvo à área de trabalho (um anel entre alcance_min e alcance_max)
        if r > alcance_max:
            x, y = np.array([x, y]) * (alcance_max * 0.999 / r)
        elif r < alcance_min:
            if r == 0:
                x, y = alcance_min * 1.001, 0.0
            else:
                x, y = np.array([x, y]) * (alcance_min * 1.001 / r)

        cos_q2 = (x**2 + y**2 - self.l1**2 - self.l2**2) / (2 * self.l1 * self.l2)
        cos_q2 = np.clip(cos_q2, -1.0, 1.0)

        solucoes = []
        for sinal in (+1, -1):
            q2 = sinal * np.arccos(cos_q2)
            q1 = np.arctan2(y, x) - np.arctan2(
                self.l2 * np.sin(q2), self.l1 + self.l2 * np.cos(q2)
            )
            solucoes.append(np.array([q1, q2]))

        def distancia(q):
            # Diferença angular "dando a volta" corretamente em ±pi
            d = np.angle(np.exp(1j * (q - self.q_alvo)))
            return np.sum(d**2)

        return min(solucoes, key=distancia)

    # ------------------------------------------------------------------
    # Controle e simulação
    # ------------------------------------------------------------------
    def passo(self, x_alvo, y_alvo, dt=0.01):
        """Avança a simulação dt segundos perseguindo o ponto (x_alvo, y_alvo)."""
        self.q_alvo = self.cinematica_inversa(x_alvo, y_alvo)

        erro = np.angle(np.exp(1j * (self.q_alvo - self.q)))

        # Lei de controle PD: torque = Kp * erro - Kd * velocidade
        torque = self.kp * erro - self.kd * self.dq

        # Modelo simplificado: cada junta se comporta como uma inércia unitária
        self.dq += torque * dt
        self.q += self.dq * dt
        return self.posicoes()
