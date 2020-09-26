import logging
import time
from flask import request, current_app
import numpy as np
import datetime
from odm360 import dbase, utils
from odm360.states import states

logger = logging.getLogger(__name__)

# def CameraRig(ip, project, root='.', n_cams=1, dt=5, auto_start=False, logger=logger):
#     # start an empty rig object
#     # add a number of properties to CameraRig
#     rig = {}
#     rig['ip'] = ip
#     rig['project'] = project
#     rig['root'] = root  # root folder to store photos
#     rig['n_cams'] = n_cams  # number of cameras to expect
#     rig['dt'] = dt # time interval of captures
#     rig['auto_start'] = auto_start  # True: automatically start server forever, False: allow interaction with server object
#     # initialize camera states
#     rig['start_time'] = None  # start time of capture thread
#     if auto_start:
#         rig['stop'] = False  # stop sign, automatically start capturing (TODO implement this with interactive server)
#     else:
#         rig['stop'] = True # initialize rig without starting capturing of pics, until called from interface
#     rig['cam_state'] = {}  # status of cameras, always passed by cameras with GET requests
#     rig['cam_logs'] = {}  # last log of cameras, always passed by cameras with POST requests
#     current_app.config['rig'] = rig
#
# def start_rig():
#     config = current_app.config['config']
#     kwargs = {
#         'ip': current_app.config['ip'],
#         'project': config['project'],
#         'root': config['root'],
#         'n_cams': int(config['n_cams']),
#         'dt': int(config['dt']),
#         'logger': logger,
#         'auto_start': False
#     }
#     # setup rig
#     CameraRig(**kwargs)
#     print('Rig started')

def get_project(cur):
    """
    :return:
    dict representation of the root folder
    """
    cur_project = dbase.query_project_active(cur, as_dict=True)
    # retrieve project with project_id
    if len(cur_project) == 0:
        return  {'task': 'wait',
                'kwargs': {}
                }

    logger.info(f"Giving project {cur_project['project_id']} to Cam {request.remote_addr}")
    project = dbase.query_projects(cur, project_id=cur_project['project_id'], as_dict=True, flatten=True)
    return {'project': project}

def get_task(cur):
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
    rig = dbase.query_project_active(cur, as_dict=True)

    # if rig['start_time'] is not None:
    #     if time.time() > rig['start_time'] + 10:
    #         rig['status'] = 1  # go back to status 'ready' # TODO remove once tested
    cur_address = request.remote_addr
    cur_device = dbase.query_devices(cur, device_name=cur_address, as_dict=True, flatten=True)
    print(f'CUR DEVICE IS {cur_device}')
    # get states of parent and child in human readable format
    device_status = utils.get_key_state(cur_device['status'])
    rig_status = utils.get_key_state(rig['status'])
    print(f'DEVICE STATE IS {device_status} and RIG STATE IS {rig_status}')

    if device_status != rig_status:
        # something needs to be done to get the states the same
        if (device_status == 'idle') and (rig_status == 'ready'):
            # initialize the camera
            logger.info('Sending camera initialization ')
            return {'task': 'init',
                    'kwargs': {}
                    }
        elif (device_status == 'ready') and (rig_status == 'capture'):
            return activate_camera(cur)

        elif (device_status == 'capture') and (rig_status == 'ready'):
            return {'task': 'stop',
                    'kwargs': {}
                    }
        # camera is already capturing, so just wait for further instructions (stop)
    return {'task': 'wait',
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

def activate_camera(cur):
    # retrieve settings of current project
    cur_project = dbase.query_project_active(cur, as_dict=True)
    project = dbase.query_projects(cur, project_id=cur_project['project_id'], as_dict=True, flatten=True)

    cur_address = request.remote_addr  # TODO: also add uuid of device
    # check how many cams have the state 'ready', only start when the full rig is ready
    n_cams_ready = len(dbase.query_devices(cur, status=states['ready']))


    # compute cams ready from a PostGreSQL query
    if n_cams_ready == project['n_cams']:
        logger.info(f'All cameras ready. Start capturing on {cur_address}')
        # no start time has been set yet, ready to start the time
        logger.debug('All cameras are ready, setting start time')

        start_time_epoch = time.time() + 10  # this number is send to the child to start capturing
        start_datetime = datetime.datetime.fromtimestamp(start_time_epoch)
        start_datetime_utc = utils.to_utc(start_datetime)

        # set start time for capturing, and set state to capture
        dbase.update_project_active(cur, status=states['capture'], start_time=start_datetime_utc)
        logger.debug(f'start time is set to {start_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S")}')
        logger.info(f'Sending capture command to {cur_address}')
        return {'task': 'capture_continuous',
                'kwargs': {'start_time': start_time_epoch}
                }
    else:
        logger.debug(f'Only {n_cams_ready} out of {project["n_cams"]} ready for capture, waiting...')
        return {'task': 'wait',
                'kwargs': {}
                }
    # TODO check wait
