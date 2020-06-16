import serial
import serial.tools.list_ports
import datetime
import numpy as np
import time

class Ublox():

    def __init__(self, baud_rate=9600, timeout=5, parent=None):
        """
        Initiate object with defaults

        :param baud_rate:
        :param timeout:
        """
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.port = None
        self.serial = None
        self.data = None
        self.text = None
        self.find_serial_device()

        pass

    def find_serial_device(self, wildcard='u-blox'):
        """
        Looks for an Arduino in all active serial ports
        TODO: check if this function works appropriately on a linux box.
        :return: str - name of COM port (e.g. 'COM1')
        """
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            port = p[0]
            description = p[1]
            if wildcard in description:
                print('Found {:s} on port {:s}'.format(description, port))
                self.port = port
                return
        # if the end of function is reached, apparently, no suitable port was found
        print('No device with wildcard {:s} found on COM ports'.format(wildcard))

    def open_serial_device(self):
        if self.port is not None:
            try:
                self.serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            except:
                raise IOError('Cannot open serial device, check permissions')
        else:
            raise IOError('No port specified, please connect a device.')

    def close_serial_device(self):
        if self.serial is not None:
            self.serial.close()
            print('Serial connection to {:s} is closed.'.format(self.port))
        else:
            raise IOError('No serial connection is open.')

    def read_serial_device(self):
        if self.serial is not None:
            self.data = self.serial.readline()
        else:
            raise IOError('No serial connection is open.')

    def read_serial_text(self):
        if self.serial is not None:
            self.text = None  # reinitiate text
            _read = True
            while _read:
                self.read_serial_device()
                try:
                    self.text = self.data.decode('utf-8')
                    _read = False
                except:
                    # binary data found, so read until
                    pass
        else:
            raise IOError('No serial connection is open.')

    def parse_nmea(self):
        if self.text is not None:
            pass
            # FIXME: implement parsing of NMEA from text
        else:
            raise ValueError('No text found.')


