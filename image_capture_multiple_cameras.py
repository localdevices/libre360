from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess


usb_devices = [] # List of camera usb ports

# List of useful gphoto2 commands
gphoto2 = "gphoto2" # Access to gphoto2 library
auto_detect = "--auto-detect" # Detect all connected cameras
list_ports = "--list-ports" # List active ports
port = "--port" # Specify camera by usb port
filename = "--filename" # Specify filename
trigger_capture = "--trigger-capture" # Does not actually capture a photo, useful for testing
capture_image_and_download = "--capture-image-and-download" # Set camera photo quality to standard


shot_date = datetime.now().strftime("%Y-%m-%d")
shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

save_dir = "/home/pi/cm360/gphoto2_images/"




# Make sure to kill gphoto2 process that starts when
# the camera is initially connected (gvfsd-gphoto2).

def kill_gphoto2_process():
    p = subprocess.Popen(['ps', '-A'], stdout = subprocess.PIPE)
    out, err = p.communicate()
    
    # Search for process we want to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            # Kill the process
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)
            
            
def detect_cameras():
    p = subprocess.Popen([gphoto2, auto_detect], stdout = subprocess.PIPE)
    out, err = p.communicate()
    
    for line in out.splitlines():
        line = line.decode('utf-8') # Turns bytes into string
        id_start = line.find('usb:')
        if (id_start != -1):
            # Add usb port to usb device list
            id_end = line.find(' ', id_start)
            usb_devices.append(line[id_start:id_end])
    
    print(usb_devices)


def trigger_cameras():
    for idx, device in enumerate(usb_devices):
        # print(idx, device)
        shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_file = save_dir + shot_time + "_cam_" + str(idx) + ".jpg"
        subprocess.call([gphoto2, port, device, capture_image_and_download, filename, save_file])

kill_gphoto2_process()
detect_cameras()
trigger_cameras()
# subprocess.call([gphoto2, capture_image_and_download, filename, save_location])
