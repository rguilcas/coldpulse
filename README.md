# Quantifying upwelling in tropical shallow waters
## A novel method using a temperature stratification index
*Published in L&O Methods - 2021* - [Link](https://aslopubs.onlinelibrary.wiley.com/doi/abs/10.1002/lom3.10449)

**Robin Guillaume-Castel, Gareth J. Williams, Justin S. Rogers, Jamison M. Gove, J.A. Mattias Green**

*Contact : r.guilcas@outlook.com*
 
This package allows you to accurateley detect individual cold pulses events in a time series over several depths.

Details on the method can be found in the paper.

## Before the first run
### Preparing your Python environment

***If Python is already installed on your machine and is ready to use from command line, skip this step***

Before anything, you need to install Python on your machine. We suggest downlading the [Anaconda environment] (https://docs.anaconda.com/anaconda/install/index.html).

### Donwloading the `cold_pulses` package

Once python is installed, open a command prompt window, and install the `coldpulse` package by typing: 
```
pip install https://github.com/rguilcas/coldpulse/zipball/master
```
## Before each run

### Preparing input directory

- Create a new folder to work with cold-pulses detection

- Download the [`processing_TSI.py`](https://raw.githubusercontent.com/rguilcas/coldpulse/master/processing_TSI.py) file and add it to the folder (Left click on the link, then right click on the background, save as `processing_TSI.py`)
- Create a new folder for each of the runs you would like to do. One run corresponds to one location and one temporal period. You need two files at different depths for each run to make the algorithm work.
- Once you have created your folders, update the `list_input_dir` field with the names of your new folders. The list should be:
```
list_input_dir = ['folder1', 'folder2', 'folder3']
```
### Choosing Input files

Each of your run folders should include two separate csv files: one for each depth. These files should follow:
- The files should show data from the same location
- The files should show data from different depth levels
- **Each file should be in two columns representing time and temperature, in this order**.
Note that the processing will be done on the temporal intersection between the two files. The sample frequency used will be the lowest one (if one file has a sampling rate of 30min and the other of 5 min, the processing will be done on a 30 min basis).

### Formatting input files

Before running the script, you should make sure the files follow a specific formating:

```
locationID_longitude_latitude_depth_.csv
```
**Don't forget the underscore before .csv**

- longitude in °E
- latitude in °N
- depth in meters, positive down

For example, for a location North of Palmyra atoll, in the central Pacific, at 26 meters deep, the name of the file would be:


**PalmyraNorth_-162.07808_5.89682_26_.csv**

Note that you can use `-` in your ID names.

Your full directory should look like:
→ working_directory
    → processing_TSI.py
    → folder1
        → locationID1_longitude1_latitude1_depth1_.csv
        → locationID1_longitude1_latitude1_depth2_.csv
    → folder2
        → locationID2_longitude2_latitude2_depth3_.csv
        → locationID2_longitude2_latitude2_depth4_.csv

In this case, `processing_TSI.py` should be:
```python
from coldpulse import coldpulse

list_input_dir = ['folder1', 'folder2]
for input_dir in list_input_dir:
    coldpulse.upwelling_cold_pulses_detection(input_dir)
```

## Run the algorithm

Once your working directory is ready, you can run the algorithm. Open a command prompt and navigate to your `working_directory`. Once you are in your `working_directory`, type in the command prompt:
```
python processing_TSI.py
```
This will start the script and create output files that will be in a new folder in your input folder. 

## Outputs

After running the algorithm, a new output folder will be created for each run folder. Each of these output folder contain three files called `..._pulse_data.nc`, `..._pulse_stats.csv` and `..._subpulse_stats.csv`.

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

###  subpulse_stats.csv

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

### pulse_stats.csv

This file is the same as the subpulse one except in gives information on total pulses, along with the number of subpulses in one pulse.

