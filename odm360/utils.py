import serial
import logging
logger = logging.getLogger(__name__)

def find_serial(wildcard='', logger=logger):
    """
    Looks for serial devices in all active serial ports

    :param wildcard: str - wildcard used to look for serial device (default: empty)
    """
    ps = list(serial.tools.list_ports.comports())
    ports = []
    descr = []
    for p in ps:
        port = p[0]
        description = p[1]
        if wildcard.lower() in description.lower():
            logger.info(f'Found {description} on port {port}')
            ports.append(port)
            descr.append(description)
    return ports, descr
