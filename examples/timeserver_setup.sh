#!/bin/bash

echo Installing infrastructure
sudo apt install -y gpsd gpsd-clients python-gps pps-tools

echo Disabling IPv6
sudo sed -i '$s/$/ ipv6.disable=1/' /boot/cmdline.txt

echo Disabling serial console to free up UART serial line
sudo sed -i 's/console=serial0,115200 //g' /boot/cmdline.txt

echo enabling UART
echo $'\n# Enable UART\nenable_uart=1' | sudo tee -a /boot/config.txt
