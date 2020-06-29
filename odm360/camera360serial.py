import time
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
        self._send_method("init")
        # ask for success or no success
        return self.success('Camera initialized', 'Camera initialize failed')

    def capture(self):
        """
        Capture an image
        :param
        """
        self._send_method(f"capture")
        # ask for success or no success
        return self.success('Image captured', 'Image capture failed')

    def set_dst_fn(self):
        raise NotImplementedError('Setting destination path is not implemented yet')
        # FIXME

    def success(self, msg_true, msg_false):
        success = bool(self._from_serial_until().decode('utf-8'))
        if success:
            self.logger.info(msg_true)
        else:
            self.logger.error(msg_false)
        return success

    # TODO: check if a file transfer method already exists
    # TODO: check if exif tag functionalities exist