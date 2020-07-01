import time
import logging
from odm360.serial_device import SerialDevice

logger = logging.getLogger(__name__)

class Camera360Serial(SerialDevice):
    """
    Class creates a serial connection to a raspi with a raspi camera. Functionalities act similar to gphoto2
    functionalities so that an end user has the feeling cameras are local and the same as a normal photo camera.
    """
    def __init__(self, port, logger=logger, **kwargs):
        super().__init__(port, logger=logger, **kwargs)   # baud_rate=baud_rate, timeout=timeout, parent=parent, wildcard=wildcard,
        self.logger.info('Serial camera initialized')
        self.photo = None  # here, information about the latest photo is stored.

    def init(self, timeout=1.):
        """
        Send "init" to raspberry pi
        On raspberry pi side, the pi camera will be initialized

        :return:
        """
        self._send_method("init")
        # ask for success or no success
        return self.success('Physical camera initialized', 'Physical camera initialize failed')

    def capture(self):
        """
        Capture an image
        :param
        """
        self._send_method(f"capture")
        # ask for success or no success
        self.photo = self.success('Image captured', 'Image capture failed')
        logger.info(f'Photo stored on {self.port} on {self.photo}')

    def exit(self):
        self._send_method(f"exit")
        # ask for success or no success
        return self.success('Serial camera closed', 'Serial camera could not be closed')

    def set_dst_fn(self):
        raise NotImplementedError('Setting destination path is not implemented yet')
        # FIXME

    def success(self, msg_true, msg_false):
        success = self._from_serial_until()
        if success is not None:
            self.logger.debug(msg_true)
        else:
            self.logger.debug(msg_false)
        return success

    # TODO: check if a file transfer method already exists
    # TODO: check if exif tag functionalities exist