#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name="libre360",
    description="libre360 is a python package to control a 360 camera with uBlox positioning setup",
    long_description=readme + "\n\n",
    url="https://github.com/localdevices/libre360",
    author="Rainbow Sensing",
    author_email="info@rainbowsensing.com",
    packages=find_packages(),
    package_dir={"libre360": "libre360"},
    test_suite="tests",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    python_requires=">=3.6",
    install_requires=[
        "pyserial",
        "numpy",
        "pytz",
        "tzlocal",
        "uuid",
        "zipstream",
        "gphoto2",
        "schedule",
        "picamera",
        "python-nmap",
        "Flask",
        "Flask-Login",
        "Bootstrap-Flask",
        "psycopg2",
        "uwsgi",
        "gpsd-py3",
    ],
    extras_require={"dev": ["pytest", "pytest-cov", "black"], "optional": [],},
    scripts=["bin/libre360"],
    entry_points="""
    """,
    include_package_data=True,
    license="AGPLv3",
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
    keywords="opendronemap topography photogrammetry data-science libre360",
)
