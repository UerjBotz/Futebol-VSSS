from astar import B, G, L, astar as planejar
from receptor import Client
from google.protobuf.json_format import MessageToDict
import transmissor
import numpy as np


# CONSTANTES
N_ROBÔS = 3
FATOR_MATRIZ = 1/100
VEL_MAX = 1000

#GRADE_INICIAL = np.zeros((13, 17))
GRADE_INICIAL = np.array([
  [B, L, L, L, L, L, L, L, L, L, L, L, L, L, L, L, B],
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
  [B, L, L, L, L, L, L, L, L, L, L, L, L, L, L, L, B]
])

def coordenadas(robô: dict):  #! usar info_campo/2 [...]?
  return (robô['x'] + 850, -(robô['y'] - 650))

def posição_matriz(coord):
  x, y = coord
  return int(x*FATOR_MATRIZ), int(y*FATOR_MATRIZ)
  
# def inserir_na_matriz(matriz: np.ndarray, entidade: dict):
#   x, y = coordenadas(entidade)
#   matriz[int(x*FATOR_MATRIZ), int(y*FATOR_MATRIZ)] = 1

def atualiza_matriz(entidades: list[dict]):
  nova = GRADE_INICIAL.copy()
  for entidade in entidades:
    nova[posição_matriz(entidade)]
  return nova

# GLOBAIS
visão = Client()
deve_parar = False

info_campo = MessageToDict(visão.receive_frame().geometry)

def main():
  robôs_amarelos = robôs_azuis = [{"robot_id": 0, "x": 0, "y": 0}]
  
  global deve_parar
  while not (deve_parar):
    try:
      posições = MessageToDict(visão.receive_frame().detection)
      #print(posições)
      robôs_amarelos = posições[ 'robotsYellow'] if 'robotsYellow' in posições else robôs_amarelos
      robôs_azuis = posições['robotsBlue'] if 'robotsBlue' in posições else robôs_azuis

      for robô in robôs_amarelos:
        print(f"amarelo: {robô['x']}, {robô['y']}")
      for robô in robôs_azuis:
        print(f"azul: {robô['x']}, {robô['y']}")

      #transmissor.enviar([1000, 1000, 1000, 1000, 1000, 1000])
      #transmissor.mover(vel_max, vel_max, robo=0)

    except KeyboardInterrupt:
      deve_parar = True

  transmissor.finalizar()
