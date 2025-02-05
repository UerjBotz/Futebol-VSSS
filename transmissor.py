from serial import Serial
from time   import sleep, time

from serial.serialutil import SerialException

master: Serial
envio : list[int] = [0, 0, 0, 0, 0, 0]

def inicializar(porta: str="/dev/ttyUSB0", taxa: int=115200):
    global master
    try:
      master = Serial(porta, taxa)
      master.timeout = 3
    except SerialException: return False
    else:                   return True


def converter(pacote: list[int]) -> str:
    msg = ' '.join(map(str,pacote)) + '\n'
    return msg.encode()

def mover(motor_esq: int, motor_dir: int, *, robo: int, agora=False):
    envio[robo*2] = motor_esq
    envio[robo*2 + 1] = motor_dir
    
    if agora: enviar()

def enviar(velocidades: list[int] = envio):
    envio[:] = velocidades[:]
    master.write(converter(envio))

def finalizar():
    enviar([0,0,0,0,0,0])
    master.close()


if __name__ == '__main__':
    from sys import argv
    _, *args = argv

    inicializar()
    enviar(tuple(map(int, args)))
    if args: exit()
    try:
      while True:
          enviar(tuple(map(int, input("> ").split())))
    except KeyboardInterrupt: pass
    finally: finalizar()

