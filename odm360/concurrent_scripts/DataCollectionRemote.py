import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from time import sleep

GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(5,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(6,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(19,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(26,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(25,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(20,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Configuring GPIO Pins to input w/ pull down resistors


t0=0 #defining t0

try:
    while True:
        while True:
            if GPIO.input(17):
                t0=10
                break
            else:
                t0=1 #setting t0 Based on small switch position
                break
            
        while True:
             if GPIO.input(5):
                 print("Camera Capture")
                 sleep(t0)
             elif GPIO.input(6):
                 print ("Camera Capture")
                 sleep(t0*2)
             elif GPIO.input(13):
                 print("Camera Capture")
                 sleep(t0*3)
             elif GPIO.input(19):
                 print("Camera Capture")
                 sleep(t0*4)
             elif GPIO.input(26):
                 print("Camera Capture")
                 sleep(t0*5)
             elif GPIO.input(21):
                 print("Camera Capture")
                 sleep(t0*6)
             elif GPIO.input(20):
                 print("Camera Capture")
                 sleep(t0*7)
             elif GPIO.input(16):
                 print("Camera Capture")
                 sleep(t0*8)
             else:
                 break
             #Setting amount of time between captures based on position of the relay switch
             
        while True:
            if GPIO.input(25):
                print("Camera Capture")
                p = subprocess.Popen(["python3", "main_camera_control.py"])
                #p1.wait()
                break#Camera Capture command Button
            else:
                break #sending Capture command with button push
        
        while True:
            if GPIO.input(12):
                print("Send Data")
                break# Send Data to WebODM button
            else:
                break #sending send data command with button push


finally:
    GPIO.cleanup()
