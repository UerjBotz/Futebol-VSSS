from math import pi
from time import time
import transmissor

_tam_eixo = 68.3  #mm
_diâmetro_roda = 34.5  #mm
R = _diâmetro_roda/2
L = _tam_eixo

#vel_x = R*cos(angulo)*(vr+vl)/2; vel_y = R*sin(angulo)*(vr+vl)/2
#vel_angular = angulo

#vel_x = v*cos(angulo); vel_x = v*cos(angulo)
#vel_angular = R*(vr - vl)/L

# ->

vl = lambda v, ang: ((2*v) + (ang*L)) / 2 * R
vr = lambda v, ang: ((2*v) - (ang*L)) / 2 * R

ang_para_vel = lambda v, ang: (vl(v, ang), vr(v, ang))

def movedor(espera: float, vels: tuple[int, int], *, robo: int):
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

def girar(vel: int, ang: float, mov):
  passo_tempo = 1
  mov.send((passo_tempo, ang_para_vel(vel, ang)))

def avançar_um_bloco(vel: int, mov):
  passo_tempo = 1
  mov.send((passo_tempo, (vel, vel)))
