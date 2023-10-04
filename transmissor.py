import serial  #type: ignore

from time import sleep
from numpy import ndarray, zeros

envio = [0, 0, 0, 0, 0, 0]
master = serial.Serial("/dev/ttyUSB0", 115200)
sleep(3)
master.timeout = 3


def converter(pacote: list[int]) -> str:
  return "Send 333, " + f"{pacote[0]},{pacote[1]},{pacote[2]},{pacote[3]},{pacote[4]},{pacote[5]}"
  # return f"{pacote[0]},{pacote[1]},{pacote[2]},{pacote[3]},{pacote[4]},{pacote[5]}"


def rodar(girar: bool):
  if girar == True:
    master.write("Send 333, -1000,1000,-1000,1000,-1000,1000".encode())
  else:
    master.write("Send 333, 0,0,0,0,0,0".encode())

def mover(motor_esq: int, motor_dir: int, *, robo: int = 0):
  envio[robo * 2] = motor_esq
  envio[robo * 2 + 1] = motor_dir
  master.write(converter(envio).encode())

def enviar(velocidades: list[int]):
  envio = velocidades
  master.write(converter(envio).encode())

def finalizar():
  enviar([0,0,0,0,0,0])
  master.close()
