from http.server import HTTPServer
import requests
import json

import logging
import platform
import time
import schedule
import gphoto2 as gp

logger = logging.getLogger(__name__)

# odm360 imports
from odm360.timer import RepeatedTimer
from odm360.camera360server import make_Camera360Server
from odm360.camera360serial import Camera360Serial
from odm360.serial_device import SerialDevice
from odm360.utils import find_serial, get_lan_ip, get_lan_devices

class CameraRig():
    def __init__(self, ip, port, root='.', n_cams=1, logger=logger):
        # add a number of properties to CameraRig
        self.ip = ip
        self.port = port
        self.root = root  # root folder to store photos
        self.n_cams = n_cams  # number of cameras to expect
        self.logger = logger  # logger object
        # initialize camera states
        self.start_time = None  # start time of capture thread
        self.stop = False  # stop sign (TODO implement this with a GPIO push button)
        self.cam_state = {}  # status of cameras, always passed by cameras with GET requests
        self.cam_logs = {}  # last log of cameras, always passed by cameras with POST requests

    def start_server(self):
        server_handler = make_Camera360Server(self)
        httpd = HTTPServer((self.ip, self.port), server_handler)
        logger.info(f'odm360 server listening on {self.ip}:{self.port}')
        httpd.serve_forever()



def parent_gphoto2(dt, root='.', timeout=1, logger=logger, debug=False):
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

def parent_server(dt, root='.', logger=logger, n_cams=2, wait_time=12000, port=8000, debug=False):
    """

    :param dt: time interval between photos
    :param root: name of root folder to store photos in
    :param logger: logger object
    :param n_cams: number of cameras to expect (capturing will not commence before this amount is reached)
    :param wait_time: time to wait until all cameras are online, stop when this is not reached in time
    :param port: port number to host server

    :return:
    """
    _start = time.time()
    # find own ip address
    ip = get_lan_ip()

    # # set a number of properties to Camera360Server
    # server_props =
    # Camera360Server.logger = logger
    # Camera360Server.n_cams = n_cams
    # Camera360Server.root = root
    # Camera360Server.stop = True

    # setup server
    server_address = (ip, port)
    rig = CameraRig(ip, port, root=root, n_cams=n_cams, logger=logger)
    rig.start_server()


def parent_serial(dt, root='.', timeout=0.02, logger=logger, rig_size=1, debug=False):
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

def child_tcp_ip(dt, root=None, timeout=1., logger=logger, port=8000, debug=False):
    """
    Start a child in tcp ip mode. Can handle multiplexing

    :param dt: time interval between photos
    :param root: name of root folder to store photos in (None, needs to come from server
    :param timeout: time in seconds to wait until next call to server is made
    :param logger: logger object
    :param port: port number to host server
    :return:
    """
    # only load Camera360Pi in a child. A parent may not have this lib
    from odm360.camera360pi import Camera360Pi
    ip = get_lan_ip()  # retrieve child's IP address
    logger.debug(f'My IP address is {ip}')
    headers = {'Content-type': 'application/json'}
    #all_ips = get_lan_devices(ip)  # find all IPs on the current network interface
    all_ips = [('192.168.178.174', 'up')]
    # initiate the state of the child as 'idle'
    log_msg = ''  # start with an empty msg
    state = 'idle'
    get_root_msg = {'state': state,
                    'req': 'ROOT'
                    }
    # try to get in contact with the right host
    logger.debug('Initializing search for server')
    host_found = False
    while not(host_found):
        for host, status in all_ips:
            try:
                r = requests.get(f'http://{host}:{port}',
                                 data=json.dumps(get_root_msg),
                                 headers=headers
                                 )
                logger.debug(f'Received {r.text}')
                msg = r.json()
                if 'root' in msg:
                    # setup camera object
                    camera = Camera360Pi(root=msg['root'], logger=logger, debug=debug, host=host, port=port)
                    state = camera.state
                    logger.info(f'Found host on {host}:{port}')
                    host_found = True
                    break
                else:
                    # msg retrieved does not contain 'root', therefore throw error msg
                    raise ValueError(f'Expected "root" as answer, but instead got {r.text}')
            except:
                pass
    # we have contact, now continuously ask for information and report back
    try:
        while True:
            # ask for a task
            get_task_msg = {'state': camera.state,
                            'req': 'TASK'
                            }
            r = requests.get(f'http://{host}:{port}',
                             data=json.dumps(get_task_msg),
                             headers=headers
                             )
            logger.debug(f'Received {r.text}')
            msg = r.json()
            task = msg['task']
            kwargs = msg['kwargs']
            f = getattr(camera, task)
            # execute function with kwargs provided
            log_msg = f(**kwargs)
            state = camera.state
            post_log_msg = {'kwargs': log_msg,
                            'req': 'LOG'
                            }
            r = requests.post(f'http://{host}:{port}', data=json.dumps(post_log_msg), headers=headers)
            success = r.json()
            if success['success']:
                logger.debug('POST was successful')
            else:
                logger.error('POST was not successful')
            time.sleep(timeout)
            # FIXME: implement capture_continuous method on Camera360Pi side
    except Exception as e:
        logger.exception(e)

def child_serial(dt, root=None, timeout=1., logger=logger, port='/dev/ttySO', deub=False):
    """
    Start a child in serial mode, instructed by parent through UART. Can currently only handle one child
    :param dt: time interval between photos
    :param root: name of root folder to store photos in (None, needs to come from server
    :param timeout: time in seconds to wait until next call to server is made
    :param logger: logger object
    :param port: port number to host server

    :return:
    """

    # only load Camera360Pi in a child. A parent may not have this lib
    from odm360.camera360pi import Camera360Pi
    if platform.node() == 'raspberrypi':
        pass
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
