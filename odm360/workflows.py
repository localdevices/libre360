from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import platform
import time
import schedule
import gphoto2 as gp

logger = logging.getLogger(__name__)

# odm360 imports
from odm360.timer import RepeatedTimer
from odm360.camera360server import Camera360Server
from odm360.camera360serial import Camera360Serial
from odm360.serial_device import SerialDevice
from odm360.utils import find_serial, get_lan_ip

def parent_gphoto2(dt, root='.', timeout=1, logger=logger):
    """

    :param logger:
    :return:
    """
    # only import gphoto2 when necessary
    from odm360.camera360gphoto import Camera360G
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

def parent_server(dt, root='.', timeout=0.02, logger=logger, n_cams=2, wait_time=12000, port=8000):
    """

    :param dt:
    :param root:
    :param timeout:
    :param logger:
    :param rig_size:
    :return:
    """
    # https://docs.python.org/3/library/http.server.html
    # https://www.afternerd.com/blog/python-http-server/
    # https://gist.github.com/nitaku/10d0662536f37a087e1b seems the best case for our uses

    children = []
    _start = time.time()
    # find own ip address
    ip = get_lan_ip()
    # all_ips = get_lan_devices(ip)
    # sel = selectors.DefaultSelector()  # handler for multiplexing
    n_clients = 0  # amount of connections
    port = 8001

    # set a number of properties to Camera360Server
    Camera360Server.logger = logger
    Camera360Server.n_cams = n_cams
    Camera360Server.root = root
    server_address = (ip, port)
    httpd = HTTPServer(server_address, Camera360Server)
    logger.info(f'odm360 listening on {ip}:{port}')
    httpd.serve_forever()


def parent_serial(dt, root='.', timeout=0.02, logger=logger, rig_size=1):
    ports = []
    _start = time.time()
    # we are looking for a specified number of cams, default set to 1. After 60 seconds, we give up!
    while (len(ports) < rig_size) and (time.time()-_start < 10):
        ports, descr = find_serial(wildcard='UART', logger=logger)
    if len(ports) < rig_size:
        raise IOError(f'Found only {len(ports)} cameras to connect to. Please connect at least {rig_size} cameras')
    logger.info(f'Found {len(ports)} cameras, initializing...')

    # TODO: turn this into a list of devices in a CameraRig object, for now only select the first found
    port, descr = ports[0], descr[0]
    logger.debug(f'Device {descr} found on port {port}')
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
        # start timer
        try:
            timer = RepeatedTimer(dt, rpi.capture)
        except:
            logger.error('Camera not responding or disconnected')
            timer.stop()
            rpi.exit()
            rpi.close_serial_device()

    except Exception as e:
        logger.exception(e)

def child_rpi(dt, root='.', timeout=1., logger=logger):
    # only lead Camera360Pi in a child. A parent may not have this lib
    from odm360.camera360pi import Camera360Pi
    if platform.node() == 'raspberrypi':
        port = '/dev/ttyS0'
    else:
        raise OSError('This function must be deployed on a raspberry pi')
    # initiate a  object
    logger.info(f"Starting raspi object on {port}.")
    try:
        rpi = SerialDevice(port,
                           timeout=0.01)  # let child communicate with 100Hz frequency so that no messages are missed
        logger.info(f"Opening port {rpi.port} for listening.")
        # # open the uart connection to raspi and see if we get a serial object back
        rpi.open_serial()
        # starting the Camera object once a {'root': <NAME>} is passed through
        start = False
        logger.info('Waiting for root folder to start camera')
        while not (start):
            try:
                p = rpi._from_serial()
                if 'root' in p:
                    start = True
                else:
                    raise IOError('Received a wrong signal. Please restart the rig.')
            except:
                pass
        logger.info(f'Root folder provided as {p["root"]}')
        # now root folder is passed, open the camera
        camera = Camera360Pi(root=p['root'], logger=logger)
        _action = False  # when action is True, something should or should have been done, otherwise just listen
        while True:
            try:
                p = rpi._from_serial()
                _action = True
                logger.info(f'Received command "{p}"')
                # a method is received, pass it to the appropriate method in camera object
                method = p['name']
                kwargs = p['kwargs']
                f = getattr(camera, method)
                # execute function with kwargs provided
                response = f(**kwargs)
                # give feedback if everything worked out
                # TODO: extend feedback with dictionary with time info, name of file, and so on, only file name so far
                rpi._to_serial(camera.dst_fn)
            except:
                # error messages are handled in the specific functions. Provide feedback back to the main
                if _action:
                    # apparently an action was tried, but failed in the try loop
                    rpi._to_serial(None)  #
            _action = False  # set _action back to False to wait for the next action

    except Exception as e:
        logger.exception(e)
