#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name="odm360",
    description="odm360 is a python package to control a 360 camera uBlox positioning setup",
    long_description=readme + "\n\n",
    url="https://github.com/OpenDroneMap/odm360",
    author="Stephen Mather",
    author_email="svm@clevelandmetroparks.com",
    packages=find_packages(),
    package_dir={"odm360": "odm360"},
    test_suite="tests",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    python_requires=">=3.6",
    install_requires=[
        "pySerial",
        "numpy",
        "pytz",
        "tzlocal",
        "uuid",
        "gphoto2",
        "schedule",
        "picamera",
        "python-nmap",
        "Flask",
        "Flask-Login",
        "Bootstrap-Flask",
        "uwsgi",
        "psycopg2",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov", "black"],
        "optional": [],
    },
    scripts=["bin/odm360"],
    entry_points="""
    """,
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Photogrammetry",
        "License :: OSI Approved :: ???",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="opendronemap topography photogrammetry data-science odm360",
)
