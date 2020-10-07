import gphoto2 as gp
from odm360 import camera360gphoto
from odm360.log import setuplog

camera_list = list(gp.Camera.autodetect())
rig = [camera360gphoto.Camera360G(addr=addr) for name, addr in camera_list]
camera = rig[0]

# start a logger with defined log levels. This may be used in our main call
verbose = 2
quiet = 0
log_level = max(10, 30 - 10 * (verbose - quiet))

logger = setuplog("odm360", "odm360.log", log_level=log_level)
logger.info("starting...")

print(camera.get_port_info())
camera.init()

text = camera.get_summary()
print("Summary")
print("=======")
print(str(text))
camera.capture_until(timeout=1)
camera.exit()
