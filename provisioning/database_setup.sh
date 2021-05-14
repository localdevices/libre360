#!/bin/bash

# Set up a Postgresql database ready for use with odm360

echo Installing posgresql
sudo apt install -y postgresql postgresql-contrib libpq-dev  >> provisioning/setup.log 2>> provisioning/error.log

echo Creating postgres user libre360
# TODO This is a pretty obvious password (it's md5 hashed).
# Generate another one using bash:
# echo -n passwordusername | md5sum
# and paste the result into the following command
# with the prefix 'md5' (the hash below begins with 44ec)
sudo -u postgres psql -c "CREATE ROLE libre360 WITH PASSWORD 'md5199464a7f2da85a3f9607c40864718c6';"
sudo -u postgres psql -c "ALTER ROLE libre360 WITH LOGIN"
sudo -u postgres psql -c "ALTER ROLE libre360 WITH SUPERUSER"

echo Creating database libre360
sudo -u postgres psql -c "CREATE DATABASE libre360 WITH OWNER libre360;"

echo ##########################################################
echo Now you should have a Postgresql database with a user and password properly configured to connect to using SQLAlchemy from Python.
echo ##########################################################
echo
