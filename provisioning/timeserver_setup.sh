#!/bin/bash

# TODO test hostname changes in script; may work in console
# but not in script. 
echo setting hostname to timeserver
echo timeserver | sudo tee /etc/hostname # overwrites
sudo sed -i "s/127.0.0.1\tlocalhost/127.0.0.1\tlocalhost timeserver/g" /etc/hosts

echo Enabling a GPIO pin to receive the PPS signal
echo $'\n# Enable GPIO for PPS signal\ndtoverlay=pps-gpio,gpiopin=4' | sudo tee -a /boot/config.txt

echo Installing GPSD, NTP, and related infrastructure
sudo apt install -y gpsd gpsd-clients python-gps pps-tools

echo Disabling IPv6
sudo sed -i '$s/$/ ipv6.disable=1/' /boot/cmdline.txt

echo Setting GPSD to listen to the GNSS on the serial port instead of USB
sudo sed -i 's/USBAUTO="true"/USBAUTO="false"/g' /etc/default/gpsd
sudo sed -i 's:DEVICES="":DEVICES="/dev/ttyS0 /dev/pps0":g' /etc/default/gpsd
sudo sed -i 's:GPSD_OPTIONS="":GPSD_OPTIONS="-n":g' /etc/default/gpsd

echo Creating symlinks for GPSD to hook to the device
echo KERNEL==\"ttyS0\", SUBSYSTEM==\"tty\", DRIVER==\"\", OWNER==\"root\", GROUP==\"tty\", MODE==\"0777\", SYMLINK+=\"gps0\" | sudo tee -a /etc/udev/rules.d/09-pps.rules

echo Setting up pps-gpio module
echo pps-gpio | sudo tee -a /etc/modules

echo Enabling the GPSD service
sudo systemctl enable gpsd

echo installing NTP (temporarily... go figure)
sudo apt install ntp -y
# TODO configure NTP
sudo apt remove ntp -y

echo Downloading and latest NTP from source
echo This will take almost an hour.
# TODO make this always grab the latest version
wget http://www.eecis.udel.edu/~ntp/ntp_spool/ntp4/ntp-4.2/ntp-4.2.8p15.tar.gz

tar -xvf ntp-4.2.8p15.tar.gz

cd ntp-4.2.8p15

./configure --prefix=/usr --enable-all-clocks --enable-parse-clocks --enable-SHM --enable-debugging --sysconfdir=/var/lib/ntp --with-sntp=no --with-lineeditlibs=edit --without-ntpsnmpd --disable-local-libopts --disable-dependency-tracking --enable-linuxcaps --enable-pps --enable-ATOM

make

sudo make install

echo now this Raspberry Pi should be configured as a TimeServer. Please ensure that it is wired to an ArduSimple u-Blox ZED-F9P GNSS receiver with the appropriate connections.


