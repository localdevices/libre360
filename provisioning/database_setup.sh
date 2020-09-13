#!/bin/bash

# Set up a Postgresql database ready for use with odm360

echo Installing posgresql
sudo apt install -y postgresql postgresql-contrib libpq-dev

# echo Installing requirements from setup.py using pip
# pip3 install -e .

echo Creating postgres user odm360
sudo -u postgres psql -c "CREATE USER odm360 WITH PASSWORD 'md51bb536130df443a4bb77eaf446bca7ca';"

echo Creating database odm360
sudo -u postgres psql -c "CREATE DATABASE odm360 WITH OWNER odm360;"




echo ##########################################################
echo Now you should have a Postgresql database with a user and password properly configured to connect to using psycopg2 from Python.
echo ##########################################################
echo
