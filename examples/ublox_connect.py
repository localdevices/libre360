from odm360 import ublox
from odm360.log import setuplog
from odm360.utils import find_serial
# start a logger with defined log levels. This may be used in our main call
verbose = 2
quiet = 0
log_level = max(10, 30 - 10 * (verbose - quiet))

logger = setuplog("odm360", "odm360.log", log_level=log_level)
logger.info("starting...")

try:
    # initiate a ublox object
    logger.info(f"Starting uBlox instance.")
    ports, descr = find_serial('u-blox')
    gps = ublox.Ublox(ports[0])
    logger.info(f"Opening port {gps.port} for reading")
    # open the ublox connection and see if we get a serial object back
    gps.open_serial()

    # try to read a line and print it
    txt = gps._from_serial_txt()
    logger.info(txt)

    # gracefully close the object
    gps.close_serial_device()

except Exception as e:
    logger.exception(e)
