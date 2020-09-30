import os
import time
import logging
import json
import requests

logger = logging.getLogger(__name__)
from datetime import datetime
from odm360.timer import RepeatedTimer
try:
    from picamera import PiCamera
except:
    class PiCamera:
        def __init__(self):
            pass

class Camera360Pi(PiCamera):
    """
    This class is for increasing the functionalities of the Camera class of PiCamera specifically for
    the 360 camera use case.
    """
    def __init__(self, logger=logger, debug=False, host=None, port=None, project_id=None, project_name=None, n_cams=None, dt=None):
        self.debug = debug
        self.state = 'idle'
        self.timer = None
        self._root = 'photos'
        self._project_id = project_id  # project_id for the entire project from parent
        self._project_name = project_name  # human-readable name
        self._n_cams = n_cams  # total amount of cameras related to this project
        self._dt = dt  # time intervals requested by parent
        self.src_fn = None  # path to currently made photo (source) inside the camera
        self.dst_fn = ''  # path to photo (destination) on drive
        self.logger = logger
        self.id = None  # TODO: give a uniue ID to each camera (once CameraRig is defined, complete)
        self.name = None  # TODO: give a name to each camera (once CameraRig is defined, complete)
        self.host = host
        self.port = port
        if not(os.path.isdir(self._root)):
            os.makedirs(self._root)
        super().__init__()
        # now set the resolution explicitly. If you do not set it, the camera will fail after first photo is taken
        self.resolution = (4056, 3040)

    def init(self):
        try:
            if not(self.debug):
                self.start_preview()
                # camera may need time to warm up
                time.sleep(2)
            msg = 'Raspi camera initialized'
            self.logger.info(msg)
            self.state = 'ready'
        except:
            msg = 'Raspi camera could not be initialized'
            self.state = 'broken'
            self.logger.error(msg)
        return {'msg': msg,
                'level': 'info'
                }

    def wait(self):
        """
        Basically do not do anything, just let the server know you understood the msg
        """
        msg = 'Raspi camera will wait for further instructions'
        self.logger.debug(msg)  # better only show this in debug mode
        return {'msg': msg,
                'level': 'debug'
                }

    def exit(self):
        self.stop_preview()
        self.state = 'idle'
        msg = 'Raspi camera shutdown'
        self.logger.info(msg)
        return {'msg': msg,
                'level': 'info'
                }

    def stop(self):
        # TODO: debug stop capture daemon
        if self.timer is not None:
            try:
                self.timer.stop()
            except:
                pass
            self.state = 'ready'
            msg = 'Camera capture stopped'
        else:
            msg = 'No capturing taking place, do nothing'
        self.logger.info(msg)
        return {'msg': msg,
                'level': 'info'
                }

    def capture(self, timeout=1.):
        fn = f'photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        self.dst_fn = os.path.join(self._root, fn)
        self.logger.info(f'Writing to {self.dst_fn}')
        tic = time.time()
        if not(self.debug):
            super().capture(self.dst_fn)
        toc = time.time()
        self.logger.debug(f'Photo took {toc-tic} seconds to take')
        post_capture = {'kwargs': {'msg': f'Taken photo {self.dst_fn}', 'level': 'info'},
                        'req': 'LOG',
                        'state': self.state
                        }
        self.post(post_capture)

    def capture_until(self, timeout=1.):
        """
        Tries to capture an image until successful
        :param timeout: float - amount of time capturing is tried
        """
        # update project status
        # TODO: make sure the parent required project is stored
        camera = PiCamera()

        _take = True
        n = 1
        start_time = time.time()
        while (_take) and (time.time()-start_time < timeout):
            try:
                self.logger.debug(f'Trial {n}')
                # Temporary image location until set_dst_fn is defined
                self.src_photo_fn = self.capture()  # '/home/pi/Desktop/image.jpg'
                dt = time.time()-start_time
                _take = False
                self.logger.info(f'Picture taken in {str(self.src_photo_fn)} within {dt*1000} ms')
            except:
                n += 1
        if _take:
            # apparently the picture was not taken
            raise IOError('Timeout reached')

    def capture_continuous(self, start_time=None, project=None):
        self._project_id = int(project['project_id'])
        self._project_name = project['project_name']
        self._dt = int(project['dt'])
        self._n_cams = int(project['n_cams'])
        # import pdb;pdb.set_trace()
        self.logger.info(f'Starting capture for project - id: {self._project_id} name: {self._project_name} interval: {self._dt} secs.')
        try:
            self.timer = RepeatedTimer(int(project['dt']), self.capture, start_time=start_time)
            self.state = 'capture'
        except:
            msg = 'Camera not responding or disconnected'
            logger.error(msg)
        msg = f'Camera is now capturing every {self._dt} seconds'
        logger.info(msg)
        return {'msg': msg,
                'level': 'info'
                }

    def post(self, msg):
        """

        :param msg: dict
        :return:
        """
        headers = {'Content-type': 'application/json'}
        r = requests.post(f'http://{self.host}:{self.port}/picam', data=json.dumps(msg), headers=headers)

    def set_dst_fn(self):
        raise NotImplementedError('Setting destination path is not implemented yet')
        # FIXME
