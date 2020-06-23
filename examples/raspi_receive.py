import platform
from odm360.log import setuplog
from odm360.serial_device import SerialDevice
# start a logger with defined log levels. This may be used in our main call
verbose = 2
quiet = 0
log_level = max(10, 30 - 10 * (verbose - quiet))
if platform.node() == 'raspberrypi':
    port = '/dev/ttyS0'
else:
    raise OSError('This function must be deployed on a raspberry pi')

logger = setuplog("odm360_slave", "odm360_slave.log", log_level=log_level)
logger.info("starting...")

try:
    # initiate a  object
    logger.info(f"Starting raspi object on {port}.")
    rpi = SerialDevice(port, timeout=1.)
    logger.info(f"Opening port {rpi.port} for listening.")
    # # open the uart connection to raspi and see if we get a serial object back
    rpi.open_serial()
    # starting the Camera object
    # TODO start the camera
    while True:
        try:
            txt = rpi._from_serial_txt()
            if txt != "":
                # TODO implement the actual camera connection with raspi camera, methods are below in commented lines
                # # a non-empty string is received, pass it to the appropriate method
                # f = getattr(camera, txt)
                # # execute function
                # f()
                # # give feedback if everything worked out
                rpi._to_serial("0")
        except:
            # error messages are handled in the specific functions. Provide feedback back to the main
            rpi._to_serial("-1")
            pass

except Exception as e:
    logger.exception(e)
