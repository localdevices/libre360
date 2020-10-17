# Debian Packaging

ODM360's software consists of a number of utilities that run on a set of Raspberry Pi system-on-a-chip computers, generally one for each camera (the "children") and one controlling the whole rig (the "parent"). To simplify installation, the whole project is provided as a set of [Debian packages](https://en.wikipedia.org/wiki/Deb_(file_format)). These install on [Raspberry Pi OS](https://www.raspberrypi.org/downloads/raspberry-pi-os/) using the standard [dpkg](https://en.wikipedia.org/wiki/Dpkg) utility.

## How the packages are created and served
We use a continuous integration system based on  [github actions](https://github.com/features/actions).

When ODM360 software is modifed (a git commit to the main branch), a series of) are triggered. These create a Git branch of the repository called apt-repo, which contains only a set of packages (it's actually slightly misleading to think of apt-repo as a "normal" branch of the repository, as it contains nothing but the packages; it's simply using Git's branch functionality to create a set of packages based on the latest code in the "real" repository).

The apt-repo branch is then served as a repository&mdash;it functions as a Web endpoint with the structure and function of a Debian repo!

#TODO explain more
