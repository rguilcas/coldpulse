import os
from tqdm import tqdm
import xarray as xr
import pandas as pd

def prepare_darray(input_dir):
    """
    Prepares darray from several csv files in the directory input_dir

    Parameters
    ----------
    input_dir : String
       Path of the input directory which contains csv files

    Returns
    -------
    complete_dataarray : xarray DataArray
        Temperature data in a DataArray

    """
    # Name format: locationID_lon_lat_depth_.csv
    # The depths should be in m positive down.
    list_files_in_dir = os.listdir(input_dir)
    list_csv_files = []
    for file in list_files_in_dir:
        if file.split('.')[-1] == 'csv':
            list_csv_files.append(file)
    assert len(list_csv_files) > 1,\
        "At least two csv files are required, %s found in %s."\
            %(len(list_csv_files), input_dir)
    depths_dict = dict()
    for file in list_csv_files:
        file_metadata = file.split('_')
        assert len(file_metadata) == 5,\
            "The name format of %s is not correct.\n \
                Please make sure all files follow this formatting style: \
                \n locationID_longitude_latitude_depth_.csv\
                \n Don't forget the underscore before .csv."%file
        location_id, longitude, latitude, depth, format = file_metadata
        depths_dict[file] = float(depth)
    
    dataarray_data_list = []
    print('Loading files...')
    for file in list_csv_files:
        dataarray_data_list.append(csv_to_darray(input_dir,
                                                 file,
                                                 depths_dict[file]))
        print("  "+u"\u21B3" + "  %s loaded."%file)
    potential_starts = []
    potential_ends = []
    potential_time_intervals = []
    sorted_dataarray_list = []
    for dataarray in dataarray_data_list:
        no_duplicate_dataarray = dataarray.groupby('time').first()
        sorted_dataarray = no_duplicate_dataarray.sortby('time', ascending=True)
        sorted_dataarray_list.append(sorted_dataarray)
        start_time = sorted_dataarray.time.values[0]
        end_time = sorted_dataarray.time.values[-1]
        time_interval_raw = sorted_dataarray.time.diff('time').values[0]
        time_interval = time_interval_raw.astype('timedelta64[s]').astype(int)
        potential_starts.append(start_time)
        potential_ends.append(end_time)
        potential_time_intervals.append(time_interval)

    total_start_time = max(potential_starts)
    total_end_time = min(potential_ends)
    total_time_interval = max(potential_time_intervals)
    time_array =pd.date_range(start=total_start_time,
                              end=total_end_time,
                              freq='%ss'%total_time_interval)
    interpolated_dataarray_list = []
    for dataarray in sorted_dataarray_list:
        interpolated_dataarray = dataarray.interp(time=time_array)
        interpolated_dataarray_list.append(interpolated_dataarray)
    complete_dataarray = xr.concat(interpolated_dataarray_list,
                                   dim = 'depth')
    complete_dataarray['locationID'] = location_id
    latitude = float(latitude)
    longitude = float(longitude)
    if longitude < 0:
        longitude += 360
    complete_dataarray['longitude'] = longitude
    complete_dataarray['latitude'] = latitude
    
    return complete_dataarray

# =============================================================================
# Side input functions    
# =============================================================================

def csv_to_darray(input_dir, file_name, depth):
    """
    Imports a csv file and make a dataarray out of it

    Parameters
    ----------
    input_dir : String
        Name of the input directory.
    file_name : String
        Name of the csv file.
    depth : float
        Depth corresponding to the csv file, positive down.

    Returns
    -------
    darray : xarray DataArray
        Temperature data

    """
    time_column = 0
    temp_column = 1
    df = pd.read_csv('%s/%s'%(input_dir,file_name))
    time_col = df.columns[time_column]
    temp_col = df.columns[temp_column]
    time = pd.DatetimeIndex(df[time_col])
    temp = df[temp_col].astype(float)
    temp.index = time
    temp.index.name='time'
    temp = temp.rename('temperature')
    darray = xr.DataArray(temp)
    if depth<5:
        depth=5
    darray['depth'] = depth
    return darray
   