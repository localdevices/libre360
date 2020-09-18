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

echo Running database setup script
./database_setup.sh

echo Installing requirements from setup.py using pip
pip3 install -e .

echo putting ~/.local/bin on PATH for flask
export PATH="$HOME/.local/bin:$PATH"
echo and appending line to .bashrc to always do that
# TODO check if already done
echo export PATH="$HOME/.local/bin:$PATH" | sudo tee -a "$HOME/.bashrc"

echo "************************************"
echo Now you should have a $model set up as a Parent for an ODM360 rig.
echo "************************************"
echo
