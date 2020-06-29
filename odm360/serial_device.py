import serial
import serial.tools.list_ports
import logging
import pickle

logger = logging.getLogger(__name__)

class SerialDevice():
    """
    Class for generic functionalities for any serial device. Can be inherited for specific serial devices.
    """
    def __init__(self, port, baud_rate=9600, timeout=5, parent=None, wildcard='dummy', logger=logger):
        """
        Initiate object with defaults

        :param baud_rate: int - baud rate for reading (default: 9600)
        :param timeout: int - timeout in ms before serial port is ignored (default: 6)
        :
        """
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.port = port
        self.serial = None
        self.data = None
        self.text = None
        self.logger = logger

    def open_serial(self):
        """
        Open the serial device on self.port (return IOError if not found)
        """
        if self.port is not None:
            try:
                self.serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
                self.logger.info(f'Serial port on {self.port} opened with baud rate {self.baud_rate}')
            except:
                raise IOError('Cannot open serial device, check permissions')
        else:
            raise IOError('No port specified, please connect a device.')

    def close_serial_device(self):
        """
        Close the serial device on self.port (return IOError if no open device is found)
        """
        if self.serial is not None:
            self.serial.close()
            logger.warning(f'Serial connection to {self.port} is closed.')
        else:
            raise IOError('No serial connection is open.')

    def _send_method(self, name, **kwargs):
        """
        serializes a function name and its arguments (provided as kwargs) in pickle, and send to device
        """
        msg = {'name': name,
               'kwargs': kwargs
               }
        p = pickle.dumps(msg)  # serialize msg
        self.serial.write(p)
        # self.serial.write(str.encode(txt))

    # def _recv_method(self):
    #     """
    #     unserializes a function name and its arguments (provided as kwargs) from pickle
    #     """
    #
    #     msg = {'name': name,
    #            'kwargs': kwargs
    #            }
    #     try:
    #         self._to_serial(msg)
    #     except:
    #

    def _to_serial(self, data):
        """
        reads a raw msg from serial connection
        :return:

        """
        if self.serial is not None:
            p = pickle.dumps(data)  # serialize msg
            self.serial.write(p)
        else:
            raise IOError('No serial connection is open.')

    def _from_serial(self):
        """
        reads a raw msg from serial connection
        :return:

        """
        if self.serial is not None:
            data = self.serial.readline()
            if len(data) == 0:
                raise IOError('Empty line received')
            return pickle.loads(data) # return loaded data
        else:
            raise IOError('No serial connection is open.')

    def _from_serial_until(self, timeout=1):
        # TODO: implement a timeout in case no suitable data is found within timeout period
        _read = True
        while _read:
            try:
                data = self._from_serial()
                _read = False
                self.logger.info(f'Data received from {self.description} on port {self.port}')
            except:
                pass
        return data

    # def _from_serial_txt(self):
    #     """
    #     Read and tries to decode lines from serial device on self.serial, until decoded text is found
    #     """
    #     _read = True
    #     while _read:
    #         data = self._from_serial()
    #         try:
    #             txt = data.decode('utf-8')
    #             _read = False
    #         except:
    #             # binary data found, so read until
    #             pass
    #     return txt

