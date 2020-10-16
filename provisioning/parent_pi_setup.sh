#!/bin/bash

# Set up a Raspberry Pi as an ODM360 Parent. Must be run after the base_pi_setup.sh script.

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

echo Installing postgresql
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Install dnsmasq and hostapd only if on a raspi
if [[ onpi == "yes" ]]; then
  provisioning/wifi_setup.sh
fi

echo Running database setup script
provisioning/database_setup.sh

echo Installing requirements from setup.py using pip
pip3 install -e .

echo putting ~/.local/bin on PATH for flask
export PATH="$HOME/.local/bin:$PATH"
echo and appending line to .bashrc to always do that
# TODO check if already done
echo export PATH="$HOME/.local/bin:$PATH" | sudo tee -a "$HOME/.bashrc"

echo installing nginx and configuring it to use uwsgi
sudo apt install -y nginx

sudo rm /etc/nginx/sites-enabled/default
echo adding the odm360dashboard site to nginx
cat > odm360dashboard <<EOF
server {
    listen 80;
    server_name localhost;
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/odm360.sock;
    }
}
EOF

sudo mv odm360dashboard /etc/nginx/sites-available/

sudo ln -s /etc/nginx/sites-available/odm360dashboard /etc/nginx/sites-enabled/

echo adding the odm360dashboard service to Systemd
cat > odm360dashboard.service <<EOF
[Unit]
Description=uWSGI instance to serve odm360dashboard
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/pi/odm360
ExecStart=/home/pi/odm360/uwsgi --ini /home/pi/uwsgi.ini

[Install]
WantedBy=multi-user.target
EOF

sudo mv odm360dashboard.service /etc/systemd/system/
echo starting and enabling the odm360dashboard service with Systemd
sudo systemctl start odm360dashboard.service
sudo systemctl enable odm360dashboard.service

echo "************************************"
echo Now you should have a $model set up as a Parent for an ODM360 rig.
echo "************************************"
echo
