#!/bin/bash

# Set up a Raspberry Pi with the basic infrastructure used by ODM360
# Normally followed by a second script which sets up either a Parent or Child

echo checking if this is running on a Raspberry Pi
# for some reason this produces a cryptic Bash error
# warning: command substitution: ignored null byte in input
# but it works so I am ignoring it for now
model="$( cat /proc/device-tree/model )" 2>> provisioning/error.log
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
if [[ $onpi == "yes" ]]; then
    # TODO check if already done before sedding in the disable flag
    echo Disabling IPv6
    sudo sed -i '$s/$/ ipv6.disable=1/' /boot/cmdline.txt
    
    echo Disabling serial console to free up UART serial line
    sudo sed -i 's/console=serial0,115200 //g' /boot/cmdline.txt
    
    # TODO check if already done before pushing this line into the file
    echo enabling UART
    echo $'\n# Enable UART\nenable_uart=1' | sudo tee -a /boot/config.txt

    # TODO: Perl whines constantly about locales.
    # Changing locale fails, apparently due to a
    # permission issue.
    # Works using raspi-config
echo Not setting locales because something is fucked
    #echo Making perl shut up about locales
    #echo by setting to en_US.UTF-8
    #sudo sed -i "s/# en_US.UTF-8/en_US.UTF-8/g" /etc/locale.gen
    #sudo locale-gen en_US.UTF-8
    # sudo update-locale en_US.UTF-8 #FAILS
    #export LANGUAGE=en_US.UTF-8
    #export LANG=en_US.UTF-8
    #export LC_ALL=en_US.UTF-8 #FAILS
fi

echo updating
sudo apt update && sudo apt upgrade -y >> provisioning/setup.log 2>> provisioning/error.log
sudo apt autoremove -y >> provisioning/setup.log 2>> provisioning/error.log

echo Installing ODM infrastructure
sudo apt install -y git python3-pip libgphoto2-dev libatlas-base-dev gfortran nmap >> provisioning/setup.log 2>> provisioning/error.log

echo Installing emacs because it is the best editor and IDE. You are welcome.
echo We assure you that this is not a waste of 160+ MB of space just to edit text
echo Y̷o̷u̷ ̷a̷r̷e̷ ̷w̷e̷l̷c̷o̷m̷e̷
sudo apt install -y emacs-nox >> provisioning/setup.log 2>> provisioning/error.log

echo Installing vim. You will have a delightful editing experience and grow spiritually. You are welcome.
echo Our sincere apologies about the emacs guy on the team. He\'s a good and 
echo useful person, in spite of this flaw.
sudo apt install -y vim >> provisioning/setup.log 2>> provisioning/error.log

echo Installing requirements from setup.py using pip
pip3 install -e . >> provisioning/setup.log 2>> provisioning/error.log

echo Installing requirements for mDNS: allows for distributed name resolution.
echo This is super useful for finding child pis based on domain name
sudo apt-get install avahi-daemon >> provisioning/setup.log 2>> provisioning/error.log


echo "************************************"
echo Now you should have a $model set up with the basic infrastructure common to all devices in the ODM360 rig. The next steps depend whether this device is intended to be a Parent or Child.
echo "************************************"
echo
