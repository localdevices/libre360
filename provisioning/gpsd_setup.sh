#!/bin/bash

echo Installing GPSD
sudo apt install -y gpsd gpsd-clients python-gpsd pps-tools

# echo Setting GPSD to listen to the GNSS on the serial port instead of USB
# sudo sed -i 's/USBAUTO="true"/USBAUTO="false"/g' /etc/default/gpsd
# sudo sed -i 's:DEVICES="":DEVICES="/dev/ttyS0 /dev/pps0":g' /etc/default/gpsd
# sudo sed -i 's:GPSD_OPTIONS="":GPSD_OPTIONS="-n":g' /etc/default/gpsd

echo Enabling a GPIO pin to receive the PPS signal
echo $'\n# Enable GPIO for PPS signal\ndtoverlay=pps-gpio,gpiopin=4' | sudo tee -a /boot/config.txt

echo Setting up pps-gpio module
echo pps-gpio | sudo tee -a /etc/modules

echo Enabling the GPSD service
sudo systemctl enable gpsd

