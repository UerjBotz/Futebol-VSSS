from math  import pi, sin, cos
from cmath import polar, phase
from time  import time

from typing import Callable, TypeIs

import transmissor


## tipos
type pos  = tuple[float, float]
type posi = tuple[int, int]
type vel  = tuple[int, int]


## funções utilitárias
def clamp(val, MIN, MAX):
    return min(MAX, max(MIN, I))

def dist(a: pos, b: pos) -> float:
    x0, y0 = a; x1, y1 = b
    return ((x0-x1)**2 + (y0-y1)**2)**0.5

def none(obj: object | None) -> TypeIs[None]:
    return obj is None
def some(obj: object | None) -> TypeIs[object]: #! talvez inclua. :. bool?
    return not none(obj)


## tentativas de modelagem do robô
_tam_eixo = 68.3  #mm
_diâmetro_roda = 34.5  #mm
R = _diâmetro_roda / 2
L = _tam_eixo

#vel_x = R*cos(angulo)*(vr+vl)/2; vel_y = R*sin(angulo)*(vr+vl)/2
#vel_angular = angulo

#vel_x = v*cos(angulo); vel_x = v*cos(angulo)
#vel_angular = R*(vr - vl)/L
# ->
vl = lambda v, ang: ((2*v) + (ang*L)) / 2 * R
vr = lambda v, ang: ((2*v) - (ang*L)) / 2 * R

ang_para_vel = lambda v, ang: (vl(v, ang), vr(v, ang))
raio_curva   = lambda vl, vr: (R/2)*(vr+vl)/(vr-vl)

_rpm  = 100 #(?)
_circ = 2*pi*R #mm
_freq = _rpm/60 #Hz
vel_max = _circ*_freq #mm/s


## "controle" atual
def movedor(robo: int, espera: float=0, vels: tuple[int, int]=(0,0)):
    t_ini: float = time()
    while True:
        terminado: bool = (time() - t_ini) >= espera
        if not terminado: transmissor.mover(*vels, robo=robo)
        else:             transmissor.mover(0, 0,  robo=robo)

        params = yield terminado
        if terminado and some(params):
            t_ini = time()
            espera, vels = params

def terminou_mov(mov):
    return mov.send(None)

def girar(mov, vel: int, ang: float, passo_tempo: float=1):
    mov.send((passo_tempo, ang_para_vel(vel, ang)))

def avançar_um_bloco(mov, vel: int, *, passo_tempo: float=1):
    mov.send((passo_tempo, (vel, vel)))


## pid (não usado ainda, adaptado do controle_luis
I_MAX   = 300
VEL_MAX = 100
def inicializar_pid(vel_padrão: int, *, kp: float, ki: float, kd: float,
                    VEL_MAX: int=VEL_MAX, I_MAX: float=I_MAX,
                    EPSILON: float=0.1): #! tipos (gerador)
    I = err_ang_ant = 0
    t_ant = time()

    def pid(atual: pos, alvo: pos, orientação: float, v=vel_padrão) -> vel:
        nonlocal I, t_ant, err_ang_ant
        x0, y0 = atual; x1, y1 = alvo

        t_agr = time()
        dt = t_agr - t_ant

        desloc = complex(x1 - x0, y1 - y0)
        err_ang = phase(desloc) - orientação

        #! if   (theta_erro > 0): theta_erro = theta_erro % pi ?
        #! elif (theta_erro < 0): theta_erro = -(abs(theta_erro) % pi) ?

        derr = err_ang - err_ang_ant

        P = kp * err_ang
        I = I + ki * err_ang * dt
        D = (kd / dt) * derr #! derr * kd * dt?

        I = clamp(I, -I_MAX, I_MAX)
        err_ang_ant = err_ang
        t_ant = t_agr

        dv = P + I + D
        vr = clamp(v - dv, -VEL_MAX, VEL_MAX)
        vl = clamp(v + dv, -VEL_MAX, VEL_MAX)
        vels = vl, vr

        return (0,0) if dist((0,0), vels) < EPSILON else vels
    
    def corrotina(): #! tipos (gerador)
        args = yield
        while True:
            args = yield pid(*args)

    return corrotina()

#https://www.cs.columbia.edu/~allen/F19/NOTES/icckinematics.pdf pg 4
def diferencial(original: pos, orientação: float,
                vels: tuple[float,float], duração: float,
                *, N_ITER = 1000) -> tuple[pos, float]:
    theta = orientação
    x, y  = original

    w = (1/R)*(vels[0]-vels[1])
    v = 0.5*(vels[0]+vels[1])

    dt = duração/N_ITER
    for i in range(N_ITER):
        theta += w*dt
        x += v*cos(theta)*dt
        y += v*sin(theta)*dt
    return (x, y), theta


## para testes de pid (falta parear com o do luis)
def simular(posição: pos, alvo: pos, orientação: float, *, EPSILON=0.1):
    import matplotlib.pyplot as plt
    tempo = 0.02
    xs = []; ys = []

    pid = inicializar_pid(800, kp=0.1, ki=0.2, kd=0.5)
    for i in range(100):
        x, y = posição
        xs.append(x)
        ys.append(y)
        vels = pid(posição, alvo, orientação)
        posição, orientação = diferencial(posição, orientação, vels, tempo)
        if (vels == (0,0)): break

    plt.plot(xs, ys)
    plt.show()

#if __name__ == "__main__":
#    # [versão script]

