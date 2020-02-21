# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:38:25 2020

@author: Robin
"""

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
   	name="cold_pulses",
    version="0.0.1",
    author="Robin Guillaume-Castel",
    author_email="robin.guilcas@gmail.com",
    description="Cold pulse detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['numpy','xarray','pandas'],
    url="https://github.com/typhonier/cold_pulses",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
