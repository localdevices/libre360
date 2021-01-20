import requests
import json

import logging
import platform
import time
import schedule

logger = logging.getLogger(__name__)

# odm360 imports
from odm360.timer import RepeatedTimer
from odm360.camera360serial import Camera360Serial
from odm360.serial_device import SerialDevice
from odm360.utils import find_serial, get_lan_ip, get_lan_devices


def parent_gphoto2(dt, root=".", timeout=1, logger=logger, debug=False):
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
            logger.info("Camera not responding or disconnected")
    camera.exit()


def parent_serial(
    dt,
    project,
    root=".",
    timeout=0.02,
    logger=logger,
    rig_size=1,
    debug=False,
    auto_start=False,
):
    ports = []
    _start = time.time()
    # we are looking for a specified number of cams, default set to 1. After 60 seconds, we give up!
    while (len(ports) < rig_size) and (time.time() - _start < 10):
        ports, descr = find_serial(wildcard="UART", logger=logger)
    if len(ports) < rig_size:
        raise IOError(
            f"Found only {len(ports)} cameras to connect to. Please connect at least {rig_size} cameras"
        )
    logger.info(f"Found {len(ports)} cameras, initializing...")

    # TODO: turn this into a list of devices in a CameraRig object, for now only select the first found
    port, descr = ports[0], descrs[0]
    logger.debug(f"Device {descr} found on port {port}")
    try:
        # initiate a serial connection
        logger.info(f"Starting device via raspi connection.")
        rpi = Camera360Serial(port, timeout=timeout, logger=logger)
        logger.info(f"Opening port {rpi.port} for reading")
        # # open the uart connection to raspi and see if we get a serial object back
        rpi.open_serial()
        # let the raspi camera know that it can start by providing a root folder to store photos in
        start = False
        while not (start):
            try:
                rpi._to_serial({"root": root})
                time.sleep(1)
                if rpi._from_serial() == "received":
                    start = True
                rpi.init()
            except:
                pass
        try:
            timer = RepeatedTimer(dt, rpi.capture)
        except:
            logger.error("Camera not responding or disconnected")
            timer.stop()
            rpi.exit()
            rpi.close_serial_device()

    except Exception as e:
        logger.exception(e)


def child_tcp_ip(
    timeout=1.0, logger=logger, host=None, port=5000, debug=False, timeoff=60.0
):
    """
    Start a child in tcp ip mode. Can handle multiplexing

    :param dt: time interval between photos
    :param root: name of root folder to store photos in (None, needs to come from server
    :param timeout: time in seconds to wait until next call to server is made
    :param logger: logger object
    :param port: port number to host server
    :param timeoff: maximum time allowed for no responses to assume server-client connection is still available
    :return:
    """
    from odm360.camera360pi import Camera360Pi, device_uuid, device_name

    # only load Camera360Pi in a child. A parent may not have this lib
    ip = get_lan_ip()  # retrieve child's IP address
    logger.debug(f"My IP address is {ip}")
    headers = {"Content-type": "application/json"}
    if host is None:
        all_ips = get_lan_devices(
            ip
        )  # find all IPs on the current network interface and loop over them
    else:
        all_ips = [(host, "up")]
    # initiate the state of the child as 'idle'
    log_msg = ""  # start with an empty msg
    state = {
        "status": "offline",
        "ip": ip,
        "device_uuid": device_uuid,
        "device_name": device_name,
        "req_time": time.time(),
        "success_time": time.time(),
        "last_photo": "",
    }
    get_project_msg = {"state": state, "req": "ONLINE"}
    # try to get in contact with the right host
    logger.debug("Initializing search for server")
    # host_found = False
    while True:
        if state["status"] == "offline":
            # while not (host_found):
            for host, status in all_ips:
                try:
                    r = requests.get(
                        f"http://{host}:{port}/picam",
                        data=json.dumps(get_project_msg),
                        headers=headers,
                    )
                    # logger.debug(f'Received {r.text}')
                    msg = r.json()
                    if "task" in msg:
                        # ip address with server found! make this a constraint for all further msgs.
                        all_ips = [(host, status)]
                        # state becomes idle!
                        state["status"] = "idle"
                        # setup camera object
                        if not ("camera" in locals()):
                            try:
                                camera = Camera360Pi(
                                    state,
                                    logger=logger,
                                    debug=debug,
                                    host=host,
                                    port=port,
                                )  # start without any project info, **msg['project'])
                            except:
                                raise IOError(
                                    "There was a problem setting up the picamera. Check if you have enough GPU memory allocated, and the picamera interface opened."
                                )
                        else:
                            # camera exists, contact is made so set status back to idle
                            camera.state["status"] = "idle"
                            camera.state["success_time"] = time.time()
                        # state['status'] = camera.state
                        logger.info(f"Found host on {host}:{port}")
                        break
                    else:
                        logger.debug(f"No suitable answer so skipping going online")

                except:
                    # sleep for 2 seconds before trying again
                    time.sleep(2)
        else:
            # we have contact, now continuously ask for information and report back
            try:
                # update req_time
                camera.state["req_time"] = time.time()
                # ask for a task
                get_task_msg = {
                    "state": camera.state,
                    "req": "TASK",
                }
                r = requests.get(
                    f"http://{host}:{port}/picam",
                    data=json.dumps(get_task_msg),
                    headers=headers,
                )
                logger.debug(f"Received {r.text}")
                msg = r.json()
                task = msg["task"]
                kwargs = msg["kwargs"]
                f = getattr(camera, task)
                # execute function with kwargs provided
                log_msg = f(**kwargs)
                # update status to camera.state
                # state['status'] = camera.state
                post_log_msg = {
                    "kwargs": log_msg,
                    "req": "LOG",
                    "state": camera.state,
                }
                r = requests.post(
                    f"http://{host}:{port}/picam",
                    data=json.dumps(post_log_msg),
                    headers=headers,
                )
                success = r.json()
                if success["success"]:
                    logger.debug("POST was successful")
                else:
                    logger.error("POST was not successful")
                # FIXME: implement capture_continuous method on Camera360Pi side
                camera.state["success_time"] = time.time()
            except Exception as e:
                if time.time() - camera.state["success_time"] > timeoff:
                    # logger.exception(e)
                    logger.warning(
                        "It seems the server went offline or provided an incorrect message back, switching to offline state."
                    )
                    if camera.state["status"] != "offline":
                        # go offline if not already so!
                        camera.stop()
                        camera.state["status"] = "offline"
                else:
                    logger.warning("No contact with server, trying again for some time")
            time.sleep(timeout)
            state = camera.state


def child_serial(timeout=1.0, logger=logger, port="/dev/ttySO", deub=False):
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

    if platform.node() == "raspberrypi":
        pass
    else:
        raise OSError("This function must be deployed on a raspberry pi")
    # initiate a  object
    logger.info(f"Starting raspi object on {port}.")
    try:
        rpi = SerialDevice(
            port, timeout=0.01
        )  # let child communicate with 100Hz frequency so that no messages are missed
        logger.info(f"Opening port {rpi.port} for listening.")
        # # open the uart connection to raspi and see if we get a serial object back
        rpi.open_serial()
        # starting the Camera object once a {'root': <NAME>} is passed through
        start = False
        logger.info("Waiting for root folder to start camera")
        while not (start):
            try:
                p = rpi._from_serial()
                if "root" in p:
                    start = True
                    rpi._to_serial("received")
                else:
                    raise IOError("Received a wrong signal. Please restart the rig.")
            except:
                pass
        logger.info(f'Root folder provided as {p["root"]}')
        # now root folder is passed, open the camera
        camera = Camera360Pi(root=p["root"], logger=logger)
        _action = False  # when action is True, something should or should have been done, otherwise just listen
        while True:
            try:
                p = rpi._from_serial()
                _action = True
                logger.info(f'Received command "{p}"')
                # a method is received, pass it to the appropriate method in camera object
                method = p["name"]
                kwargs = p["kwargs"]
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
