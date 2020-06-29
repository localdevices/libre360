"""
This example connects automatically to a raspberry pi (first one found on ports) and commands it through serial msgs.
On the raspberry pi side, a receiving script should run (raspi_receive.py)
"""

from odm360.log import setuplog
from odm360.camera360serial import Camera360Serial
from odm360.utils import find_serial
# start a logger with defined log levels. This may be used in our main call
verbose = 2
quiet = 0
log_level = max(10, 30 - 10 * (verbose - quiet))

logger = setuplog("odm360", "odm360.log", log_level=log_level)
logger.info("starting...")

ports, descr = find_serial(wildcard='UART')
port, descr = ports[0], descr[0]
logger.info(f'Device {descr} found on port {port}')
try:
    # initiate a serial connection
    logger.info(f"Starting device via raspi connection.")
    rpi = Camera360Serial(port, timeout=1)
    logger.info(f"Opening port {rpi.port} for reading")
    # # open the uart connection to raspi and see if we get a serial object back
    rpi.open_serial()
    rpi.init()
    rpi.capture()
    rpi.exit()
    rpi.close_serial_device()

except Exception as e:
    logger.exception(e)
