from math import pi
from time import time
from math import sin, cos
from cmath import polar, phase
import transmissor

_tam_eixo = 68.3  #mm
_diâmetro_roda = 34.5  #mm
R = _diâmetro_roda / 2
L = _tam_eixo

#vel_x = R*cos(angulo)*(vr+vl)/2; vel_y = R*sin(angulo)*(vr+vl)/2
#vel_angular = angulo

#vel_x = v*cos(angulo); vel_x = v*cos(angulo)
#vel_angular = R*(vr - vl)/L

# ->

#vl = lambda v, ang: ((2*v) + (ang*L)) / 2 * R
#vr = lambda v, ang: ((2*v) - (ang*L)) / 2 * R

#ang_para_vel = lambda v, ang: (vl(v, ang), vr(v, ang))
#raio_curva = lambda vl, vr: (R/2)*(vr+vl)/(vr-vl)

def movedor(robo: int, espera: float = 0, vels: tuple[int, int] = (0,0)):
  t_ini = time()
  while True:
    if (time() - t_ini) < espera:
      transmissor.mover(*vels, robo=robo)
    else:
      transmissor.mover(0, 0, robo=robo)
    params = yield
    if params is not None:
      t_ini = time()
      espera, vels = params

_rpm = 100 #(?)
_circ = 2*pi*R #mm
_freq = _rpm/60 #Hz
vel_max = _circ*_freq #mm/s

def girar(vel: int, ang: float, mov, passo_tempo: float = 1):
  mov.send((passo_tempo, ang_para_vel(vel, ang)))

def avançar_um_bloco(vel: int, mov, *, passo_tempo: float = 1):
  mov.send((passo_tempo, (vel, vel)))

#####luis

distância = lambda pos0, pos1: ((pos0[0]-pos1[0])**2 + (pos0[1]-pos1[1])**2)**0.5

pos = tuple[float, float]

I_MAX = 300
def inicializar_pid(vel_padrão, *, kp, ki, kd, EPSILON=0.1):
  err_ang_ant = 0
  t_ant = time()
  I = 0

  def pid(atual: pos,
          alvo: pos,
          orientação: float,
          v=vel_padrão
          ) -> tuple[int, int]:
    nonlocal I
    nonlocal t_ant
    nonlocal err_ang_ant

    x0, y0 = atual
    x1, y1 = alvo

    desloc = complex(x1 - x0, y1 - y0)
    err_ang = phase(desloc) - orientação

    t_agr = time()
    dt = t_agr - t_ant
    derr = err_ang - err_ang_ant

    P = kp * err_ang
    I = I + ki * err_ang * dt
    D = (kd / dt) * derr

    I = min(I_MAX, max(-I_MAX, I))
    err_ang_ant = err_ang
    t_ant = t_agr

    dv = P + I + D
    vr = int(min(1023, max(v - dv, -1023)))
    vl = int(min(1023, max(v + dv, -1023)))
    vels = vl, vr
    if distância(0, vels) < EPSILON:
      return (0,0)
    else:
      return (vl, vr)

  return pid


#https://www.cs.columbia.edu/~allen/F19/NOTES/icckinematics.pdf pg 4
def diferencial (original: pos, orientação: float, vels: tuple[float,float], duração: float, *, N_ITER = 1000) -> tuple[pos, float]:
  theta = orientação
  x, y = original
  w = (1/R)*(vels[0]-vels[1])
  v = 0.5*(vels[0]+vels[1])
  dt = duração/N_ITER
  for i in range(N_ITER) :
    theta += w*dt
    x += v*cos(theta)*dt
    y += v*sin(theta)*dt
  return (x, y), theta


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


##teste
simular((0, 0), (10, 7), 2)
