#!/bin/bash

# Set up a Postgresql database ready for use with odm360

echo Installing posgresql
sudo apt install -y postgresql postgresql-contrib libpq-dev

echo Creating postgres user libre360
sudo -u postgres psql -c "CREATE ROLE libre360 WITH PASSWORD 'zanzibar';"
sudo -u postgres psql -c "ALTER ROLE libre360 WITH LOGIN"
sudo -u postgres psql -c "ALTER ROLE libre360 WITH SUPERUSER"

echo Creating database odm360
sudo -u postgres psql -c "CREATE DATABASE libre360 WITH OWNER libre360;"


echo ##########################################################
echo Now you should have a Postgresql database with a user and password properly configured to connect to using psycopg2 from Python.
echo ##########################################################
echo
