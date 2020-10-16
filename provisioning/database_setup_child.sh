#!/bin/bash

# Set up a Postgresql database ready for use with odm360

echo Installing posgresql
sudo apt install -y postgresql postgresql-contrib libpq-dev

echo Creating postgres user odm360
# TODO This is a pretty obvious password (it's md5 hashed).
# Generate another one using bash:
# echo -n passwordusername | md5sum
# and paste the result into the following command
# with the prefix 'md5' (the hash below begins with 44ec)
sudo -u postgres psql -c "CREATE ROLE odm360 WITH PASSWORD 'md544ec1a1a609f26f78f20decd3a34bd2d';"
sudo -u postgres psql -c "ALTER ROLE odm360 WITH LOGIN"
sudo -u postgres psql -c "ALTER ROLE odm360 WITH CREATEDB"

echo Creating database odm360
sudo -u postgres psql -c "CREATE DATABASE odm360 WITH OWNER odm360;"

echo Adding extensions and tables to database odm360
sudo -u postgres psql -d odm360 -f dbase_child.sql

# retrieve the child's uuid and change the hostname of child accordingly
hostname_prefix=`sudo -u postgres psql -d odm360 -t -c "SELECT (device_uuid) FROM device;"`
echo $hostname_prefix | sudo tee /etc/hostname
sudo sed -i "s/raspberrypi/$hostname_prefix/g" /etc/hosts
# make sure that the database folder is prepared
sudo mkdir /home/pi/piimages

# ensure external access to database
sudo sed -i -e "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/11/main/postgresql.conf
echo "host    all             all              0.0.0.0/0                       md5" | sudo tee -a /etc/postgresql/11/main/pg_hba.conf
echo "host    all             all              ::/0                            md5" | sudo tee -a /etc/postgresql/11/main/pg_hba.conf

echo ##########################################################
echo Now you should have a Postgresql database with a user and password properly configured to connect to using psycopg2 from Python.
echo ##########################################################
echo
