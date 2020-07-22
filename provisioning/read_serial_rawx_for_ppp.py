#!/usr/bin/python3
"""
Read serial raw GNSS data from a device to a file.
One positional argument: output file to write.
Two flag arguments:
-br or --baud_rate: the expected baud rate of the device. Default 38400.
-to or --timeout: the time in seconds to wait before giving up on a port
-p or --port: the specific name of the port the device is on (don't search)
Checks for serial ports, iterates through them and grabs the first one that
provides a valid NMEA sentence. Then writes all following NMEA sentences
to the specified output file.
"""
import sys, os
import argparse

import serial
import serial.tools.list_ports

def make_serial_reader(baud_rate, timeout, port = None):
    """Create a serial reader for a GNSS receiver."""
    if port:
        serial_reader = serial.Serial(port, baud_rate, timeout)
        for i in range(10):
            if(validate_NMEA_sentence(serial_reader.readline())):
                return serial_reader
        return None
    ports = serial.tools.list_ports.comports()
    for port in ports:
        serial_reader = serial.Serial(port[0], baud_rate, timeout)
        for i in range(10):
            if(validate_NMEA_sentence(serial_reader.readline())):
                return serial_reader
        return None

def log_raw_GNSS(serial_reader, outfile):
    ```Write binary data from a serial port to a file```
    with open(outfile, 'wb') as of:
        while True:
            # Using a KiB as a default size; unoptimized 
            block = serial_reader.read(1024)
            of.write(block)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('outfile', help = "Text file to write GNSS data to")
    p.add_argument('-br', '--baud_rate', default = 460800,
                   help = 'expected baud rate of the device')
    p.add_argument('-to', '--timeout', default = 5,
                   help = 'Time in seconds to wait before giving up on a port')
    p.add_argument('-p', '--port', default = None,
                   help = 'Known serial port of device. Searches if omitted.')

    opts = vars(p.parse_args())

    br = int(opts['baud_rate'])
    to = int(opts['timeout'])
    pt = opts['port']
    of = opts['outfile']
    print(f'\nAttempting to create serial reader with: \nbaud rate: {br}'
          f'\non port {pt}')
    reader = make_serial_reader(br,to, pt)
    print(f'Writing output to {of}')
    log_raw_GNSS(reader, of)
