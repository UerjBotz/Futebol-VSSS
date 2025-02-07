from time  import sleep
from astar import B, G, L, astar as planejar
from visão import vision_conf, vision_info, bot_info, vision as visão
from enum  import Enum
from queue import Queue

from threading import Thread, Event

import transmissor
import controle
import teclado
import ajogada as aj

import numpy as np
import cv2   as cv


## CONSTANTES e Tipos
class Evento(Event):
    __call__ = Event.is_set

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

PX2CM     = .1
CONVERSÃO = 10 * PX2CM #! isso dá 1... ver depois se ainda usar...


## Globais
fim         : Evento = Evento()
estado_atual: Estado = Estado.PARADO

cores_min = {"orange":   3,
             "yellow":   14,
             "green":    38,
             "blue":     72, # ciano
             "darkblue": 99, # azul
             "pink":    134,
             "red":     180} #! não consegui ler
cores     = list(cores_min.items())
cores_max = {cor: h for cor, h in cores[1:]+cores[:1]}

vs_conf: vision_conf = vision_conf(86,86,20, 0, {
    'MIN':  cores_min,
    'MEAN': {c: (cores_min[c] + cores_max[c])//2
                           for c, _ in cores},
    'MAX':  cores_max,
})

cam    = cv.VideoCapture(3)
frames = Queue[np.ndarray]()

w = int(cam.get(cv.CAP_PROP_FRAME_WIDTH))
h = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT))


## Grade
GRADE_INICIAL = np.array([ # 13 por 17
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
  
def coords(robô: bot_info): #! usar info_campo/2 [...]?
    x, y = complex_to_tuple(robô.pos)
    return (x + 850, -(y - 650)) #! ver se ainda tem que fazer isso

def posição_matriz(coord):
    x, y = coord
    return int(x * FATOR_MATRIZ), int(y * FATOR_MATRIZ)

def inserir_na_matriz(matriz: np.ndarray, entidade: dict) -> None: #! tipos
    x, y = coords(entidade)
    matriz[int(x*FATOR_MATRIZ), int(y*FATOR_MATRIZ)] = 1

def atualiza_matriz(entidades: list[dict]) -> np.ndarray:
    nova = GRADE_INICIAL.copy()
    for entidade in entidades:
        nova[posição_matriz(entidade)]
    return nova


## Threads
def camera(fim: Evento):
    while not fim():
        ret, frame = cam.read()
        if not ret:
            print("Não foi possível receber o frame..."); fim.set()
        elif frames.empty():
            frames.put(frame)

def main(arg_time: str, desenhar: bool):
    vel_escalar = VEL_MAX*2/3

    movedores = [controle.movedor(i) for i in range(N_ROBÔS)]
    for m in movedores: m.send(None)

    frame = frames.get()
    visto, tela = visão(frame, vs_conf, CONVERSÃO, desenhar)
    posições = visto.teams

    amarelos, azuis = {}, {}
    if   arg_time == 'y':
        time = acessa_dicio(posições, 'team_yellow', {})
    elif arg_time == 'b':
        time = acessa_dicio(posições, 'team_blue',   {})
    else: assert False

    ids = sorted([id for id in time.keys()])
    try:
      for m in movedores: #! teste
          controle.avançar_um_bloco(m, VEL_MAX//3) #! teste
      transmissor.enviar() #! teste

      global estado_atual
      while not fim():
        if not teclado.fila.empty():
            tecla = teclado.fila.get()
            if   tecla == teclado.ESPAÇO:
                estado_atual = Estado.PARADO
                print(f"MODO: PARADO")
            elif tecla == teclado.ENTER:
                estado_atual = Estado.NORMAL
                print(f"MODO: NORMAL")
            elif tecla == teclado.ESC:
                print("Saindo..."); raise KeyboardInterrupt
            else:
                print(f"letra: {tecla.encode()}, {ord(tecla)}")
    
        if not frames.empty():
            frame = frames.get()

        visto, tela = visão(frame, vs_conf, CONVERSÃO, desenhar)
        posições = visto.teams

        amarelos = acessa_dicio(posições, 'team_yellow', amarelos)
        azuis    = acessa_dicio(posições, 'team_blue',   azuis)
        if   arg_time == 'y': time = amarelos
        elif arg_time == 'b': time = azuis
    
        bola = visto.ball #! fallback/valor_padrão?
        for _, robô in time.items():
            try: id_transmissor = ids.index(robô.id) #! esquisito
            except ValueError: continue #! esquisito

            if   estado_atual == Estado.PARADO:
                vels = aj.parado()
            elif estado_atual == Estado.NORMAL:
                vels = (0,0)
                if   id_transmissor == 0:
                    pos_alvo = aj.guardar_gol(coords(robô), coords(bola))
                elif id_transmissor == 1:
                    pos_alvo = aj.defender(coords(robô), coords(bola))
                elif id_transmissor == 2:
                    pos_alvo = aj.seguir_a_bola(coords(robô), coords(bola),
                                                entrar_area=True)
                else: assert False
            else: assert False, "outros estados não implementados"
            
            if controle.terminou_mov(movedores[id_transmissor]):
                movedores[id_transmissor].send((0.1, vels))
            print(f"robô {id_transmissor} em {robô.pos} com vel aplicada {vels}")

        cv.imshow("preview", tela["vision"])
        cv.waitKey(1) # necessário!!!

        transmissor.enviar()
    except KeyboardInterrupt: pass
    finally:
      fim.set()

      cam.release()
      cv.destroyAllWindows()
      transmissor.finalizar()

## Ponto de entrada do programa
if __name__ == "__main__":
    from sys import argv as args
    try:
      nome, *args = args
      time, *args = args
    except (IndexError, ValueError):
      print(f"uso:\n"
            f"    python3 {nome} <time>\n\n"
            f"<time>: y|b\n", end='')
    else:
      if not (time in ('y', 'b')):
          print(f"{time} não é um time válido"); exit(1)
      if not (cam.isOpened()):
          print("Não foi possível abrir a câmera"); exit(1)
      if not (transmissor.inicializar()):
          print("Não foi possível abrir a serial"); exit(1)

      Thread(target=teclado.ler_para_sempre, daemon=True).start()
      Thread(target=camera, args=[fim], daemon=True).start()
      main(arg_time=time, desenhar=True)

