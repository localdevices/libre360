#!/bin/bash

echo Installing NTP
sudo apt install -y ntp

echo Stopping the default timesync daemon
sudo systemctl stop systemd-timesyncd
sudo systemctl disable systemd-timesyncd

echo Starting the full NTP server
sudo /etc/init.d/ntp stop
sudo /etc/init.d/ntp start

echo at this point the setup depends whether this device is the parent (which will be the NTP server) or a child (which will be an NTP client)

echo test this using ntpq -pn
