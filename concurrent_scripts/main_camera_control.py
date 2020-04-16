from datetime import datetime
import signal, os, subprocess, sys
import numpy as np
import cv2

camera_ports = []

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

def capture_image(count):
	
	str_count = str(count)

	before_time = datetime.now()

	p1 = subprocess.Popen(["python3", "capture_camera_1.py", str_count, camera_ports[0]])
	p2 = subprocess.Popen(["python3", "capture_camera_2.py", str_count, camera_ports[1]])

	p1.wait()
	p2.wait()

	after_time = datetime.now()
	print("All cameras: {}".format((after_time - before_time).total_seconds()))

def main():
	count = 1
	kill_gphoto2_process()
	detect_cameras()
	while True:
		value = input("Command:\n")
		if value == "capture":
			print("CAPTURING IMAGE")
			capture_image(count)
			count = count + 1
		
		if value == "exit":
			print("EXITING")
			break
		
	cv2.destroyAllWindows()
	

	

if __name__ == "__main__":
	main()
