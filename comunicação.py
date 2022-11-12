import serial #type: ignore
import time

from numpy import ndarray, zeros

master: serial.Serial
envio: ndarray = zeros(6)

def converter (pacote: ndarray) -> str :
	return f"{pacote[0]},{pacote[1]},{pacote[2]},{pacote[3]},{pacote[4]},{pacote[5]}"

def começar (porta:str,baudrate:int) :
	master = serial.Serial(porta,baudrate)
	time.sleep(3)
	master.timeout = 3

def rodar (girar:bool) :
	if girar == True:
		master.write("-1000,1000,-1000,1000,-1000,1000".encode())
	else:
		master.write("0,0,0,0,0,0".encode())

def mover (motor_esq:int, motor_dir:int,*, robo:int=0) :
	envio[robo*2] = motor_esq; envio[robo*2 +1] = motor_dir
	master.write(converter(envio).encode())

def finalizar ():
	master.close()