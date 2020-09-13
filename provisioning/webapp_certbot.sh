#!/bin/bash -eu

# Grabs a letsencrypt cert if for some reason you need one

echo Unless you need this (i.e. you are on a cloud dev instance), do not.
echo please enter the domain name of your server
read domain_name
echo
echo Please enter an email address for certificate renewal information
read email
echo

echo installing Certbot
if ! type "certbot"; then
    sudo add-apt-repository -y ppa:certbot/certbot
    sudo apt install -y python-certbot-nginx
else echo Certbot seems to be already installed
fi

echo Procuring a certificate for the site from LetsEncrypt using Certbot
sudo certbot --nginx -n --agree-tos --redirect -m $email -d $domain_name -d www.$domain_name
