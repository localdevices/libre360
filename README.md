# odm360

## Overview

This repository contains code for the EECS 398 group working on the odm360 project with the Cleveland Metroparks. The idea is to build a 360 camera from individual cameras for the purposes of high quality 3D reconstructions in challenging environments where drones don't work or don't work well.

![](images/cameras5.jpg)

In our specific use case this is built around Sony α6000 using [gphoto2](http://gphoto.org/), but this could be extended to include other cameras, especially other cameras supported by gphoto2 or [that fancy new Raspberry Pi camera](https://www.raspberrypi.org/products/raspberry-pi-high-quality-camera/).

![](images/overallschematic.JPG)

For this implementation, we are using 5 Sony α6000's using a manual Rokinon 2.8/10mm lens. One additional camera could be integrated pointed straight up in cases where the skyward data was beneficial, e.g. urban canyons or heavily forested areas.

Control is via physical buttons and switches to maximize the use of muscle memory and simplify maintenance.

![](images/gpiolayout.JPG)

From the 360 data, we can get detailed 3D reconstructions in OpenDroneMap:

![](images/points.jpg)

See also: https://www.opendronemap.org/2020/05/360-cameras/

## Quickstart on Raspberry Pi
This is a quick listing of install steps, intended for someone who already knows most of what's needed and just needs a checklist/reminder. [Full instructions here](provisioning/setup_pi.md).

- Buy Pis, SD cards, cameras, wires, GNSS receivers, etc. [Parts list here](provisioning/setup_pi.md).
- Solder, jumper, assemble, etc. [Instructions here](provisioning/setup_pi.md).
- Flash parent SD card with [Raspberry Pi OS](https://www.raspberrypi.org/downloads/raspberry-pi-os/)
- Add empty ```ssh``` file and appropriate ```wpa_supplicant.conf``` [like this]((https://www.raspberrypi.org/documentation/configuration/wireless/headless.md) with wifi info to boot partition on that SD card. Put it in the parent Pi and start it up.
- SSH into the pi ```ssh pi@raspberrypi.local``` with password ```raspberry```.
- Change the default password ```passwd```, update, upgrade ```sudo apt update && sudo apt upgrade -y``` and install Git ```sudo apt install git -y```.
- Clone odm360 repo ```git clone https://github.com/OpenDroneMap/odm360.git```, cd into the folder ```cd odm360```
- Run provisioning/base_pi_setup.sh ```provisioning/base_pi_setup.sh```
- Run the web app with ```python3 -m flask run --host=0.0.0.0```
- See the dashboard by going to [http://raspberrypi.local:5000/](http://raspberrypi.local:5000/) in your browser

## Requirements

This project is built around raspbian, but can likely be deployed on almost any linux flavor.

If you wish to test and develop code, we recommend establishing a Miniconda environment.
When deploying on a raspberry pi, you can skip this part. 
```
conda env create -f environment.yml
```
Before installation, make sure you have the gphoto2 library installed with
```
sudo apt install libgphoto2-dev
```
Additional libraries that need installation in case raspbian lite is used are:
```
sudo apt-get install git libatlas-base-dev gfortran python3-pip
```
If you are working on a isolated conda environment, then first activate it.
```
conda activate odm360
```
Retrieve and install (as developer) this repository:
```
git clone https://github.com/OpenDroneMap/odm360.git
cd odm360
pip3 install -e .
```

## Enabling the raspberry pi camera
To ensure you can communicate with a raspberry pi camera through a serial connection, please go through the following steps on a child node
```
sudo raspi-config
```
Select 