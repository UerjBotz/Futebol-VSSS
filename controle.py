from math  import pi, sin, cos
from cmath import polar, phase
from time  import time

from typing import Final, TypeIs, Iterator

import transmissor


## constantes e tipos
type pos  = tuple[float, float]
type posi = tuple[int, int]
type vel  = tuple[int, int]

VEL_MAX:    Final[int] = 100#!%(range superior pro envio)
DIST_BLOCO: Final[int] = 100#mm #! usar o tamanho de célula da grade


## funções utilitárias
def clamp[Num](val: Num, MIN: Num, MAX: Num) -> Num:
    return min(MAX, max(MIN, val))

def dist(a: pos, b: pos) -> float:
    x0, y0 = a; x1, y1 = b
    return ((x0-x1)**2 + (y0-y1)**2)**0.5

def none(obj: object | None) -> TypeIs[None]:
    return obj is None
def some(obj: object | None) -> TypeIs[object]: #! talvez inclua. :. bool?
    return not none(obj)


## modelagem do robô
_eixo: Final = 68.3 #mm
_diam: Final = 34.5 #mm
_circ: Final = pi*_diam #mm
_rpm : Final = 500 #rpm #! checar nos motores

hz   = lambda rpm: rpm/60       # rpm -> rot/s | Hz
rads = lambda rpm: 2*pi*hz(rpm) # rpm -> rad/s

_freq: Final = hz(rpm) #Hz
rot_para_dist = lambda freq, dt: freq*_circ*dt # rot/s -> s -> mm
# -> dist = freq*_circ*dt
# -> 1/dt = freq*_circ/dist
# -> dt = dist/(freq*_circ) ->
dist_para_tempo = lambda ds: ds/(_freq*_circ) # mm -> s #! usar vel (converter)

ang_para_tempo = lambda delta_ang: 1 #! fazer direito
ang_para_vel = lambda delta_ang: (-_freq,  _freq) if delta_ang < 0 else \
                                 ( _freq, -_freq) #! lidar com tempo


## "controle" atual
def movedor(robo: int, espera: float=0, vels: vel=(0,0)): #! tipos(gerador)
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

def girar(mov, vel: int, ang: float):
    mov.send((ang_para_tempo(ang), ang_para_vel(vel, ang)))

def avançar_por(mov, vel: int, *, tempo: float=1):
    mov.send((tempo, (vel, vel)))

def avançar_dist(mov, vel: int, *, dist: float=1):
    avançar_por(mov, vel, dist_para_tempo(dist)) #! usar vel (converter)

def avançar_um_bloco(mov, vel: int):
    avançar_dist(mov, vel, TAM_BLOCO)


## pid (não usado ainda, adaptado do controle_luis
I_MAX   = 300
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

