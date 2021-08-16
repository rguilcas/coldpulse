# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:38:25 2020

@author: Robin
"""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
   	name="coldpulse",
    version="0.4.10",
    author="Robin Guillaume-Castel",
    author_email="r.guilcas@outlook.com",
    description="Cold pulse detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['numpy', 'scipy', 'xarray', 
                      'pandas', 'netcdf4', 'pydap', 
                      'dask', 'tqdm', 'h5netcdf',
                      'haversine'],
    url="https://github.com/rguilcas/coldpulses",
    include_package_data=True,
    package_data={'': ['data/*.nc']},
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
