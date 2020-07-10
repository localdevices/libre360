#!/bin/bash

echo updating
sudo apt update && sudo apt upgrade -y

echo Installing infrastructure
sudo apt install -y git python3-pip libgphoto2-dev libatlas-base-dev gfortran emacs-nox

echo Disabling IPv6
sudo sed -i '$s/$/ ipv6.disable=1/' /boot/cmdline.txt

echo Disabling serial console to free up UART serial line
sudo sed -i 's/console=serial0,115200 //g' /boot/cmdline.txt

echo enabling UART
echo $'\n# Enable UART\nenable_uart=1' | sudo tee -a /boot/config.txt

echo fetching and installing the ODM360 code
git clone https://github.com/OpenDroneMap/odm360
cd odm360
pip3 install -e

echo Now you should have a Raspberry Pi set up with the basic infrastructure common to all devices in the kit. The next steps depend whether this device is intended to be a Parent, Child, or TimeServer.
