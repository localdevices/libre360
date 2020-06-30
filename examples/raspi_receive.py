"""
This example is for letting a raspberry pi (child) listen and respond to incoming msgs.
On the Parent side, after this script is started, a orchastrator should run (raspi_connect.py)


"""
import platform
from odm360.log import setuplog
from odm360.serial_device import SerialDevice
from odm360.camera360pi import Camera360Pi
# start a logger with defined log levels. This may be used in our main call
verbose = 2
quiet = 0
log_level = max(10, 30 - 10 * (verbose - quiet))
if platform.node() == 'raspberrypi':
    port = '/dev/ttyS0'
else:
    raise OSError('This function must be deployed on a raspberry pi')

logger = setuplog("odm360_child", "odm360_child.log", log_level=log_level)
logger.info("starting...")

try:
    # initiate a  object
    logger.info(f"Starting raspi object on {port}.")
    rpi = SerialDevice(port, timeout=0.01)  # let child communicate with very high frequency so that no messages are missed
    logger.info(f"Opening port {rpi.port} for listening.")
    # # open the uart connection to raspi and see if we get a serial object back
    rpi.open_serial()
    # starting the Camera object once a {'root': <NAME>} is passed through
    start = False
    logger.info('Waiting for root folder to start camera')
    while not(start):
        try:
            p = rpi._from_serial()
            if 'root' in p:
                start = True
            else:
                raise('Received a wrong signal. Please restart the rig.')
        except:
            pass
    logger.info(f"Root folder provided as {p['root']}")
    camera = Camera360Pi(root=p['root'], logger=logger)
    _action = False  # when action is True, something should or should have been done, otherwise just listen
    while True:
        try:
            p = rpi._from_serial()
            _action = True
            # if p != "":
            logger.info(f'Received command "{p}"')
            # a method is received, pass it to the appropriate method in camera object
            method = p['name']
            kwargs = p['kwargs']
            f = getattr(camera, method)
            # # execute function with kwargs provided
            f(**kwargs)
            # give feedback if everything worked out
            # TODO: extend feedback with dictionary with time info, name of file, and so on
            rpi._to_serial(camera.dst_fn)
        except:
            # error messages are handled in the specific functions. Provide feedback back to the main
            if _action:
                rpi._to_serial(False)  #
        _action = False

except Exception as e:
    logger.exception(e)
