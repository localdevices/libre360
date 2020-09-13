#!/bin/bash -eu

# Sets up an ODM360 web app with wsgi and nginx
# Assumes a non-root sudo user.

echo Updating and upgrading the OS
sudo apt -y update
sudo apt -y upgrade

echo installing nginx
if ! type "nginx"; then
    sudo apt install -y nginx
else echo Nginx seems to be already installed
fi


echo adding the odm360 site to nginx
cat > odm360 <<EOF
server {
    listen 80;
    server_name localhost;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/home/pi/odm360/odm360.sock;
    }
}
EOF

sudo mv odm360 /etc/nginx/sites-available/

echo creating symlink to odm360 site in nginx sites-enabled
if [ ! -f /etc/nginx/sites-enabled/odm360 ]; then
    sudo ln -s /etc/nginx/sites-available/odm360 /etc/nginx/sites-enabled
else echo Looks like the symlink has already been created
fi

echo setting up uwsgi and flask
pip install wheel
pip install uwsgi flask

echo adding the odm360 service to Systemd
sudo cp provisioning/odm360_dashboard.service /etc/systemd/system/

echo starting and enabling the odm360_dashboard service with Systemd
sudo systemctl start odm360_dashboard.service
sudo systemctl enable odm360_dashboard.service
