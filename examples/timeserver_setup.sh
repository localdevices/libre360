#!/bin/bash

echo Installing infrastructure
sudo apt install -y gpsd gpsd-clients python-gps pps-tools

echo Disabling IPv6
sudo sed -i '$s/$/ ipv6.disable=1/' /boot/cmdline.txt

echo Disabling serial console to free up UART serial line
sudo sed -i 's/console=serial0,115200 //g' /boot/cmdline.txt

echo enabling UART
echo $'\n# Enable UART\nenable_uart=1' | sudo tee -a /boot/config.txt

echo Enabling a GPIO pin to receive the PPS signal
echo $'\n# Enable GPIO for PPS signal\ndtoverlay=pps-gpio,gpiopin=4' | sudo tee -a /boot/config.txt

echo setting hostname to timeserver
sudo hostnamectl set-hostname timeserver
sudo sed -i 's/127.0.0.1\tlocalhost/127.0.0.1\tlocalhost timeserver/g' /etc/hosts

echo Setting GPSD to listen to the GNSS on the serial port instead of USB
sudo sed -i 's/USBAUTO="true"/USBAUTO="false"/g' /etc/default/gpsd
sudo sed -i 's:DEVICES="":DEVICES="/dev/ttyS0 /dev/pps0":g' /etc/default/gpsd
sudo sed -i 's:GPSD_OPTIONS="":GPSD_OPTIONS="-n":g' /etc/default/gpsd

echo Enabling the GPSD service
sudo systemctl enable gpsd

echo Creating symlinks for GPSD to hook to the device
echo KERNEL==\"ttyS0\", SUBSYSTEM==\"tty\", DRIVER==\"\", OWNER==\"root\", GROUP==\"tty\", MODE==\"0777\", SYMLINK+=\"gps0\" | sudo tee -a /etc/udev/rules.d/09-pps.rules

echo Setting up pps-gpio module
echo pps-gpio | sudo tee -a /etc/modules

