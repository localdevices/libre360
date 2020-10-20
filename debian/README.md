# Debian Packaging

ODM360's software consists of a number of utilities that run on a set of Raspberry Pi system-on-a-chip computers, generally one for each camera (the "children") and one controlling the whole rig (the "parent"). To simplify installation, the whole project is provided as a set of [Debian packages](https://en.wikipedia.org/wiki/Deb_(file_format)). These install on [Raspberry Pi OS](https://www.raspberrypi.org/downloads/raspberry-pi-os/) using the standard [dpkg](https://en.wikipedia.org/wiki/Dpkg) utility.

## How the packages are created and served
We use a continuous integration system based on  [github actions](https://docs.github.com/en/free-pro-team@latest/actions).

When a GitHub repo is modifed (such as when someone does a git push), GitHub checks for a file in the directory ```.github/workflows```. In this case, it finds ```.github/workflows/debian.yml``` which is set to execute ```on:push``` (whenever someone pushes). This file contains a workflow called  ```build-packages```, which creates a set of virtual machines on which to build installable packages for the Raspberry Pi's (which use [armhf](https://wiki.debian.org/ArmHardFloatPort) architecture). 

After building the packages, the workflow creates a Git branch of the repository called apt-repo, which contains only a set of packages (it's actually slightly misleading to think of apt-repo as a "normal" branch of the repository, as it contains nothing but the packages; it's simply using Git's branch functionality to create a set of packages based on the latest code in the "real" repository).

The apt-repo branch is then served as a set of package repositories&mdash;they function as a Web endpoint with the structure and function of a Debian repo (one for each branch other than apt-repo itself). These repos can be added to the ```/etc/apt/sources.list``` and installed directly from the Internet onto the Pi's. 

For example, add ```deb [trusted=yes] https://github.com/OpenDroneMap/odm360/blob/apt-repo/ main odm360``` to ```/etc/apt/sources.list```. 

