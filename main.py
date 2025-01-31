from time  import sleep
from astar import B, G, L, astar as planejar
from visão import vision_conf, vision_info, bot_info, vision as visão
from enum  import Enum
from queue import Queue
from threading import Thread

import transmissor
import controle
import ajogada as aj

import atexit
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
fila_teclado = Queue[str]()

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

acessa_dicio = dict.get #!

def complex_to_tuple(pos: complex) -> tuple:
    return pos.real, pos.imag
  
def id(robô):
    return acessa_dicio(robô, 'robotId', -1)

def coords(robô: bot_info):  #! usar info_campo/2 [...]?
    x, y = complex_to_tuple(robô.pos)
    return (x + 850, -(y - 650)) #! ver se ainda tem que fazer isso

def posição_matriz(coord):
    x, y = coord
    return int(x * FATOR_MATRIZ), int(y * FATOR_MATRIZ)

def inserir_na_matriz(matriz: np.ndarray, entidade: dict):
    x, y = coords(entidade)
    matriz[int(x*FATOR_MATRIZ), int(y*FATOR_MATRIZ)] = 1

def atualiza_matriz(entidades: list[dict]):
    nova = GRADE_INICIAL.copy()
    for entidade in entidades:
        nova[posição_matriz(entidade)]
    return nova


def ler_teclado(): # adaptado de https://stackoverflow.com/a/10079805
    import termios, select, sys, tty

    conf_term_antiga = termios.tcgetattr(sys.stdin)

    @atexit.register
    def resetar_terminal():
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, conf_term_antiga)

    tty.setcbreak(sys.stdin.fileno())
    while True:
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            fila_teclado.put(sys.stdin.read(1))

    #! windows

def main(args: list[str]):
    global estado_atual

    movedores = [controle.movedor(i) for i in range(0,3)]

    vel_fixa = 60#%
    for m in movedores:
        m.send(None)
        controle.avançar_um_bloco(VEL_MAX//3, m) #! teste

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
        if not fila_teclado.empty():
            tecla = fila_teclado.get()
            if   tecla == ' ':
                estado_atual = Estado.PARADO
                print(f"MODO PARADO")
            elif tecla == '\n':
                estado_atual = Estado.NORMAL
                print(f"MODO NORMAL")
            else:
                print(f"letra: {tecla}")
    
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
    
        bola = visto.ball #! acessa_dicio(posições, 'balls', {'x': 0, 'y': 0})
        for _, robô in time.items():
            id_transmissor = ids.index(robô.id) #! id(robô)
            if   estado_atual == Estado.PARADO:
                vels = aj.parado()
            elif estado_atual == Estado.NORMAL:
                vels = (0,0)
                if id_transmissor == 0:
                    pos_alvo = aj.guardar_gol(coords(robô), coords(bola))
                elif id_transmissor == 1:
                    pos_alvo = aj.defender(coords(robô), coords(bola))
                elif id_transmissor == 2:
                    pos_alvo = aj.seguir_a_bola(coords(robô), coords(bola), entrar_area=True)
                else: assert False
            else: assert False, "outros estados não implementados"
            
            if controle.terminou_mov(movedores[id_transmissor]):
                movedores[id_transmissor].send((0.1, vels))
            print(f"robô: {robô.pos}, aplicando vel {vels}")

        transmissor.enviar()
        sleep(0.214) #! não

      except KeyboardInterrupt: break
    transmissor.finalizar()

if __name__ == "__main__":
    Thread(target=ler_teclado, daemon=True).start()

    from sys import argv
    main(argv[1:])

