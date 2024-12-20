from time import sleep
from astar import B, G, L, astar as planejar
from receptor import Client
from enum import Enum
from sys import argv

from google.protobuf.json_format import MessageToDict

import transmissor
import controle
import controle_luis
import numpy as np

import ajogada as aj

import pygame

Estado = Enum('Estado', ['PARADO',
                         'NORMAL',
                         'BOLA_LIVRE_FAVOR',
                         'BOLA_LIVRE_CONTRA', 
                         'TIRO_LIVRE_FAVOR',
                         'TIRO_LIVRE_CONTRA',
                         'PÊNALTI_FAVOR',
                         'PÊNALTI_CONTRA'])

estado_atual = Estado.PARADO

# CONSTANTES
N_ROBÔS = 3
FATOR_MATRIZ = 1 / 100
VEL_MAX = 1000

#GRADE_INICIAL = np.zeros((13, 17))
GRADE_INICIAL = np.array([[B, L, L, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
                          [B, L, L, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
                          [B, L, L, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
                          [B, G, G, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
                          [B, G, G, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
                          [G, G, G, L, L, L, L, L, L, L, L, L, L, L, L, L, L],
                          [G, G, G, L, L, L, L, L, L, L, L, L, L, L, L, L, L],
                          [G, G, G, L, L, L, L, L, L, L, L, L, L, L, L, L, L],
                          [B, G, G, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
                          [B, G, G, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
                          [B, L, L, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
                          [B, L, L, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
                          [B, L, L, L, L, L, L, L, L, L, L, L, L, L, L, L, B]])


def acessa_dicio(dicio, chave, valor_padrão):
  return dicio[chave] if chave in dicio else valor_padrão
  
def id (robô):
  return acessa_dicio(robô, 'robotId', -1)

def coordenadas(robô: dict):  #! usar info_campo/2 [...]?
  return (robô['x'] + 850, -(robô['y'] - 650))

def posição_matriz(coord):
  x, y = coord
  return int(x * FATOR_MATRIZ), int(y * FATOR_MATRIZ)


# def inserir_na_matriz(matriz: np.ndarray, entidade: dict):
#   x, y = coordenadas(entidade)
#   matriz[int(x*FATOR_MATRIZ), int(y*FATOR_MATRIZ)] = 1


def atualiza_matriz(entidades: list[dict]):
  nova = GRADE_INICIAL.copy()
  for entidade in entidades:
    nova[posição_matriz(entidade)]
  return nova


# GLOBAIS
visão = Client(vision_ip='224.5.23.2', vision_port=10015)
deve_parar = False
pygame.init() 
info_campo = MessageToDict(visão.receive_frame().geometry)


def main(argv: list[str]):
  movedores = [controle.movedor(0),
               controle.movedor(1),
               controle.movedor(2)]

  vel_fixa = 600
  pids = [controle_luis.pid(kp=0.1, ki=0.2, kd=0.5) for i in range(3)]
  for m in movedores:
    next(m)
    controle.avançar_um_bloco(VEL_MAX // 3, m)

  dicio_padrão = [{"robot_id": 0, "x": 0, "y": 0, "orientation": 0}]
  robôs_amarelos = dicio_padrão.copy(); robôs_azuis = dicio_padrão.copy()

  posições = MessageToDict(visão.receive_frame().detection)
  robôs_amarelos = acessa_dicio(posições, 'robotsYellow', robôs_amarelos)
  robôs_azuis    = acessa_dicio(posições, 'robotsBlue', robôs_azuis)

  if   argv[1] == 'y': #! isso tem que tar dentro
    time = robôs_amarelos
  elif argv[1] == 'b': #! isso tem que tar dentro
    time = robôs_azuis
  else: exit(1)
  
  ids = [id(robô) for robô in time]
  ids.sort()
  
  global deve_parar, estado_atual
  while not (deve_parar):
    try:
      keys = pygame.key.get_pressed()
      if   keys[pygame.KSCAN_SPACE]:
        estado_atual = Estado.PARADO
      elif keys[pygame.KSCAN_KP_ENTER]:
        estado_atual = Estado.NORMAL

      posições = MessageToDict(visão.receive_frame().detection)

      robôs_amarelos = acessa_dicio(posições, 'robotsYellow', robôs_amarelos)
      robôs_azuis = acessa_dicio(posições, 'robotsBlue', robôs_azuis)
      bola = acessa_dicio(posições, 'balls', {'x': 0, 'y': 0})
      for robô in time:
        if   estado_atual == Estado.PARADO:
          id_transmissor = ids.index(id(robô))
          vels = aj.parado()
        else: #if estado_atual == Estado.NORMAL:
          id_transmissor = ids.index(id(robô))
          if id_transmissor == 0:
            pos_alvo = aj.guardar_gol(coordenadas(robô), coordenadas(bola))
          elif id_transmissor == 1:
            pos_alvo = aj.defender(coordenadas(robô), coordenadas(bola))
          else: # id_transmissor == 2:
            pos_alvo = aj.seguir_a_bola(coordenadas(robô), coordenadas(bola), entrar_area=True)
          vels = pids[id_transmissor].update(vel_fixa, *coordenadas(robô), robô['orientation'], *pos_alvo)
        transmissor.mover(*vels, robo=id_transmissor)
        print(f"robô: {robô['x']}, {robô['y']}, aplicando vel {vels}")

      transmissor.enviar()
      sleep(0.214)

    except KeyboardInterrupt:
      deve_parar = True

  transmissor.finalizar()


main(argv)
