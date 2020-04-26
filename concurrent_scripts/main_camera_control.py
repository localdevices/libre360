'''
@author Gabriel Maguire
@date 4/26/2020

This script is the main control script used for triggering image capture commands for the CM360 project.
'''

from datetime import datetime
import signal, os, subprocess, sys
import time

camera_ports = []
capture_time = []

'''
This method searches for automatic processes that may start to run when a camera is initially connected.
These processes interfere with the functioning of the gphoto2 command library.
'''
def kill_gphoto2_process():
    p = subprocess.Popen(['ps', '-A'], stdout = subprocess.PIPE)
    out, err = p.communicate()
    
    # Search for process we want to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            # Kill the process
            print("Killed extra process")
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)

'''
This method detects every usb device (camera) connected to the Raspberry Pi and stores the port values
in a list. This is crucial, because each camera capture must be called using the specific port id, and
the port ids can change each time a camera is connected/disconnected.
'''
def detect_cameras():
    p = subprocess.Popen(["gphoto2", "--auto-detect"], stdout = subprocess.PIPE)
    out, err = p.communicate()
    
    usb_devices = []
    for line in out.splitlines():
        line = line.decode('utf-8') # Turns bytes into string
        id_start = line.find('usb:')
        if (id_start != -1):
            # Add usb port to usb device list
            id_end = line.find(' ', id_start)
            camera_ports.append(line[id_start:id_end])

'''
This method takes an integer value "count" (photo number) as an argument and triggers a camera
capture command for each camera in the CM360 device (currently testing with only 2). Each camera
is called in parallel tocapture an image, and immediately download the image to its specific camera
folder on the Pi.
'''
def capture_image(count):

    str_count = str(count)

    before_time = datetime.now()

    p1 = subprocess.Popen(["python3", "capture_camera_1.py", str_count, camera_ports[0]])
    p2 = subprocess.Popen(["python3", "capture_camera_2.py", str_count, camera_ports[1]])

    p1.wait()
    p2.wait()

    after_time = datetime.now()
    total_time = (after_time - before_time).total_seconds()
    capture_time.append(total_time)
    print("All cameras: {}".format(total_time))

'''
Main method that is setup to search for user input to trigger an image capture.
'''
def main():
    count = 1
    kill_gphoto2_process()
    detect_cameras()
    
    ''' This loop is used a temporary method of collecting user input to trigger an image capture '''
    while True:
        value = input("Command:\n")
        if value == "capture":
            print("CAPTURING IMAGE")
            capture_image(count)
            count = count + 1
        
        if value == "exit":
            print("EXITING")
            break
    print(type(capture_time[0]))
    
    '''
    These series of loops are used to test the total speed in seconds of the image capture
    and download with multiple cameras
    '''
    '''
    for _ in range(10):
        for _ in range(10):
            capture_image(count)
            count = count + 1
            time.sleep(1)
        time.sleep(5)
    print(capture_time)
    avg_capture_time = sum(capture_time) / len(capture_time)
    print("Average total capture time: {}".format(avg_capture_time))
    '''


if __name__ == "__main__":
    main()
