import serial  #type: ignore
from time import sleep, time

master = serial.Serial( "COM14", #"/dev/ttyACM0",
                       115200,
                       timeout = 0.1,
                       writeTimeout = 0.1
                       )
#sleep(1)

def send_ch_333(data: list[int]) -> str:
  send_list( [333] + data )

def send_list(data: list[int]) -> str:
  msg = "Send "
  for d in data:
    msg += f"{d} "
  send(msg + " \n")

def send( msg ):
  master.write(msg.encode())

def close():
  send_ch_333([])
  master.close()