#!/bin/bash

# Set up a Raspberry Pi as an ODM360 Child.

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

echo Running base pi setup
provisioning/base_pi_setup.sh

echo Running child setup script
provisioning/child_pi_setup.sh

echo Running database setup script
provisioning/database_setup_child.sh

echo "************************************"
echo Now you should have a $model set up as a Child for an ODM360 rig.
echo "************************************"
echo

echo Rebooting to enable camera in 15 seconds...
sleep 15s
sudo reboot
