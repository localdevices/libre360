import logging
import time
from flask import request
import numpy as np
import datetime

logger = logging.getLogger(__name__)

class CameraRig():
    def __init__(self, ip, project, root='.', n_cams=1, dt=5, auto_start=False, logger=logger):
        # add a number of properties to CameraRig
        self.ip = ip
        self.project = project
        self.root = root  # root folder to store photos
        self.n_cams = n_cams  # number of cameras to expect
        self.dt = dt # time interval of captures
        self.logger = logger  # logger object
        self.auto_start = auto_start  # True: automatically start server forever, False: allow interaction with server object
        # initialize camera states
        self.start_time = None  # start time of capture thread
        if auto_start:
            self.stop = False  # stop sign, automatically start capturing (TODO implement this with interactive server)
        else:
            self.stop = True # initialize rig without starting capturing of pics, until called from interface
        self.cam_state = {}  # status of cameras, always passed by cameras with GET requests
        self.cam_logs = {}  # last log of cameras, always passed by cameras with POST requests

    def get_root(self):
        """
        :return:
        dict representation of the root folder
        """
        self.logger.info(f'Giving root {self.root} to Cam {request.remote_addr}')
        return {'root': self.root}

    def get_task(self):
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
        if self.start_time is not None:
            if time.time() > self.start_time + 10:
                self.stop = True
        cur_address = request.remote_addr
        state = self.cam_state[cur_address]
        if state == 'idle':
            # initialize the camera
            self.logger.info('Sending camera initialization ')
            return {'task': 'init',
                    'kwargs': {}
                    }
        elif state == 'ready':
            if not(self.stop):
                return self.activate_camera()

        elif state == 'capture':
            if self.stop:
                return {'task': 'stop',
                        'kwargs': {}
                        }
            # camera is already capturing, so just wait for further instructions (stop)
        return {'task': 'notready',
                'kwargs': {}
                }

    def post_log(self, msg, level='info'):
        """
        Log message from current camera on logger
        :return:
        dict {'success': False or True}
        """
        try:
            cur_address = request.remote_addr
            log_msg = f'Cam {cur_address} - {msg}'
            log_method = getattr(self.logger, level)
            log_method(log_msg)
            return {'success': True}
        except:
            return {'success': False}

    def activate_camera(self):
        cur_address = request.remote_addr
        # check how many cams have the state 'ready', only start when the full rig is ready
        n_cams_ready = np.sum([self.cam_state[s] == 'ready' for s in self.cam_state])
        if n_cams_ready == self.n_cams:
            self.logger.info(f'All cameras ready. Start capturing on {cur_address}')
            # no start time has been set yet, ready to start the time
            self.logger.debug('All cameras are ready, setting start time')
            self.start_time = self.dt * round((time.time() + 10) / self.dt)
            self.start_datetime = datetime.datetime.fromtimestamp(self.parent.start_time)
            self.logger.debug(f'start time is set to {self.parent.start_datetime}')
            self.logger.info(f'Sending capture command to {cur_address}')
            return {'task': 'capture_continuous',
                    'kwargs': {'start_time': self.parent.start_time}
                    }
        else:
            self.logger.debug(f'Only {n_cams_ready} out of {self.n_cams} ready for capture, waiting...')
            return {'task': 'wait',
                    'kwargs': {}
                    }
        # TODO check wait
