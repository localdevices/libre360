import logging
import time
from flask import request, current_app
import numpy as np
import datetime

logger = logging.getLogger(__name__)

def CameraRig(ip, project, root='.', n_cams=1, dt=5, auto_start=False, logger=logger):
    # start an empty rig object
    # add a number of properties to CameraRig
    rig = {}
    rig['ip'] = ip
    rig['project'] = project
    rig['root'] = root  # root folder to store photos
    rig['n_cams'] = n_cams  # number of cameras to expect
    rig['dt'] = dt # time interval of captures
    rig['auto_start'] = auto_start  # True: automatically start server forever, False: allow interaction with server object
    # initialize camera states
    rig['start_time'] = None  # start time of capture thread
    if auto_start:
        rig['stop'] = False  # stop sign, automatically start capturing (TODO implement this with interactive server)
    else:
        rig['stop'] = True # initialize rig without starting capturing of pics, until called from interface
    rig['cam_state'] = {}  # status of cameras, always passed by cameras with GET requests
    rig['cam_logs'] = {}  # last log of cameras, always passed by cameras with POST requests
    current_app.config['rig'] = rig

def start_rig():
    config = current_app.config['config']
    kwargs = {
        'ip': current_app.config['ip'],
        'project': config['project'],
        'root': config['root'],
        'n_cams': int(config['n_cams']),
        'dt': int(config['dt']),
        'logger': logger,
        'auto_start': False
    }
    # setup rig
    CameraRig(**kwargs)
    print('Rig started')

def get_root():
    """
    :return:
    dict representation of the root folder
    """
    logger.info(f'Giving root {current_app.config["rig"]["root"]} to Cam {request.remote_addr}')
    return {'root': current_app.config["rig"]["root"]}

def get_task():
    """
    Choose a task for the child to perform, and return this
    Currently implemented are:
        init: - initialize camera (done when status of camera is 'idle')
        wait: - tell camera to simply wait and send a request for a task later (typically done when not all cameras are online yet
        capture_until: - capture until a stop (not implemented yet) is given, using kwargs for time and time intervals
                         this is only provided when all cameras in the expected camera rig size are initialized
    :return:
    dict representation of task, including the following fields:
    task: str - name of task method to be performed on child side
    kwargs: dict - set of key word arguments and their values to provide to that task
    """
    # TODO: remove the automatic stopping after 10 secs
    if current_app.config['rig']['start_time'] is not None:
        if time.time() > current_app.config['rig']['start_time'] + 10:
            current_app.config['rig']['stop'] = True
    cur_address = request.remote_addr
    state = current_app.config['rig']['cam_state'][cur_address]
    if state == 'idle':
        # initialize the camera
        logger.info('Sending camera initialization ')
        return {'task': 'init',
                'kwargs': {}
                }
    elif state == 'ready':
        if not(current_app.config['rig']['stop']):
            return activate_camera()

    elif state == 'capture':
        if current_app.config['rig']['stop']:
            return {'task': 'stop',
                    'kwargs': {}
                    }
        # camera is already capturing, so just wait for further instructions (stop)
    return {'task': 'notready',
            'kwargs': {}
            }

def post_log(msg, level='info'):
    """
    Log message from current camera on logger
    :return:
    dict {'success': False or True}
    """
    try:
        cur_address = request.remote_addr
        log_msg = f'Cam {cur_address} - {msg}'
        log_method = getattr(logger, level)
        log_method(log_msg)
        return {'success': True}
    except:
        return {'success': False}

def activate_camera():
    cur_address = request.remote_addr
    # check how many cams have the state 'ready', only start when the full rig is ready
    n_cams_ready = np.sum([current_app.config['rig']['cam_state'][s] == 'ready' for s in current_app.config['rig']['cam_state']])
    if n_cams_ready == current_app.config['rig']['n_cams']:
        logger.info(f'All cameras ready. Start capturing on {cur_address}')
        # no start time has been set yet, ready to start the time
        logger.debug('All cameras are ready, setting start time')
        current_app.config['rig']['start_time'] = current_app.config['rig']['dt'] * round((time.time() + 10) / current_app.config['rig']['dt'])
        current_app.config['rig']['start_datetime'] = datetime.datetime.fromtimestamp(current_app.config['rig']['start_time'])
        logger.debug(f'start time is set to {current_app.config["rig"]["start_datetime"]}')
        logger.info(f'Sending capture command to {cur_address}')
        return {'task': 'capture_continuous',
                'kwargs': {'start_time': current_app.config['rig']['start_time']}
                }
    else:
        logger.debug(f'Only {n_cams_ready} out of {current_app.config["rig"]["n_cams"]} ready for capture, waiting...')
        return {'task': 'wait',
                'kwargs': {}
                }
    # TODO check wait
