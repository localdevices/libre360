from picamera import PiCamera
import time
import logging

logger = logging.getLogger(__name__)

class Camera360pi(PiCamera):
    """
    This class is for increasing the functionalities of the Camera class of gphoto2 specifically for
    the 360 camera use case. Additional functionalities are:
    - enable selecting a camera on a specific address (so that use of multiple cameras is warranted)
    - enable transfer data to a root folder
    - enable modification of exif tags of photos
    """
    def __init__(self, root=None, addr=None, logger=logger):
        super().__init__()
        self._root = root  # root folder where to store photos from this specific camera instance
        self.src_fn = None  # path to currently made photo (source) inside the camera
        self.dst_fn = None  # path to photo (destination) on drive
        self.logger = logger
        self.id = None  # TODO: give a uniue ID to each camera (once CameraRig is defined, complete)
        self.name = None  # TODO: give a name to each camera (once CameraRig is defined, complete)
        if addr is not None:
            # access a specific camera if the address details are provided
            # get all accessible ports
            ports = gp.PortInfoList()
            ports.load()
            # find the port that's commensurate with the address of the camera
            idx = ports.lookup_path(addr)
            self.set_port_info(ports[idx])


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
                camera.capture('/home/pi/Desktop/image.jpg') # Temporary image location until set_dst_fn is defined
                dt = time.time()-start_time
                _take = False
                self.logger.info(f'Picture taken in {str(self.src_photo_fn)} within {dt*1000} ms')
            except:
                n += 1
        if _take:
            # apparently the picture was not taken
            raise IOError('Timeout reached')

    def set_dst_fn(self):
        raise NotImplementedError('Setting destination path is not implemented yet')
        # FIXME

    # TODO: check if a file transfer method already exists
    # TODO: check if exif tag functionalities exist
