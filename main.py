from time  import sleep
from astar import B, G, L, astar as planejar
from visão import vision_conf, vision_info, vision as visão
from enum  import Enum

import transmissor
import controle
import ajogada as aj

import pygame
import numpy as np
import cv2   as cv


# CONSTANTES E TIPOS
Estado = Enum('Estado', ['PARADO',
                         'NORMAL',
                         'BOLA_LIVRE_FAVOR',
                         'BOLA_LIVRE_CONTRA', 
                         'TIRO_LIVRE_FAVOR',
                         'TIRO_LIVRE_CONTRA',
                         'PÊNALTI_FAVOR',
                         'PÊNALTI_CONTRA'])

N_ROBÔS = 3
FATOR_MATRIZ = 1 / 100
VEL_MAX = 100

PX2CM = 0.1
CONVERSÃO = 10 * PX2CM #! isso dá 1... ver depois se ainda usar...

# Globais
estado_atual: Estado = Estado.PARADO
vs_conf: vision_conf = vision_conf(0,0,0,0, {
    'MIN':  {"darkblue": 0, "yellow": 0, "orange": 0,
             "red": 0, "blue": 0, "green": 0, "pink": 0},
    'MEAN': {"darkblue": 0, "yellow": 0, "orange": 0,
             "red": 0, "blue": 0, "green": 0, "pink": 0},
    'MAX':  {"darkblue": 0, "yellow": 0, "orange": 0,
             "red": 0, "blue": 0, "green": 0, "pink": 0},
}) #! checar código velho

captura = cv.VideoCapture(0)
img = np.zeros((200,200, 3), np.uint8) #! dimensão

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


def acessa_dicio(dicio, chave, valor_padrão):
    return dicio[chave] if chave in dicio else valor_padrão
  
def id(robô):
    return acessa_dicio(robô, 'robotId', -1)

def coordenadas(robô: dict):  #! usar info_campo/2 [...]?
    return (robô['x'] + 850, -(robô['y'] - 650))

def posição_matriz(coord):
    x, y = coord
    return int(x * FATOR_MATRIZ), int(y * FATOR_MATRIZ)

# def inserir_na_matriz(matriz: np.ndarray, entidade: dict):
#     x, y = coordenadas(entidade)
#     matriz[int(x*FATOR_MATRIZ), int(y*FATOR_MATRIZ)] = 1

def atualiza_matriz(entidades: list[dict]):
    nova = GRADE_INICIAL.copy()
    for entidade in entidades:
        nova[posição_matriz(entidade)]
    return nova


def main(args: list[str]):
    global estado_atual

    pygame.init() 
    movedores = [controle.movedor(i) for i in range(0,3)]

    vel_fixa = 60#%
    for m in movedores:
        next(m)
        controle.avançar_um_bloco(VEL_MAX//3, m)

    ret, img = captura.read()

    visto, _ = visão(img, vs_conf, CONVERSÃO) #! descarte _
    posições = visto.teams

    amarelos = acessa_dicio(posições, 'team_yellow', {})
    azuis    = acessa_dicio(posições, 'team_blue',   {})

    try:
        if   args[0] == 'y': time = amarelos
        elif args[0] == 'b': time = azuis
        else:
            print(f"{args[0]} não é um time válido")
            exit(1)
    except IndexError:
        print(f"por favor forneça o time")
        exit(1)
    else:
        arg_time = args[0]

    ids = sorted([id for id in time.keys()])
  
    while True:
      try:
        keys = pygame.key.get_pressed()
        if   keys[pygame.KSCAN_SPACE]:
            print(f"letra: espaço")
            estado_atual = Estado.PARADO
        elif keys[pygame.KSCAN_KP_ENTER]:
            print(f"letra: enter")
            estado_atual = Estado.NORMAL
        else:
            print(f"letra: {True in keys}")
    
        ret, frame = captura.read()
        if ret:
            img = frame
        else: continue
            
        visto, _ = visão(img, vs_conf, CONVERSÃO) #! descarte _
        posições = visto.teams

        amarelos = acessa_dicio(posições, 'team_yellow', amarelos)
        azuis    = acessa_dicio(posições, 'team_blue',   azuis)
        if   arg_time == 'y': time = amarelos
        elif arg_time == 'b': time = azuis
        else: assert False
    
        bola = visto.ball # acessa_dicio(posições, 'balls', {'x': 0, 'y': 0})
        for _, robô in time.items():
            print("time")
            if   estado_atual == Estado.PARADO:
                print("parado")
                id_transmissor = ids.index(robô.id)
                vels = aj.parado()
            elif estado_atual == Estado.NORMAL:
                print("normal")
                id_transmissor = ids.index(robô.id)
                if id_transmissor == 0:
                    pos_alvo = aj.guardar_gol(coordenadas(robô), coordenadas(bola))
                elif id_transmissor == 1:
                    pos_alvo = aj.defender(coordenadas(robô), coordenadas(bola))
                else: # id_transmissor == 2:
                    pos_alvo = aj.seguir_a_bola(coordenadas(robô), coordenadas(bola), entrar_area=True)
                #! vels = pids[id_transmissor].update(vel_fixa, *coordenadas(robô), robô['orientation'], *pos_alvo)
            else: assert False, "outros estados não implementados"

            transmissor.mover(*vels, robo=id_transmissor)
            print(f"robô: {robô.pos}, aplicando vel {vels}")

        transmissor.enviar()
        sleep(0.214) #! não

      except KeyboardInterrupt: break
    transmissor.finalizar()

if __name__ == "__main__":
    from sys import argv
    main(argv[1:])

