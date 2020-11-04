#!/bin/bash

# Set up a Raspberry Pi as an ODM360 Parent.

model="$( cat /proc/device-tree/model )"
onpi="no"
if [[ "$model" == *"Raspberry Pi"* ]]; then
    echo "This is actually a Raspberry Pi!"
    onpi="yes"
fi

# If nothing in /proc/device-tree/model:
if [[ "$model" == "" ]]; then
    echo "I have no idea what this machine is!"
    model="computer of some sort"
fi

# Install dnsmasq and hostapd only if on a raspi
if [[ $onpi == "yes" ]]; then
  provisioning/wifi_setup.sh
fi

echo Running base pi setup
provisioning/base_pi_setup.sh

echo Running database setup script
provisioning/database_setup.sh

echo Running NTP setup script
provisioning/ntp_setup.sh

echo Setting NTP to server
cat <<EOF >> /etc/ntp.conf
restrict 192.168.1.0 mask 255.255.255.0

broadcast 192.168.1.255
broadcast 224.0.1.1
EOF

echo installing nginx and configuring it to use uwsgi
sudo apt install -y nginx

sudo rm /etc/nginx/sites-enabled/default
echo adding the odm360dashboard site config file to nginx
sudo cp provisioning/odm360dashboard /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/odm360dashboard /etc/nginx/sites-enabled/

sudo cp provisioning/systemd_services/odm360dashboard.service /etc/systemd/system/
echo starting and enabling the odm360dashboard service with Systemd
sudo systemctl start odm360dashboard.service
sudo systemctl enable odm360dashboard.service

echo "************************************"
echo Now you should have a $model set up as a Parent for an ODM360 rig.
echo "************************************"
echo
