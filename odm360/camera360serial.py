import logging
from odm360.serial_device import SerialDevice
logger = logging.getLogger(__name__)

class Camera360Serial(SerialDevice):
    """
    This class is for increasing the functionalities of the Camera class of gphoto2 specifically for
    the 360 camera use case. Additional functionalities are:
    - enable selecting a camera on a specific address (so that use of multiple cameras is warranted)
    - enable transfer data to a root folder
    - enable modification of exif tags of photos
    """
    # def __init__(self, baud_rate=9600, timeout=1, parent=None, wildcard='UART', logger=logger):
    def __init__(self, port, logger=logger, **kwargs):
            super().__init__(port, logger=logger, wildcard='UART', **kwargs)   # baud_rate=baud_rate, timeout=timeout, parent=parent, wildcard=wildcard,

    def init(self, timeout=1.):
        """
        Send "init" to raspberry pi
        On raspberry pi side, the pi camera will be initialized

        :return:
        """
        self._to_serial("init")
        # ask for success or no success
        if self._from_serial_txt() != "0":
            msg = 'Initialization of camera was unsuccessful'
            self.logger.error(msg)
            raise IOError(msg)
        self.logger('Camera initialized')

    def capture_until(self, timeout=1.):
        """
        Tries to capture an image until successful
        :param timeout: float - amount of time capturing is tried
        """
        self._to_serial(f"capture_until(timeout={timeout}")
        # ask for success or no success
        if self._from_serial_txt() != "0":
            msg = 'Image capture was unsuccessful'
            self.logger.error(msg)
            raise IOError(msg)
        else:
            self.logger('Image captured')

    def set_dst_fn(self):
        raise NotImplementedError('Setting destination path is not implemented yet')
        # FIXME

    # TODO: check if a file transfer method already exists
    # TODO: check if exif tag functionalities exist