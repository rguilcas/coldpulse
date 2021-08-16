import sys
import numpy as np
import xarray as xr
import pandas as pd
from scipy.signal import argrelmax
from .detection import pulses_detection

def get_output(darray, input_dir):
    """
    Generates output from te TSI method

    Parameters
    ----------
    darray : xarray DataArray
        Temperrature input data.
    lon : Float
        Longitude of the location studied.
    lat : Float
        Latitude of the location studied
    manual_threshold : Float
        manual TSI threshold that can be computed from local climatology
    Returns
    -------
    df_output : pandas DataFrame
        DataFrame containing information about individual pulses.
    ds_output : xarrray Dataset
        Dataset including drops and degree cooling hours data.


    """
    list_starts, list_ends = pulses_detection(darray, input_dir)
    df_output_sub, ds_output,df_output = prepare_output(darray, list_starts, list_ends) 
    return df_output_sub, ds_output, df_output
    
def save_output(df_subpulse, df_pulse, ds_output, file_name, dir_name = None):
    """
    Saves output files

    Parameters
    ----------
    df_output : pandas DataFrame
        DataFrame including all pulses and subpulses.
    ds_output : xarray Dataset
        Dataset including drops and degree coolgin hours data.
    file_name : String
        Name to use to save the files.
    dir_name : String
        Directory in where to save the files. If None, will be saved in the
        current directory.
    
    Returns
    -------
    None.

    """
    df_pulse.to_csv('%s/%s_pulse_stats_.csv'%(dir_name,file_name))
    df_subpulse.to_csv('%s/%s_subpulse_stats_.csv'%(dir_name,file_name))
    ds_output.to_netcdf('%s/%s_pulse_series_.nc'%(dir_name,file_name))



# =============================================================================
# Output side functions
# =============================================================================

def prepare_output(darray, list_starts, list_ends):
    """
    Computes degree cooling hours and temperature drops for cold-pulses detected

    Parameters
    ----------
    darray : xarray DataArray
        Temperature data
    list_starts : numpy 1d array
        Array containing start indexes of found pulses.
    list_ends : numpy 1d array
        Array containing start indexes of found pulses.

    Returns
    -------
    dataframe_starts_ends_subpulses : pandas DataFrame
        DataFrame including all pulses and subpulses.
    ds : xarrray Dataset
        Dataset including drops and degree cooling hours data.

    """
    bottom_temperature = darray.sel(depth=darray.depth.max())
    dataframe_starts_ends_subpulses = split_pulses(bottom_temperature, 
                                                   list_starts,
                                                   list_ends)
    dt = bottom_temperature.time.diff('time').values[0].astype('timedelta64[s]').astype(int)
    list_dch = []
    list_drops = []
    list_min_temp = []
    dch_series = np.nan*np.zeros(bottom_temperature.size)
    drops_series = np.nan*np.zeros(bottom_temperature.size)
    min_temp_series = np.nan*np.zeros(bottom_temperature.size)
    temp_series = np.nan*np.zeros(bottom_temperature.size)
    sys.stdout.write("\r+'                                                   ")
    for index in range(dataframe_starts_ends_subpulses.shape[0]):
        progress = index/dataframe_starts_ends_subpulses.shape[0]*100
        sys.stdout.write('\r' + 'Computing DCH: %.02f'%progress + r'%')
        pulse_id, start_pulse, end_pulse, start_subpulse, end_subpulse = \
            dataframe_starts_ends_subpulses.iloc[index]
        dch = -(bottom_temperature[start_subpulse:end_subpulse] - bottom_temperature[start_pulse])*dt
        drop = (bottom_temperature[start_subpulse:end_subpulse] - bottom_temperature[start_pulse]).min('time').values
        min_temp = bottom_temperature[start_subpulse:end_subpulse].min('time').values
        list_dch.append(dch.sum().values)
        list_drops.append(drop)
        list_min_temp.append(bottom_temperature[start_subpulse:end_subpulse].min('time').values)
        dch_series[start_subpulse:end_subpulse] = dch
        drops_series[start_subpulse:end_subpulse] = drop
        min_temp_series[start_subpulse:end_subpulse] = min_temp
        temp_series[start_subpulse:end_subpulse] = bottom_temperature[start_subpulse:end_subpulse]
    dataframe_starts_ends_subpulses['dch_subpulse'] = list_dch
    dataframe_starts_ends_subpulses['drop_subpulse'] = list_drops
    dataframe_starts_ends_subpulses['min_temp_subpulse'] = list_min_temp
    dataframe_starts_ends_subpulses['duration_subpulse'] = \
        dataframe_starts_ends_subpulses.end_subpulse - dataframe_starts_ends_subpulses.start_subpulse  
    dataframe_pulses_group = dataframe_starts_ends_subpulses.groupby('pulse_id')
    dataframe_pulse = pd.DataFrame()
    dataframe_pulse['start_pulse'] =   dataframe_pulses_group.start_pulse.first()
    dataframe_pulse['start_time'] = bottom_temperature.time.values[dataframe_pulse['start_pulse']]
    dataframe_pulse['end_pulse'] =   dataframe_pulses_group.end_pulse.first()
    dataframe_pulse['end_time'] = bottom_temperature.time.values[dataframe_pulse['end_pulse']]
    dataframe_pulse['number_subpulses'] =   dataframe_pulses_group.start_pulse.count()
    dataframe_pulse['dch_pulse'] =   dataframe_pulses_group.dch_subpulse.sum()
    dataframe_pulse['drop_pulse'] =   dataframe_pulses_group.drop_subpulse.min()
    dataframe_pulse['min_temp_pulse'] =   dataframe_pulses_group.min_temp_subpulse.min()
    dataframe_pulse['duration_pulse'] =   (dataframe_pulse.end_pulse-dataframe_pulse.start_pulse)*dt
    dch_darray = xr.DataArray(dch_series,
                              dims = ['time'],
                              coords = dict(time=bottom_temperature.time))
    drops_darray = xr.DataArray(drops_series,
                                dims = ['time'],
                                coords = dict(time=bottom_temperature.time))
    pulse_temp_darray = xr.DataArray(temp_series,
                                     dims = ['time'],
                                     coords = dict(time=bottom_temperature.time))
    min_temp_darray = xr.DataArray(min_temp_series,
                                   dims = ['time'],
                                   coords = dict(time=bottom_temperature.time))
    
    ds = xr.Dataset(dict(dch = dch_darray, 
                         drops = drops_darray,
                         min_temp=min_temp_darray,
                         pulse_temp=pulse_temp_darray,
                         temperature =darray))
    sys.stdout.write("\r+'                                                   ")
    sys.stdout.write('\r' + 'Metrics computed !')
    
    return dataframe_starts_ends_subpulses, ds, dataframe_pulse


def split_pulses(bottom_temperature, list_starts, list_ends):
    """
    Splits pulses following method for DCH computation

    Parameters
    ----------
    bottom_temperature : xarray DataArray
        Bottom temperature data
    list_starts : numpy 1d array
        Array containing start indexes of found pulses.
    list_ends : numpy 1d array
        Array containing start indexes of found pulses.
        
    Returns
    -------
    dataframe_starts_ends_subpulses : pandas DataFrame
        DataFrame containing start and end indexes of each subpulse

    """
    #Combine pulses if they overlap
    is_pulse_present = np.zeros(bottom_temperature.size)
    sys.stdout.write("\r+'                                                   ")
    for k in range(list_starts.size):
        progress = list_starts[k]/is_pulse_present.size*100
        sys.stdout.write('\r' + 'Removing overlap: %.02f'%progress + r'%')
        is_pulse_present[list_starts[k]:list_ends[k]] = 1
        is_pulse_present_grad = np.diff(is_pulse_present)
    if is_pulse_present[0]:
        is_pulse_present_grad[0] = 1
    if is_pulse_present[-1]:
        is_pulse_present_grad[-1] = -1
    list_starts_no_overlap = np.where(is_pulse_present_grad == 1)[0]
    list_ends_no_overlap = np.where(is_pulse_present_grad == -1)[0]
    #Divide pulses if the temperature gets warmer than the initial temperature
    list_starts_no_overlap_split = []
    list_ends_no_overlap_split = []
    sys.stdout.write("\r+'                                                   ")
    for k in range(list_starts_no_overlap.size):
        init_start = list_starts_no_overlap[k]
        progress = init_start/list_ends[-1]*100
        sys.stdout.write('\r' + 'Splitting pulses: %.02f'%progress + r'%')
        init_end = list_ends_no_overlap[k]
        pulse_done = False
        decreasing_temperature = \
            np.where(bottom_temperature[init_start:init_end].diff('time') < 0)[0]
        is_temperature_decreasing = \
            decreasing_temperature.size > 0
        if is_temperature_decreasing:
            init_start = init_start + decreasing_temperature[0]
        else:
            pulse_done = True
        while not pulse_done:
            init_temp = bottom_temperature[init_start]
            warmer_temperature_than_init = \
                np.where(bottom_temperature[init_start:init_end] > init_temp)[0]
            is_temperature_warmer_than_init = \
                warmer_temperature_than_init.size > 0
            if is_temperature_warmer_than_init:
                new_end = init_start + warmer_temperature_than_init[0]
                list_starts_no_overlap_split.append(init_start)
                list_ends_no_overlap_split.append(new_end)
                decreasing_temperature = \
                    np.where(bottom_temperature[new_end:init_end].diff('time') < 0)[0]
                is_temperature_decreasing = \
                    decreasing_temperature.size > 0
                if is_temperature_decreasing:
                    init_start = new_end + decreasing_temperature[0]
                else:
                    pulse_done = True
            else:
                list_starts_no_overlap_split.append(init_start)
                list_ends_no_overlap_split.append(init_end)
                pulse_done = True
    list_starts_no_overlap_split = np.array(list_starts_no_overlap_split)
    list_ends_no_overlap_split = np.array(list_ends_no_overlap_split)
    #Divide into subpulses
    list_starts_ends_subpulses = []
    sys.stdout.write("\r+'                                                   ")
    for k in range(list_starts_no_overlap_split.size):
        start = list_starts_no_overlap_split[k]
        progress = start/list_ends[-1]*100
        sys.stdout.write('\r' + 'Finding subpulses: %.02f'%progress + r'%')
        end = list_ends_no_overlap_split[k]
        temp_extract = bottom_temperature[start:end]
        local_maxima = argrelmax(temp_extract.values)[0]
        local_maxima = np.insert(local_maxima, 0, 0)
        local_maxima += start
        local_maxima = np.insert(local_maxima, len(local_maxima), end)
        
        for i in range(local_maxima.size-1):
            data_subpulse = [k, start, end, local_maxima[i], local_maxima[i+1]]
            list_starts_ends_subpulses.append(data_subpulse)
    dataframe_starts_ends_subpulses = pd.DataFrame(list_starts_ends_subpulses,
    					   columns=['pulse_id',
    					   			'start_pulse',
    					   			'end_pulse',
    					   			'start_subpulse',
    					   			'end_subpulse'])
    return dataframe_starts_ends_subpulses
