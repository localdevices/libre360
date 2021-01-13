#!/bin/bash

echo Installing GPSD
echo Adding repository to sources.list with latest version of gpsd
echo $'\n# buster backports\ndeb http://deb.debian.org/debian buster-backports main' | sudo tee -a /etc/apt/sources.list

# get the required repository keys
sudo wget -qO - 'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x04EE7237B7D453EC' | sudo apt-key add -
sudo wget -qO - 'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x648ACFD622F3D138' | sudo apt-key add -
sudo apt update

echo $'\n# Enable UART\nenable_uart=1' | sudo tee -a /boot/config.txt
sudo apt install -y -t buster-backports gpsd gpsd-clients pps-tools

# echo Setting GPSD to listen to the GNSS on the serial port instead of USB
# sudo sed -i 's/USBAUTO="true"/USBAUTO="false"/g' /etc/default/gpsd
sudo sed -i 's:DEVICES="":DEVICES="/dev/ttyACM0 /dev/pps0":g' /etc/default/gpsd
# sudo sed -i 's:GPSD_OPTIONS="":GPSD_OPTIONS="-n":g' /etc/default/gpsd

echo Enabling a GPIO pin to receive the PPS signal
echo $'\n# Enable GPIO for PPS signal\ndtoverlay=pps-gpio,gpiopin=4' | sudo tee -a /boot/config.txt

echo Setting up pps-gpio module
echo pps-gpio | sudo tee -a /etc/modules

echo Enabling the GPSD service
sudo systemctl enable gpsd

