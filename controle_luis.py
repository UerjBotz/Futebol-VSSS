from math import pi
from time import time
from math import sin, cos
from cmath import polar, phase
#import transmissor


def constrain(x, MIN, MAX):
  if (x >= MAX): return MAX
  if (x <= MIN): return MIN
  return x


class pid:
  kp = 1.0
  ki = 0.0
  kd = 0.0

  P = 0
  I = 0
  D = 0

  theta_erro_last = 0
  t_last = time()

  def __init__(self, kp=1.0, ki=0.0, kd=0.0) -> None:
    self.kp = kp
    self.ki = ki
    self.kd = kd
    t_last = time()

  def update(self, speed, x_act, y_act, theta_act, x_set, y_set):
    t = time()
    self.t_last = time()
    dt = t - self.t_last

    v_set = x_set + 1j * y_set - x_act - 1j * y_act
    theta_set = polar(v_set)[1]
    theta_erro = theta_set - theta_act

    if (theta_erro > 0):
      theta_erro = theta_erro % pi
    elif (theta_erro < 0):
      theta_erro = -(abs(theta_erro) % pi)

    self.P = theta_erro * self.kp
    self.I += theta_erro * self.ki * dt
    self.I = constrain(self.I, -300, 300)
    self.D = (theta_erro - self.theta_erro_last) * self.kd * dt
    self.theta_erro_last = theta_erro

    dif = self.P + self.I + self.D

    vl = constrain(speed - dif, -1000, 1000)
    vr = constrain(speed + dif, -1000, 1000)
    return (vl, vr)


def simular(x_set, y_set):
  import matplotlib.pyplot as plt

  tempo = 2.0
  N = 1000
  dt = tempo / N

  x = [0.0]
  y = [0.0]
  theta = [0.0]

  speed = 200
  l = 10

  bot = pid(500.0, 0, 0)

  for i in range(N):
    vl, vr = bot.update(speed, x[i], y[i], theta[i], x_set, y_set)
    w = (vr - vl) / l
    theta += [theta[i] + w * dt]
    x += [x[i] + speed * cos(theta[i + 1]) * dt]
    y += [y[i] + speed * sin(theta[i + 1]) * dt]

    if (polar(complex(x_set - x[i + 1], y_set - y[i + 1]))[0] < 1):
      break

  plt.plot(x, y)
  plt.show()


#simular( 10, 50 );
