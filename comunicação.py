import serial #type: ignore
import time
import numpy as np

master: serial.Serial
envio: np.ndarray = np.zeros(6)

def converter (pacote: np.ndarray) -> str :
	return str(pacote[0])+","+str(pacote[1])+","+str(pacote[2])+","+str(pacote[3])+","+str(pacote[4])+","+str(pacote[5])

def começar (porta:str,baudrate:int) :
	master = serial.Serial(porta,baudrate)
	time.sleep(3)
	master.timeout = 3

def rodar (girar:bool) :
	if girar == True:
		master.write("-1000,1000,-1000,1000,-1000,1000".encode())
	else:
		master.write("0,0,0,0,0,0".encode())

def andar (motor_esq:int, motor_dir:int,*, robo:int=0) :
	envio[robo*2] = motor_esq; envio[robo*2 +1] = motor_dir
	master.write(converter(envio).encode())

def finalizar ():
	master.close()