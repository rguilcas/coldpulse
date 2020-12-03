# cold_pulses
# Detection of cold water intrusion in a weakly-stratified environment.
*Robin Guillaume-Castel - 2020*

*Contact : r.guilcas@outlook.com*
 

This package allows you to accurateley detect individual cold pulses events in a time series over several depths.

## Before the first run
### Preparing your Python environment

***If Python is already installed on your machine and is ready to use from command line, skip this step***

Before anything, you need to install Python on your machine. We suggest downlading the [Anaconda environment] ( https://www.anaconda.com/). If you are using Windows, make sure to tick the box `Add anaconda to your PATH` when installing it. If you are using Mac, this should be automatic.

### Donwloading the `cold_pulses` package

Once python is installed, open a command prompt window, and install the `cold_pulse` package by typing: 
```
pip install https://github.com/rguilcas/cold_pulses/zipball/master
```
### Downloading NCEP-GODAS climatological data

You can download NCEP-GODAS data that suit your location using [this link](https://psl.noaa.gov/cgi-bin/db_search/DBSearch.pl?Dataset=NCEP+GODAS&Variable=potential+temperature&group=0&submit=Search). Download data as a NETCDF (.nc) format from 1980 to 2020 to get a climatology of the temperature at the location studied. Note that you should include AT LEAST all depth values between your shallowest and deepest logger, including those loggers' depths. For example, if your loggers are at depthranging from 7 to 56, download data for 5, 15, 25, 35, 45, 55 and 65 m deep. We advise you to download slightly more than what you think you need. Once your NCEP-GODAS file is downloaded, rename it "NCEP-GODAS_ocean-temp_1980-2020.nc"

## Before each run

### Preparing input directory

- Create a new folder to work with cold-pulses detection
- Add the `NCEP-GODAS_ocean-temp_1980-2020.nc` to this folder
- Download the [`processing_TSI.py`](https://raw.githubusercontent.com/rguilcas/cold_pulses/master/processing_TSI.py) file and add it to the folder (Left click on the link, then right click on the background, save as `processing_TSI.py`)
- Create a new folder for each of the runs you would like to do. One run corresponds to one location and one temporal period. You need two files at different depths for each run to make the algorithm work.

### Choosing Input files

Each of your run folders should include two separate csv files: one for each depth. These files should follow:
- The files should show data from the same location
- The files should show data from different depth levels
- **Each file should be in two columns representing time and temperature, in this order**.
Note that the processing will be done on the temporal intersection between the two files. The sample frequency used will be the lowest one (if one file has a sampling rate of 30min and the other of 5 min, the processing will be done on a 30 min basis).

### Formatting input files

This script works automatically if the files' names follow one rule. Each file should be named as:


**island_locationID_longitude_latitude_depth_.csv**.


- longitude in °E
- latitude in °N
- depth in meters, positive down

For example, for a location North of Palmyra atoll, in the central Pacific, at 26 meters deep, the name of the file would be:


**palmyra_north_-162.07808_5.89682_26_.csv**


Your directories should look like in the following figure. Note that you can name the run folders as you want, as long as **their names do 
not include spaces**.
![Working directory and run folders formatting](https://github.com/rguilcas/cold_pulses/blob/master/Image1.png?raw=true)

## Run the algorithm

Once your working directory is ready, you can run the algorithm. Open a command prompt and navigate to your working directory. Note that if you are using Windows and your working directory is in a different disk to the one displayed on the prompt, start by changing disk by typing the letter of your disk followed by a semi column. To navigate to your working directory, type 'cd' followed by your working directory path in the command prompt. For example:
```
cd C:\Users\Robin\working_directory
```

Once you are in your working directory, type in the command prompt:
```
python processing_TSI.py
```
This will start the script and create output files that will be in a new folder in your input folder. 

## Outputs

After running the algorithm, a new output folder will be created for each run folder. Each of these output folder contain two files called `..._pulse_data.nc` and `..._pulse_stats.csv`.

### pulse_data.nc

This file contain instantaneous information on pulses in the studied time series. 
Its coordinates are the following:
- time: timestamps of the studied time series
- depth: depths of the different input csv files
- lon: longitude of the studied location
- lat: latitude of the studied location
Its variables are the following:
- dch: Instantaneous degree cooling hours (DCH). These are computed as the difference between the instantaneous temperature at the deepest logger and the pre-pulse temperature at the deepest logger, multiplied by the time step. If there is a pulse, this is positive. If there is no pulse, this value is **NaN**
- drops: associated temperature drops. It is conputed as the temperature drop induced by the pulse, i.e. the difference between the instantaneous temperature at the deepest logger and the pre-pulse temperature at the deepest logger.
- min_temp: minimum associtated temperature drop with the ongoing subpulse. When there is no pulse, the value is a **NaN**
- pulse_temp: bottom temperature data when a pulse is present, otherwise it is a **NaN**
- temperature: all temperature data over which the processing was done.

###  pulse_stats.csv

This file contain various statistics on each pulse detected. A pulse is first divided into subpulses. One subpulse is defined between two local maxima. Each line of the csv file gives the following information on the subpulse:
- pulse_id: the ID number of the pulse 
- start_pulse: the start index of the pulse in the time series provided in the pulse_data.nc file
- end_pulse: the end index of the pulse in the time series provided in the pulse_data.nc file
- start_subpulse: the start index of the subpulse in the time series provided in the pulse_data.nc file
- end_subpulse: the end index of the subpulse in the time series provided in the pulse_data.nc file
- dch_subpulse: the cumulative Degree Cooling Hours of the subpulse
- drop_subpulse: the maximum associated temperature drop of the subpulse
- min_temp_subpulse: the minmum temperature reached by the subpulse
- duration subpulse: the duration of the subpulse

Information on complete pulses can be obtained by grouping data by pulse_id and then processing the columns (summing DCH or duration, getting the minimum drop or the minimum temperature,...)
 
## Acknwoledgements

