#!/bin/bash

# Set up a Raspberry Pi as a Child for an ODM360 rig
echo checking if this is running on a Raspberry Pi
# for some reason this produces a cryptic Bash error
# warning: command substitution: ignored null byte in input
# but it works so I am ignoring it for now
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

# TODO set up the database specifically for a child

# Set up pi camera
if [[ "$onpi" ]]; then
    echo "" | sudo tee --append /boot/config.txt # Add blank line before camera setup in config
    echo "# Enable camera and set GPU memory to allow for maximum resolution." | sudo tee --append /boot/config.txt
    echo "start_x=1             # Enable camera" | sudo tee --append /boot/config.txt
    echo "gpu_mem=256           # Set GPU memory" | sudo tee --append /boot/config.txt
fi

echo "************************************"
echo Now you should have a $model set up as Child for an ODM360 rig.
echo 'About to reboot to enable camera... (15s)'
echo "************************************"
echo

sleep 15s

# Reboot to enable camera
sudo reboot
