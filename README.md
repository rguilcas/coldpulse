# cold_pulses
# Detection of cold water intrusion in a weakly-stratified environment.
*Robin Guillaume-Castel - 2020*

*Contact : r.guilcas@outlook.com*
 

This package allows you to accurateley detect individual cold pulses events in a time series over several depths.

## Before the first run
### Preparing your Python environment

***If Python is already installed on your machine and is ready to use from command line, skip this step***

Before anything, you need to install Python on your machine. We suggest downlading the [Anaconda environment] ( https://www.anaconda.com/). If you are using Windows, make sure to tick the box `Add anaconda to your PATH` when installing it. If you are using Mac, this should be automatic.
`cold_pulses` package
5
### Donwloading the `cold_pulses` package

Once python is installed, open a command prompt window, and install the `cold_pulse` package by typing: 
```
pip install https://github.com/rguilcas/cold_pulses/zipball/master
```
### Downloading NCEP-GODAS climatological data

You can download NCEP-GODAS data that suit your location using [this link](https://psl.noaa.gov/cgi-bin/DataAccess.pl?DB_dataset=NCEP+GODAS&DB_variable=potential+temperature&DB_statistic=Monthly+Mean&DB_tid=84088&DB_did=98&DB_vid=1913). Download data as a NETCDF (.nc) format from 1980 to 2020 to get a climatology of the temperature at the location studied. Note that you should include AT LEAST all depth values between your shallowest and deepest logger, including those loggers' depths. For example, if your loggers are at depthranging from 7 to 56, download data for 5, 15, 25, 35, 45, 55 and 65 m deep. We advise you to download slightly more than what you think you need. Once your NCEP-GODAS file is downloaded, rename it "NCEP-GODAS_ocean-temp_1980-2020.nc"

## Before each run
### Preparing input directory
### Input files
![alt text](https://github.com/rguilcas/cold_pulses/blob/master/Image1.png?raw=true)
Before getting into the algorithm, you will need to prepare input files that will be used. Several (two or more) csv input files are necessary to make the algorithm work. They should fit the folowing criteria:
- The files should show data from the same location
- The files should show data from different depth levels
- If more than two depth levels are used, the depths should be equally spaced
- Each file should be in two columns representing time and temperature, in this order.

To make the algorithm work at its best, the files should preferably:
- not show a strong daily variability
- not show a strong vertical stratification
Visual inspection could be used to observe those criteria.

We suggest using depths that are multiples of 5 to create equally spaced data. Round your files to the nearest one.
### Preparing working directory
Once your files are ready, you should create a working directory in your computer. **All names that will be used here should not contain spaces. We suggest you only use letters, numbers and underscores.**
Then, download the [`cold_pulse_detection.py`](https://raw.githubusercontent.com/rguilcas/cold_pulses/master/example_input/cold_pulse_detection.py): right click on the link and *save link as*. This is the python script that we will use to launch the algorithm from command line.

Put the file in the working directory you created. 

Create a new folder with the name of your choice in the working directory and put your csv files in your directory. **All names that will be used here should not contain spaces. We suggest you only use letters, numbers and underscores.**

The stucture of your working directory should be:
- `working_directory`
  - `cold_pulse_detection.py`
  - `new_folder`
    - `csv_file1.csv`
    - `csv_file2.csv`
    - ...

Open the `cold_pulse_detection.py` file in Python or in a text editor and modify the information accordingly with your `.csv` files and `new_folder` names.

The `cold_pulse_detection.py` file is made of **four** sections, two of which should me adapted to your needs:
- `INPUT DATA`, **should be modified**: This is where input variables such as file names and depths should be entered. 
- `ALGORITHM PARAMETERS`, **should be modified**: This is where algorithm parameters can be changed.
- `CREATE CONFIGURATION DATA`: This is where configuration data are created from `INPUT DATA` and `ALGORITHM PARAMETERS`;
- `RUN ALGORITHM`: This is where the algorithm is run.

Note that most of the fields should be in quotation marks as this is how string should be in Python.

The `INPUT DATA` section contains:
- `INPUT_DIR`, *quotation marks needed*: Directory where the csv files are stored. You should replace the value by the name you gave to `new_folder`.
- `OUTPUT_NAME`, *quotation marks needed*: Name that will be used for output files. We recommend using a new name for each run.
- `BOT`, ***True** or **False** without quotation marks*: Should be **True** if you want to detect deep pulses, **False** if not.
- `TOP`, ***True** or **False** without quotation marks*: Should be **True** if you want to detect surface pulses, **False** if not.
- `PREPARE_CSV`, ***True** or **False** without quotation marks*: Should be **True** if your csv files have not been prepared yet, **False** if not. This will create a NetCDF file `prepared_csv.nc` in your `new_folder`. Should be **True** for the first run with new files.
- `FILE_NAMES`, *quotation marks needed*: Python *list* containing names of your csv files. Do not forget to add *.csv* at the end of each file name. A list should be in square braquets, with comas to separate each file name.
```
    FILE_NAME = ['file_name1.csv',
    		 'file_name2.csv']
```
- `FILE_DEPTHS`, *no quotation mark needed*: Python *list* containing loggers depths for each of your csv files. Depths should be in the same order as the `FILE_NAME` field. For example, the following `FILE_DEPTHS` indicates that *file_name1.csv* is from a 15 meters deep logger and *file_name1.csv* is from a 25 meters deep one:
```
    FILE_DEPTHS = [15,
                   25]
```

- `TIME_FILE_NAME`, *quotation marks needed*: Name of the file that will be used for time interpolation. All other files will be interpolated over this file's time steps to create the NetCDF file. It needs to be one of the files in the `FILE_NAME` field. Do not forget to add *.csv* at the end of the file name. If all files have the same time, the file you chose does not matter.

The `ALGORITHM PARAMETERS` section contains:
- `FILTER_MIN_DURATION`,  ***True** or **False** without quotation marks*: If **True**, a filter on minimum pulse duration will be applied.
- `MIN_DURATION`, *no quotation mark needed*: If `FILTER_MIN_DURATION` is **True**, this is what the minimum accepted pulse duration will be in minutes.
- `FILTER_MAX_DURATION`,  ***True** or **False** without quotation marks*: If **True**, a filter on maximum pulse duration will be applied.
- `MAX_DURATION`, *no quotation mark needed*: If `FILTER_MAX_DURATION` is **True**, this is what the maximum accepted pulse duration will be in minutes.
- `FILTER_MIN_DROP`,  ***True** or **False** without quotation marks*: If **True**, a filter on minimum temperature drop will be applied.
- `MIN_DROP`, *no quotation mark needed*: If `FILTER_MIN_DROP` is **True**, this is what the minimum accepted temperature drop will be in °C.
- `FILTER_STSI`,  ***True** or **False** without quotation marks*: If **True**, a filter on specific TSI will be applied.
- `AUTO_MIN_STSI`,  ***True** or **False** without quotation marks*: If `FILTER_STSI` is **True**, the minimum STSI allowed will be computed based on the rTSI instantaneous value without any input parameter.
- `MANUAL_MIN_TSI`, *no quotation mark needed*: If `FILTER_STSI` is **True** and `AUTO_MIN_STSI` is **False**, this is what the minimum specific TSI will be in °C.m².
- `RTSI_NUM_DAYS`, *no quotation mark needed*: Number of days that will be used to compute the rTSI baseline profile.
- `RTSI_STRONG_EVENT`, ***True** or **False** without quotation marks*: If **True**, the rTSI will be corrected for strong event using a maximum absolute value.
- `NUM_RIGHT_MAX`, *no quotation mark needed*: Number of minutes that define a local right maximum.

**After modifying the file, save it and close the window.**

## Run the algorithm
Once your working directory is ready and your 'cold_pulse_detection.py' is configured, you can run the algorithm. Open a command prompt and navigate to your working directory. Note that if you are using Windows and your working directory is in a different disk to the one displayed on the prompt, start by changing disk by typing the letter of your disk followed by a semi column. To navigate to your working directory, type 'cd' followed by your working directory path in the command prompt. For example:
```
cd C:\Users\Robin\working_directory
```


Once you are in your working directory, type in the command prompt:
```
python cold_pulse_detection.py
```
This will start the script and create output files that will be in a new folder in your input folder. 

## Outputs
After running the algorithm, your working directory will look like:
- `working_directory`
  - `cold_pulse_detection.py`
  - `new_folder`
    - `**csv_prepared.nc**`
    - `csv_file1.csv`
    - `csv_file2.csv`
    - ...
    - `OUTPUT_NAME_pulses_out`
      - `OUTPUT_NAME_all_data.nc`
      - `OUTPUT_NAME_bot_stats.csv`
      - `OUTPUT_NAME_top_stats.csv`
      
 Note that if only one of the `TOP` or `BOT` fields was **True**, `OUTPUT_NAME_all_data.nc` is replaced by `OUTPUT_NAME_bot_data.nc` or `OUTPUT_NAME_top_data.nc` and only the relevant *.csv* file will be present.

Those files contain different data:
- `..._pulse_data.nc` are NetCDF files containing time series of different metrics:
  - `temp` is the temperature time series in **°C**.
  - `dch_top`, `dch_bot` and `dch` are *degree cooling hours* computed for surface, deep or the relevant type of pulse in **°C.h**.
  - `pulse_temp_top`, `pulse_temp_bot` and `pulse_temp` are the temperature time series where every time step outside of a pulse is a **NaN**.
- `..._pulse_stats.csv` are *.csv* files containing information on individual pulses. Fields are:
  - `start_time` is the time step when the pulse started
  - `duration` is the duration of the pulse in minutes
  - `dchDEPTH1`, `dchDEPTH2`, ... are the degree cooling hours for all different depths
  - `dropDEPTH1`, `dropDEPTH2`, ... are the maximum temperature drops for all different depths
  - `temp_initDEPTH1`, `temp_initDEPTH2`, ... are the initial temperature for all different depths
  - `start` and `end` are the start and end indexes of the pulse in the time series
  
## Acknwoledgements

