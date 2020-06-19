#!/usr/bin/python3
"""
Read serial NMEA data from a device to a file.

One positional argument: output file to write.

Two flag arguments:
-br or --baud_rate: the expected baud rate of the device
-to or --timeout: the time in seconds to wait before giving up on a port

Checks for serial ports, iterates through them and grabs the first one that
provides a valid NMEA sentence. Then writes all following NMEA sentences
to the specified output file.
"""
import sys, os
import argparse

import serial
import serial.tools.list_ports

def make_serial_reader(baud_rate, timeout):
    """Create a serial reader for a GNSS receiver."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        serial_reader = serial.Serial(port[0], baud_rate, timeout)
        for i in range(10):
            if(validate_NMEA_sentence(serial_reader.readline())):
                return serial_reader

def log_NMEA(serial_reader, outfile):
    with open(outfile, 'wb') as of:
        while True:
            sentence = serial_reader.readline()
            if(validate_NMEA_sentence(sentence)):
               of.write(serial_reader.readline())   

def validate_NMEA_sentence(sentence):
    """Check for a valid NMEA sentence."""
    # TODO: Check for valid NMEA sentence structure, calculate checksums
    # At the moment this only checks for a leading '$' char (ASCII 36)
    if(sentence.strip()[0] == 36):
       return True

def validate_rinex_sentence(sentence):
    """Check for a valid Rinex sentence (for now in .ubx format)"""
    # TODO: actually validate something
    return True # just assume it's ok so anything not NMEA gets passed for now

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('outfile', help = "Text file to write NMEA data to")
    p.add_argument('-br', '--baud_rate', default = 9600,
                   help = 'expected baud rate of the device')
    p.add_argument('-to', '--timeout', default = 5,
                   help = 'Time in seconds to wait before giving up on a port')

    opts = vars(p.parse_args())
    reader = make_serial_reader(int(opts['baud_rate']), int(opts['timeout']))
    log_NMEA(reader, opts['outfile'])
    
    
    
    
