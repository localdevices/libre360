#!/bin/bash

# Set up a Raspberry Pi with the basic infrastructure used by ODM360
# Normally followed by a second script which sets up either a Parent or Child

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

# Check if on RPi before doing stuff specific to Pi
if [[ onpi == "yes" ]]; then
    # TODO check if already done before sedding in the disable flag
    echo Disabling IPv6
    sudo sed -i '$s/$/ ipv6.disable=1/' /boot/cmdline.txt
    
    echo Disabling serial console to free up UART serial line
    sudo sed -i 's/console=serial0,115200 //g' /boot/cmdline.txt
    
    # TODO check if already done before pushing this line into the file
    echo enabling UART
    echo $'\n# Enable UART\nenable_uart=1' | sudo tee -a /boot/config.txt

    echo Making perl shut up about locales
    echo by setting to en_US.UTF-8
    export LANGUAGE=en_US.UTF-8
    export LANG=en_US.UTF-8
    export LC_ALL=en_US.UTF-8
    sudo sed -i "s/# en_US.UTF-8/en_US.UTF-8/g" /etc/locale.gen
    sudo locale-gen
fi

echo updating
sudo apt update && sudo apt upgrade -y

echo Installing ODM infrastructure
sudo apt install -y git python3-pip libgphoto2-dev libatlas-base-dev gfortran

echo Installing emacs because it is the best editor and IDE. You are welcome.
sudo apt install -y emacs-nox

echo Installing requirements from setup.py using pip
pip3 install -e .

echo ************************************
echo Now you should have a $model set up with the basic infrastructure common to all devices in the ODM360 rig. The next steps depend whether this device is intended to be a Parent or Child.
echo ************************************
echo
