from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess


gphoto2 = "gphoto2"

shot_date = datetime.now().strftime("%Y-%m-%d")
shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

camera_id = "camera_02/"
save_location = "/home/pi/cm360/gphoto2_images/" + camera_id + shot_time + ".jpg"

filename = "--filename"
capture_image_and_download = "--capture-image-and-download"


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


kill_gphoto2_process()
subprocess.call([gphoto2, capture_image_and_download, filename, save_location])
