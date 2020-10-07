import logging
from odm360.serial_device import SerialDevice

logger = logging.getLogger(__name__)


class Ublox(SerialDevice):
    # def find_serial_device(self, wildcard='u-blox'):
    #     """
    #     Looks for a u-blox device in all active serial ports
    #     :param wildcard: str - wildcard used to look for serial device (default: u-blox)
    #     """
    #     super().find_serial_device(wildcard=wildcard)

    def parse_nmea(self):
        """
        Parse text in self.text to NMEA message if valid NMEA string is found
        """
        if self.text is not None:
            pass
            # FIXME: implement parsing of NMEA from text to self.nmea
        else:
            raise ValueError("No text found.")

    def log_rinex(self):
        """
        Logs raw rinex data from serial connection

        :return:
        """
        raise NotImplementedError("Not implemented yet.")
