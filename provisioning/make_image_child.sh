#!/bin/bash
help() {
	echo "provide the mount point name, this has to be a mounted USB pen drive (e.g. /media/usb) as sole input"
	echo "I will make an image called libre360_child.img.gz on that pen drive for you"
}

if [[ $1 = "" ]]; then
  help
  exit 0
fi
export trg="$1/libre360_child.img"
echo $trg
sudo dd if=/dev/mmcblk0 of=$trg bs=1M
sudo /home/pi/libre360/provisioning/pishrink_libre360.sh -z $trg
