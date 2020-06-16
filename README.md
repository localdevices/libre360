# odm360

This repository contains code for the EECS 398 group working on the odm360 project with the Cleveland Metroparks.

To install an environment, use Miniconda and prepare an environment with
```
conda env create -f environment.yml
``` 
Before installation, make sure you have the gphoto2 library installed with
```
sudo apt install libgphoto2-dev
```
Then install odm360 as developer with
```
conda activate odm360
pip install -e .
```
