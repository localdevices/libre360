import logging
import time
import schedule

import gphoto2 as gp
from odm360.camera360gphoto import Camera360G

logger = logging.getLogger(__name__)

# odm360 imports
from odm360.camera360serial import Camera360Serial
from odm360.utils import find_serial

def parent_gphoto2(dt, root='.', timeout=1, logger=logger):
    """

    :param logger:
    :return:
    """
    camera_list = list(gp.Camera.autodetect())
    rig = [Camera360G(addr=addr) for name, addr in camera_list]
    # TODO expand to a full rig and continuous photos
    camera = rig[0]
    print(camera.get_port_info())
    camera.init()
    schedule.every(dt).seconds.do(camera.capture(timeout=timeout))
    while True:
        try:
            schedule.run_pending()
        except:
            logger.info('Camera not responding or disconnected')
    camera.exit()


def parent_serial(dt, root='.', timeout=1, logger=logger):
    ports, descr = find_serial(wildcard='UART', logger=logger)
    if len(ports) == 0:
        raise IOError('No serial devices (raspberry pi) found, please connect at least one serial device')
    # TODO: turn this into a list of devices in a CameraRig object, for now only select the first found
    # TODO: ensure this is tried several times until sufficient ports are found. It takes a while to boot the raspis
    port, descr = ports[0], descr[0]
    logger.info(f'Device {descr} found on port {port}')
    try:
        # initiate a serial connection
        logger.info(f"Starting device via raspi connection.")
        rpi = Camera360Serial(port, timeout=timeout, logger=logger)
        logger.info(f"Opening port {rpi.port} for reading")
        # # open the uart connection to raspi and see if we get a serial object back
        rpi.open_serial()
        # let the raspi camera know that it can start by providing a root folder to store photos in
        rpi._to_serial({'root': root})
        time.sleep(1)
        rpi.init()
        # TODO: replace this scheduler with something like https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds/13151299
        schedule.every(dt).seconds.do(rpi.capture)
        while True:
            try:
                schedule.run_pending()
            except:
                logger.info('Camera not responding or disconnected')

        rpi.capture()
        rpi.exit()
        rpi.close_serial_device()

    except Exception as e:
        logger.exception(e)

def child_rpi(dt, root='.', timeout=1., logger=logger):
    pass
