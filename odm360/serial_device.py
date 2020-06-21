import serial
import serial.tools.list_ports
import datetime
import numpy as np
import time

import logging

logger = logging.getLogger(__name__)

class SerialDevice():
    """
    Class for generic functionalities for any serial device. Can be inherited for specific serial devices.
    """
    def __init__(self, baud_rate=9600, timeout=5, parent=None, logger=logger):
        """
        Initiate object with defaults

        :param baud_rate: int - baud rate for reading (default: 9600)
        :param timeout: int - timeout in ms before serial port is ignored (default: 6)
        :
        """
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.port = None
        self.serial = None
        self.data = None
        self.text = None
        self.logger = logger
        self.find_serial_device()

    def find_serial_device(self, wildcard='dummy'):
        """
        Looks for an Arduino in all active serial ports

        :param wildcard: str - wildcard used to look for serial device (default: u-blox)
        """
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            port = p[0]
            description = p[1]
            if wildcard in description:
                self.logger.info(f'Found {description} on port {port}')
                self.port = port
                self.description = description
                return
        # if the end of function is reached, apparently, no suitable port was found
        raise IOError(f'No device with wildcard {wildcard} found on COM ports')

    def open_serial_device(self):
        """
        Open the serial device on self.port (return IOError if not found)
        """
        if self.port is not None:
            try:
                self.serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
                logger.info(f'Serial port on {self.port} with name {self.description} opened with baud rate {self.baud_rate}')
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

    def read_serial_device(self):
        """
        Read one line (non-decoded) from serial device self.serial
        """
        if self.serial is not None:
            self.data = self.serial.readline()
            self.logger.info(f'Line read from {self.description} on port {self.port} with baud rate {self.baud_rate}')
        else:
            raise IOError('No serial connection is open.')

    def read_serial_text(self):
        """
        Read and tries to decode lines from serial device on self.serial, until decoded text is found
        """
        if self.serial is not None:
            self.text = None  # reinitiate text
            _read = True
            # TODO: implement a timeout in case no suitable data is found within timeout period
            while _read:
                self.read_serial_device()
                try:
                    self.text = self.data.decode('utf-8')
                    _read = False
                    self.logger.info(f'Text read from {self.description} on port {self.port} with baud rate {self.baud_rate}')
                except:
                    # binary data found, so read until
                    pass
        else:
            raise IOError('No serial connection is open.')

