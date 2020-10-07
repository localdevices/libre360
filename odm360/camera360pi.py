import os
import io
import time
import logging
import json
import requests
import psycopg2
logger = logging.getLogger(__name__)
from datetime import datetime

# import odm360 methods and functions
from odm360.timer import RepeatedTimer
from odm360 import dbase

# connect to child database
db = 'dbname=odm360 user=odm360 host=localhost password=zanzibar'
conn = psycopg2.connect(db)
cur = conn.cursor()

# get the uuid of the device
try:
    cur.execute("SELECT * FROM device")
    device_uuid, device_name = cur.fetchone()[0]
except:
    import uuid
    device_uuid, device_name = str(uuid.uuid4()), 'dummy'
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
    def __init__(self, state, logger=logger, debug=False, host=None, port=None, project_id=None, project_name=None, n_cams=None, dt=None):
        self.debug = debug
        self.state = state
        self.timer = None
        self._device_uuid = device_uuid
        self._device_name = device_name
        self._root = 'photos'
        self._project_id = project_id  # project_id for the entire project from parent
        self._project_name = project_name  # human-readable name
        self._n_cams = n_cams  # total amount of cameras related to this project
        self._dt = dt  # time intervals requested by parent
        self.src_fn = None  # path to currently made photo (source) inside the camera
        self.dst_fn = ''  # path to photo (destination) on drive
        self.logger = logger
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
            self.state['status'] = 'ready'
        except:
            msg = 'Raspi camera could not be initialized'
            self.state['status'] = 'broken'
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
        self.state['status'] = 'idle'
        msg = 'Raspi camera shutdown'
        self.logger.info(msg)
        return {'msg': msg,
                'level': 'info'
                }

    def stop(self):
        if self.timer is not None:
            try:
                self.timer.stop()
            except:
                pass
            self.state['status'] = 'ready'
            msg = 'Camera capture stopped'
        else:
            msg = 'No capturing taking place, do nothing'
        self.logger.info(msg)
        return {'msg': msg,
                'level': 'info'
                }

    def capture(self, timeout=1., cur=cur):
        fn = f'photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        # capture to local file
        self.dst_fn = os.path.join(self._root, fn)
        self.logger.info(f'Writing to {self.dst_fn}')
        target = self.dst_fn
        # prepare kwargs for database insertion
        kwargs = {
            'project_id': self._project_id,
            'survey_run': self._survey_run,
            'device_uuid': self._device_uuid,
            'device_name': self._device_name,
            'fn': fn,
        }
        tic = time.time()
        if not(self.debug):
            super().capture(target, 'jpeg')
        toc = time.time()
        # store details about photo in database
        dbase.insert_photo(cur, **kwargs)
        dbase.insert_photo(cur, **kwargs)
        # retrieve uuid of inserted photo

        self.logger.debug(f'Photo took {toc-tic} seconds to take')
        post_capture = {'kwargs': {'msg': f'Taken photo {fn}', 'level': 'info'},
                        'req': 'LOG',
                        'state': self.state
                        }
        self.post(post_capture)  # this just logs on parent side what happened on child side
        # TODO, once we are sure that parent inherits photos through a combined VIEW, remove commented lines below
        # # now add a photo on the parent side's database as well, making sure the uuid is fixed!
        # kwargs['photo_uuid'] = dbase.query_photo(cur, fn)['photo_uuid']
        # store_capture = {'kwargs': kwargs,
        #                 'req': 'STORE',
        #                 'state': self.state
        #                 }
        #
        # self.post(store_capture)  # store info on photo on parent side


    def capture_continuous(self, start_time=None, survey_run=None, project=None):
        self._project_id = int(project['project_id'])
        self._project_name = project['project_name']
        self._dt = int(project['dt'])
        self._n_cams = int(project['n_cams'])
        self._survey_run = survey_run
        # import pdb;pdb.set_trace()
        self.logger.info(f'Starting capture for project - id: {self._project_id} name: {self._project_name} interval: {self._dt} secs survey run {self._survey_run}.')
        try:
            self.timer = RepeatedTimer(int(project['dt']), self.capture, start_time=start_time)
            self.state['status'] = 'capture'
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

