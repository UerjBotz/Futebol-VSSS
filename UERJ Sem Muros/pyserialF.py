import serial
import time

def serialStart(porta,bit):
    SerialObj = serial.Serial(porta,bit)
    time.sleep(3)
    SerialObj.timeout = 3
    return SerialObj


def serialBlink(SerialObj,detected):
    if detected == "A":
       SerialObj.write(b'A')
    elif detected == "B":
       SerialObj.write(b'B')
    print(SerialObj.readline()) #readline reads a string terminated by \n
    return

def serialRotate(SerialObj,girar):
   if girar == True:
      SerialObj.write("-1000,1000,0,0,0,0".encode())
   else:
      SerialObj.write("0,0,0,0,0,0".encode())
   return

def serialClose(SerialObj):
   SerialObj.close()
   return