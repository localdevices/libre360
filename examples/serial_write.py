#!/usr/bin/env python
import time
import serial

ser = serial.Serial(
    port="/dev/ttyUSB1",  # Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
)
counter = 0

while 1:
    ser.write(str.encode(f"Write counter: {counter}\n"))
    time.sleep(5)
    counter += 1
