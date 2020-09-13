#!/bin/bash

# Set up a Postgresql database ready for use with odm360

echo Installing posgresql
sudo apt install -y postgresql postgresql-contrib libpq-dev

# echo Installing requirements from setup.py using pip
# pip3 install -e .

sudo -u postgres createuser -d odm360


echo ##########################################################
echo Now you should have a Postgresql database with a user and password properly configured to connect to using psycopg2 from Python.
echo ##########################################################
echo
