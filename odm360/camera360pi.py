import os
from picamera import PiCamera
import time
import logging

logger = logging.getLogger(__name__)
from datetime import datetime
from odm360.timer import RepeatedTimer

class Camera360Pi(PiCamera):
    """
    This class is for increasing the functionalities of the Camera class of gphoto2 specifically for
    the 360 camera use case. Additional functionalities are:
    - enable selecting a camera on a specific address (so that use of multiple cameras is warranted)
    - enable transfer data to a root folder
    - enable modification of exif tags of photos
    """
    def __init__(self, root=None, logger=logger, debug=False):
        self.debug = debug
        self.state = 'idle'
        self.timer = None
        if not(self.debug):
            super().__init__()
        self._root = root  # root folder where to store photos from this specific camera instance
        self.src_fn = None  # path to currently made photo (source) inside the camera
        self.dst_fn = 'dummy.jpg'  # path to photo (destination) on drive
        self.logger = logger
        self.id = None  # TODO: give a uniue ID to each camera (once CameraRig is defined, complete)
        self.name = None  # TODO: give a name to each camera (once CameraRig is defined, complete)
        if not(os.path.isdir(self._root)):
            os.makedirs(self._root)

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
            self.timer.stop()
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
        self.logger.info(f'Photo took {toc-tic} seconds to take')

    def capture_until(self, timeout=1.):
        """
        Tries to capture an image until successful
        :param timeout: float - amount of time capturing is tried
        """

        camera = PiCamera()

        _take = True
        n = 1
        start_time = time.time()
        while (_take) and (time.time()-start_time < timeout):
            try:
                self.logger.debug(f'Trial {n}')
                # Temporary image location until set_dst_fn is defined
                self.src_photo_fn = camera.capture('/home/pi/Desktop/image.jpg')
                dt = time.time()-start_time
                _take = False
                self.logger.info(f'Picture taken in {str(self.src_photo_fn)} within {dt*1000} ms')
            except:
                n += 1
        if _take:
            # apparently the picture was not taken
            raise IOError('Timeout reached')

    def capture_continuous(self, start_time=None, interval=5):
        # FIXME: refactor RepeatedTimer so that a start_time can be passed
        try:
            self.timer = RepeatedTimer(interval, self.capture, start_time=start_time)
            self.state = 'capture'
        except:
            msg = 'Camera not responding or disconnected'
            logger.error(msg)
        msg = f'Camera is now capturing avery {interval} seconds'
        logger.info(msg)
        return {'msg': msg,
                'level': 'info'
                }


    def set_dst_fn(self):
        raise NotImplementedError('Setting destination path is not implemented yet')
        # FIXME

