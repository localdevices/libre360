from odm360 import ublox

# initiate a ublox object
gps = ublox.Ublox()
# open the ublox connection and see if we get a serial object back
gps.open_serial_device()
print(gps.serial)

# try to read a line and print it
gps.read_serial_text()
print(gps.text)

# gracefully close the object
gps.close_serial_device()

