import serial
import time

def serialStart(porta,bit):
        
    # Receives a string from Arduino using readline()
    # Requires PySerial

    # (c) www.xanthium.in 2021
    # Rahul.S

    SerialObj = serial.Serial(porta,bit) # COMxx   format on Windows

                                            # /dev/ttyUSBx format on Linux
                                            #
                                            # Eg /dev/ttyUSB0
                                            # SerialObj = serial.Serial('/dev/ttyUSB0')

    time.sleep(3)   # Only needed for Arduino,For AVR/PIC/MSP430 & other Micros not needed
                    # opening the serial port from Python will reset the Arduino.
                    # Both Arduino and Python code are sharing Com11 here.
                    # 3 second delay allows the Arduino to settle down.


    SerialObj.timeout = 3 # set the Read Timeout
    return SerialObj


def serialBlink(SerialObj,detected):
    if detected == "A":
       SerialObj.write(b'A')
    elif detected == "B":
       SerialObj.write(b'B')
    print(SerialObj.readline()) #readline reads a string terminated by \n
    return

def serialClose(SerialObj):
   SerialObj.close()
   return