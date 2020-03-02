# cold_pulses
 \h1{Detection of cold water intrusion in a weakly-stratified environment.}
 

 This package allows you to detect accurateley individual cold pulses events in a time series over several depths.


Several csv input files are necessary to make the algorithm work, you should get them ready before getting to the algorithm itself.
They should fit the folowing criteria:
- The files should show data from the same location
- The files should show data from different depth levels
- If more than two depth levels are used, the depths should be equally spaced
- Each file should be in two columns representing time and temperature, in this order.

To make the algorithm work at its best, the files should preferably:
- not show a strong daily variability
- not show a strong vertical stratification
Visual inspection could be used to observe those criteria.

We suggest using depths that are multiples of 5 to create equally spaced data. Round your files to the nearest one.

Once your files are ready, you should create a working directory in your computer.
Then, download the example files available at https://github.com/rguilcas/cold_pulses/tree/master/example_input.
This folder contains two files and one folder:
- cold_pulse_detection.py: this is the python script that we will use to launch the algorithm from command line.
- config_file.txt: this is the configuration file for the algorithm where we can change parameters like input.
- the input_folder: this is the folder where the input csv files go.

Copy these files and folder in the working directory chosen. 

Create a new folder with the name of your choice in the working directory and put your csv files in your directory.

Open the config_file.txt file in a text editor and modify the information accordingly with your files and new folder name.

The config_file is made of several lines:
- input_name:In the case where the csv files are already prepared, choose the netcdf file to open to detect pulses. This should be with the extension .nc
- input_folder:This is the directory where input csv files are stored
- bot:True if bottom pulses want to be detected, False if not
- top:True if top pulses want to be detected, False if not
- prepare_csv: True if csv files need to be prepared (made into a unique netcdf file), False if not
- time_file_name:if prepare_csv, this is the csv file that will be used for time interpolation, i.e. the time steps will be defined by this file and all other files will be linearly interpolated over these steps. 
- depths: This is where we specify the depth of each file in the input folder. The format is the following : 
		file_name1.csv:depth (depth is in meters, positive down), file_name2.csv:depth, ... 
		
!!!WARNING!!!
Make sure python is installed on your machine, along with the pip library (automatically installed on most python GUI). 
If it isn't, we suggest downloading and installing anaconda first: https://www.anaconda.com/. If on windows, you will be asked to add anaconda to your path, where you will have to tick the box.

Once python is installed ad the config_file modified, open a command prompt (anaconda prompt in windows) and go to your working directory.

If it is the first time you use the package, install the cold_pulses package using:

	pip install git+http://github.com/rguilcas/cold_pulses

Then for any other time, use from your working directory:

	python cold_pulse_detection.py

This will start the script and output two to three files in the output_dir chosen.

The files available are:
- one or two csv (bot_stats and/or top_stats) files. These files give specific information on all individual pulses detected (top or bottom pulses depending on the file)

The columns contained are:

	start_time			The starting time step of the pulse

	duration			The duration of the pulse (in minutes)

	gammaD1, gammaD2, ... 		The Degree Cooling Hours of the pulse (°C.h) for depth level 1, level 2, ... 

	dropD1, dropD2, ... 		The maximum temperature drop of the pulse for depth level 1, level 2, ...

	init_tempD1, init_tempD2,...    The initial temperature of the pulse for depth level 1, level 2, ...

	start, end 			The start and end indexes of the pulse in the time series

- one netcdf file containing time series of different parameters
		
The fields available are:
			
	temp : time series of the temperature in several depths

	dch_top (only if top was True in the config file): instantaneous degree cooling hours for top pulses at different depths

	dch_bot (only if bot was True in the config file): instantaneous degree cooling hours for bottom pulses at different depths

	pulse_temp_top (only if top was True in the config file): temperature time series where all temperature values outside of top pulses are nans

	pulse_temp_bot (only if bot was True in the config file): temperature time series where all temperature values outside of bottom pulses are nans

