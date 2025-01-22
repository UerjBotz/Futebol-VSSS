from serial import Serial
from time   import sleep, time

master = Serial("/dev/ttyUSB0", 115200)
#! sleep(3) #! ver se precisa mesmo. muito esquisito...
master.timeout = 3

envio = [0, 0, 0, 0, 0, 0]


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

    enviar(tuple(map(int, argv[1:])))

