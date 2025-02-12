#!.venv/bin/python3

from math  import pi, tau, sin, cos
from cmath import phase
from time  import time

from typing import Final, Iterator
from comum  import *

import transmissor


## constantes e tipos
type posf = tuple[float, float]
type posi = tuple[int, int]
type vel  = tuple[int, int]

VEL_MAX:    Final[int] = 100#!%(range superior pro envio)
DIST_BLOCO: Final[int] = 100#mm #! usar o tamanho de célula da grade


## modelagem do robô
_eixo: Final = 62.9     #mm
_diam: Final = 33.7     #mm
_circ: Final = pi*_diam #mm
_rpm : Final = 200      #rpm #! checar valor melhor

hz   = lambda rpm: rpm/60       # rpm -> rot/s | Hz
rads = lambda rpm: 2*pi*hz(rpm) # rpm -> rad/s

_freq: Final = hz(_rpm) #Hz
rot_para_dist = lambda freq, dt: freq*_circ*dt # rot/s -> s -> mm
# -> dist = freq*_circ*dt
# -> 1/dt = freq*_circ/dist
# ->   dt = dist/(freq*_circ) ->
dist_para_tempo = lambda freq, ds: abs(ds/(freq*_circ)) # rot/s -> mm -> s

ang_para_tempo = lambda freq, dang: dist_para_tempo(freq, _circ*dang/tau)
               #^ rot/s -> rad -> s
ang_para_vel   = lambda vel,  dang: (-vel, vel) if dang < 0 else \
                                    ( vel,-vel)
               #^ vel -> rad -> (vel, vel)


## "controle" atual
def movedor(robô: Final[int]) -> Iterator: #! tipo melhor
    t_ini:  float = time()
    espera: float = 0
    vels:   vel   = (0, 0)
    while True:
        terminado: bool = (time() - t_ini) >= espera
        if not terminado: transmissor.mover(*vels, robô=robô)
        else:             transmissor.mover(0, 0,  robô=robô)

        params = yield terminado
        if terminado and some(params):
            t_ini = time()
            espera, vels = params

def terminou_mov(mov):
    return mov.send(None)
def espera_mov(mov):
    while not terminou_mov(mov): pass

def vel_para_freq(vel): return _freq*vel/VEL_MAX

def girar_por(mov, vel: int, tempo: float):
    mov.send(tempo, ang_para_vel(vel, ang))
def girar(mov, vel: int, ang: float):
    freq = vel_para_freq(vel)
    mov.send((ang_para_tempo(freq, ang), ang_para_vel(vel, ang)))

def avançar_por(mov, vel: int, *, tempo: float):
    mov.send((tempo, (vel, vel)))
def avançar_dist(mov, vel: int, *, dist: float):
    freq = vel_para_freq(vel)
    avançar_por(mov, vel, tempo=dist_para_tempo(freq, dist))
def avançar_um_bloco(mov, vel: int):
    avançar_dist(mov, vel, TAM_BLOCO)


## pid (não usado ainda, adaptado do controle_luis
I_MAX = 300
def inicializar_pid(vel_fixa: int, *, kp: float, ki: float, kd: float,
                    VEL_MAX: int=VEL_MAX, I_MAX: float=I_MAX,
                    EPSILON: float=0.1): #! tipos (gerador)
    I = err_ang_ant = 0
    t_ant = time()

    def pid(atual: posf, alvo: posf, orientação: float, v=vel_fixa) -> vel:
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

## para testes de pid (antigo)
def diferencial(original: posf, orientação: float,
                vels: tuple[float,float], duração: float,
                *, N_ITER = 1000) -> tuple[posf, float]:
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
#^ https://www.cs.columbia.edu/~allen/F19/NOTES/icckinematics.pdf pg 4

def simular_diferencial(inicial: posf, alvo: posf, orientação: float):
    import matplotlib.pyplot as plt
    dt = 0.02

    x,  y  = inicial
    xs, ys = [x], [y]

    pid = inicializar_pid(VEL_MAX//2, kp=0.1, ki=0.2, kd=0.5)
    for i in range(100):
        vels = pid((x, y), alvo, orientação)
        (x, y), orientação = diferencial(posição, orientação, vels, dt)

        xs.append(x)
        ys.append(y)

        if (vels == (0,0)): break

    plt.plot(xs, ys)
    plt.show()

## para testes de pid (adaptado do luis)
def simular(alvo: posf, tempo=2.0, N=1000, E=1):
    import matplotlib.pyplot as plt
    
    dt = tempo / N

    xs, ys = [0.0], [0.0]
    thetas = [0.0]

    speed = VEL_MAX//2
    l = 10 #! ?

    bot = inicializar_pid(vel, 500.0, 0, 0)
    for i in range(N):
        vl, vr = bot.send(((xs[i],ys[i]), alvo, thetas[i]))
        w = (vr - vl) / l
        thetas += [thetas[i] + w * dt]
        xs     += [xs[i] + speed * cos(thetas[i + 1]) * dt]
        ys     += [ys[i] + speed * sin(thetas[i + 1]) * dt]

        if (abs(complex(x_set - xs[i + 1], y_set - ys[i + 1])) < E): break

    plt.plot(x, y)
    plt.show()


if __name__ == "__main__":
    from argparse import ArgumentParser

    cmd = parseador = ArgumentParser()
    cmd.add_argument('id', type=int)

    subparseadores = parseador.add_subparsers(dest='cmd')
    cmd = comando_andar = subparseadores.add_parser('andar')
    cmd.add_argument('vel',  type=int)
    cmd.add_argument('dist', type=float)
    cmd.add_argument('--verbose', '-v', action='count', default=0)

    cmd = comando_girar = subparseadores.add_parser('girar')
    cmd.add_argument('vel', type=int)
    cmd.add_argument('ang', type=float)
    cmd.add_argument('--verbose', '-v', action='count', default=0)

    args = parseador.parse_args() #; print(args)

    def interpretar_comando(args):
        if args.verbose >= 3: print(args)

        if   args.cmd == 'andar':
            avançar_dist(movs[args.id], args.vel, dist=args.dist)
        elif args.cmd == 'girar':
            girar(movs[args.id], args.vel, ang=args.ang)
        if args.verbose >= 1: print(transmissor.envio)

        transmissor.enviar()
        espera_mov(movs[args.id])
        transmissor.enviar()
        if args.verbose >= 2: print(transmissor.envio)
    
    try:
      if not transmissor.inicializar():
          print("não foi possível inicializar a serial"); exit(1)
      movs = [movedor(i) for i in range(3)]
      for mov in movs: mov.send(None)

      interpretar_comando(args)

      if not args.id: exit(0)
      while True:
          args = parseador.parse_args(input("> ").split())
          interpretar_comando(args)
    except KeyboardInterrupt: pass
    finally:
      transmissor.finalizar()

