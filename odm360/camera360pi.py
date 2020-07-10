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
        #self.start_preview()
        # camera may need time to warm up
        time.sleep(2)
        self.logger.info('Raspi camera initialized')

    def exit(self):
        self.stop_preview()
        self.logger.info('Raspi camera stopped')

    def capture(self, timeout=1.):
        fn = f'photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        self.dst_fn = os.path.join(self._root, fn)
        self.logger.info(f'Writing to {self.dst_fn}')
        tic = time.time()
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

    def dummy_capture(self):
        fn = f'photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        self.dst_fn = os.path.join(self._root, fn)
        self.logger.info(f'Writing to {self.dst_fn}')
        tic = time.time()
        # super().capture(self.dst_fn)
        toc = time.time()
        self.logger.info(f'Photo took {toc-tic} seconds to take')

    def capture_continuous(self, start_time=None, interval=5):
        # FIXME: refactor RepeatedTimer so that a start_time can be passed
        try:
            timer = RepeatedTimer(interval, self.dummy_capture, start_time=start_time)
        except:
            logger.error('Camera not responding or disconnected')



    def set_dst_fn(self):
        raise NotImplementedError('Setting destination path is not implemented yet')
        # FIXME

