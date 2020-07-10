#!/bin/bash

sudo apt update && sudo apt upgrade -y
git clone https://github.com/tomojitakasu/RTKLIB.git
cd RTKLIB
git checkout rtklib_2.4.3
cd /app/str2str/gcc
make
cd
