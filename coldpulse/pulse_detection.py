# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 09:08:42 2020

@author: rguil
"""
import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
from scipy.signal import argrelmax
from tqdm import tqdm
from .inputs import prepare_darray
# =============================================================================
# Main functions
# =============================================================================
def upwelling_cold_pulses_detection(input_dir,auto_in=True,ignore_double=False, manual_threshold=None):
    process = True
    list_dir= os.listdir()
    if '%s_TSI_out'%input_dir in list_dir and not auto_in:
        test = input('%s has already been used by the algorithm.\n'%input_dir+\
                     'This will erase previous data in the output folder.\n'+\
                     'Do you want to proceed? (y/n)')
        while test not in ['y','n']:
            test = input("Please answer by 'y' or 'n'")
        if test =='n':
            process = False
        
    elif '%s_TSI_out'%input_dir in list_dir and ignore_double == True and auto_in:
        process = False
    if not('%s_TSI_out'%input_dir in list_dir):
        os.mkdir('%s_TSI_out'%input_dir)
            
    if process:
        darray = prepare_darray(input_dir,auto_in=auto_in)
        
        if type(darray) != bool:
            lon = darray.lon
            lat = darray.lat
            df_output,ds_output,df_sub = get_output(darray, lon, lat, manual_threshold = manual_threshold)
            save_output(df_output,df_sub,ds_output,input_dir,dir_name='%s_TSI_out'%input_dir)
# =============================================================================
# =============================================================================
# # Input functions 
# =============================================================================
# =============================================================================

    
# =============================================================================
# =============================================================================
# # Detection functions
# =============================================================================
# =============================================================================

def pulses_detection(darray, lon, lat, manual_threshold=None):
    """
    Detects upweling-induced cold-pulses in a xarray DataArray at the longitude
    lon and the latitude lat.
    
    Parameters
    ----------
    darray : xarray DataArray
        Input temperature data.
    lon : float
        Longitude of the location studied.
    lat : float
        Latitude of the location studied.
    manual_threshold: float
        Manual TSI threshold taht can be computed from local climatology

    Returns
    -------
    filtered_starts : numpy 1d array
        final start indexes of pulses detected
    shifted_filtered_ends : numpy 1d array
        final end indexes of pulses detected

    """
 
    if lon < 0:
        lon += 360
    sys.stdout.write('\r'+'Computing TSI threshold ...')
    sys.stdout.flush()
    if manual_threshold == None:
        tsi_threshold = make_tsi_threshold_from_climatology(darray, lon, lat)
    else:
        tsi_threshold = manual_threshold
    sys.stdout.write("\r+'                                                   ")
    sys.stdout.write('\r'+'Getting initial start and end indexes ...')
    list_starts, list_ends = \
        get_potential_pulses_start_end_from_TSI(darray, threshold=tsi_threshold)
    sys.stdout.write("\r+'                                                   ")
    sys.stdout.write('\r'+'Computing TSI ...')
    phi = compute_temperature_stratification_index(darray)
    sys.stdout.write("\r+'                                                   ")
    sys.stdout.write('\r'+'Shifting starts ...')
    shifted_starts = shift_starts(list_starts, list_ends, darray, phi,
                                  use_positive_phi = True,
                                  use_increasing_phi = True,
                                  use_increasing_temp = False,
                                  use_minimum_water_column_temp = True)
    sys.stdout.write("\r+'                                                   ")    
    sys.stdout.write('\r'+'Applying heat filter ...')
    filtered_starts, filtered_ends = \
        remove_potential_pulse_if_not_from_bottom_logger(shifted_starts,
                                                          list_ends,
                                                          darray,
                                                          phi)
    sys.stdout.write("\r+'                                                   ")
    sys.stdout.write('\r'+'Shifting ends ...')
    shifted_filtered_ends = shift_ends(filtered_ends, darray, phi)
    sys.stdout.write("\r+'                                                   ")    
    sys.stdout.write('\r'+'%d Pulses detected !'%filtered_starts.size)
    return filtered_starts, shifted_filtered_ends

# =============================================================================
# Detection side functions
# =============================================================================

def get_potential_pulses_start_end_from_TSI(darray, threshold=0):
    """
    Extract start and end indexes of potential pulses from TSI below a 
    threshold
    
    Parameters
    ----------
    darray : xarray DataArray
        Represents temperature data
    
    Returns
    -------
    list_starts  : 1darray 
        Array of indexes representing the start of the TSI variability detected
    list_ends    : 1darray
        Array of indexes representing the end of the TSI variability detected
    """
    phi = compute_temperature_stratification_index(darray)
    index_bottom_logger = darray.depth.argmax('depth')
    is_potential_pulse_present = \
                (darray[index_bottom_logger] == darray.min('depth'))\
              & (phi<threshold)    
    list_starts = np.where((1*is_potential_pulse_present).diff('time')>0)[0]
    list_ends = np.where((1*is_potential_pulse_present).diff('time')<0)[0] +1
    if is_potential_pulse_present[0]:
        list_starts = np.insert(list_starts, 0, 0)
    if is_potential_pulse_present[-1]:
        list_ends = np.insert(list_ends, list_ends.size, phi.size-1)
    return list_starts, list_ends

def compute_temperature_stratification_index(darray):
    """
    Computes the temperature stratification index of a temperature time series
    
    Parameters
    ----------
    darray : xarray DataArray
        Represents temperature data
    
    Returns
    -------
    phi : xarray DataArray
        Represent the temperature stratification index
    """
    return ((darray-darray.mean('depth'))*darray.depth).mean('depth')

def shift_starts(list_starts, list_ends, darray, phi,
                 use_positive_phi = True,
                 use_increasing_phi = True,
                 use_increasing_temp = True,
                 use_minimum_water_column_temp = True):
    """
    Shifts starts indexes to get the real start of potential pulses
    
    Parameters
    ----------
    list_starts                     : 1darray 
        Array of indexes representing the start of the TSI variability detected
    list_ends                       : 1darray
        Array of indexes representing the end of the TSI variability detected
    darray                          : xarray DataArray 
        Represents temperature data
    phi                             : xarray DataArray 
        Represents the temperature stratification index
    use_positive_phi                : bool
        If true, one of the potential new indexes will be the last index when
        the temperature stratification index was positive
    use_increasing_phi              : bool
        If true, one of the potential new indexes will be the last index when
        the temperature stratification index was increasing
    use_increasing_temp             : bool
        If true, one of the potential new indexes will be the last index when
        the bottom temperature was increasing
    use_minimum_water_column_temp   : bool
        If true, one of the potential new indexes will be the last index when
        the bottom temperature was not the minimum temperature in the water 
        column
        
    Returns
    -------
    new_list_starts : 1darray
        List of shifted start indexes with chosen parameters
    """
    index_bottom_logger = darray.depth.argmax('depth')
    
    phi_series = pd.Series(phi)
    bottom_temp_series = pd.Series(darray[index_bottom_logger])
    if use_positive_phi:
        a = phi_series >= 0
    else:
        a = False*np.ones(phi_series.size)
    if use_increasing_phi:
        b = (phi_series.diff().shift(1) >= 0)
    else:
        b = False*np.ones(phi_series.size)
    if use_increasing_temp:
        c = (bottom_temp_series.diff().shift(1) >= 0)
    else:
        c = False*np.ones(phi_series.size)
    if use_minimum_water_column_temp:
        d = pd.Series((darray[index_bottom_logger] != darray.min('depth')))
    else:
        d = False*np.ones(phi_series.size)
        
    not_a_pulse = pd.DataFrame(np.transpose([a,b,c,d])).sum(axis=1) > 0
    not_a_pulse[0] = True
    potential_new_starts = np.where(not_a_pulse)[0]
    new_list_starts = []
    for start in list_starts:
        progress = start/phi.size*100
        sys.stdout.write('\r' + 'Shifting starts: %.02f'%progress + r'%')
        new_list_starts.append(potential_new_starts[potential_new_starts <= start][-1])
    return np.array(new_list_starts)

def remove_potential_pulse_if_not_from_bottom_logger(list_starts, list_ends,
                                                     darray, phi):
    """
    Filters potential pulses that do not pass the bottom logger test
    
    Parameters
    ----------
    darray       : xarray DataArray 
        Represents temperature data
    phi          : xarray DataArray 
        Represents the temperature stratification index
    list_starts  : 1darray 
        Array of indexes representing the start of the TSI variability detected
    list_ends    : 1darray
        Array of indexes representing the end of the TSI variability detected
    
    Returns
    -------
    new_list_starts : 1darray
    new_list_ends   : 1darray
    
    Returns new list_starts and list_ends list with indexes from potential 
    pulse that are not linked with cooling in the bottom logger removed.
    """
    
    df = pd.DataFrame({'starts':list_starts,
                       'ends':list_ends})
    new_list_starts = []
    new_list_ends = []
    
    for index in df.index:
        progress = index/df.shape[0]*100
        sys.stdout.write('\r'+'Apply heating fiter: %.02f'%progress + r'%')
        start, end = df.iloc[index]
        if is_TSI_variability_from_bottom_logger(darray, phi, start, end):
            new_list_starts.append(start)
            new_list_ends.append(end)
    
    return np.array(new_list_starts), np.array(new_list_ends)

def is_TSI_variability_from_bottom_logger(darray, phi, start, end):
    """
    Bottom logger test
    
    Parameters
    ----------
    darray : xarray DataArray 
        Represents temperature data
    phi    : xarray DataArray 
        Represents the temperature stratification index
    start  : int 
        Represents the start of the TSI variability detected
    end    : int 
        Represents the end of the TSI variability detected
    
    Returns
    -------
    output : bool
        Returns True if the temperature stratification index (phi) variation 
        detected in darray from start to end comes from cooling in the bottom 
        logger. False if not.
    """

    index_bottom_logger = darray.depth.argmax('depth')
    phi_argmin = start + phi[start:end+1].argmin('time')
    temp_difference_till_phi_argmin = darray[:, start] - darray[:, phi_argmin]
    try:
        if temp_difference_till_phi_argmin[index_bottom_logger]:
            if np.abs(temp_difference_till_phi_argmin).argmax('depth') == index_bottom_logger:
                return True
        else:
            return False
    except:
        return False

def shift_ends(list_ends, darray, phi,
               use_positive_phi = True,
               use_decreasing_phi = True,
               use_decreasing_temp = True,
               use_maximum_water_column_temp = True):
    """
    Shifts ends indexes to get the real end of potential pulses
    
    Parameters
    ----------
    list_starts                     : 1darray 
        Array of indexes representing the start of the TSI variability detected
    list_ends                       : 1darray
        Array of indexes representing the end of the TSI variability detected
    darray                          : xarray DataArray 
        Represents temperature data
    phi                             : xarray DataArray 
        Represents the temperature stratification index
    use_positive_phi                : bool
        If true, one of the potential new indexes will be the first index after 
        the last end when the temperature stratification index is positive
    use_decreasing_phi              : bool
        If true, one of the potential new indexes will be the first index after 
        the last end when the temperature stratification index is decreasing
    use_decreasing_temp             : bool
        If true, one of the potential new indexes will be the first index after 
        the last end when the bottom temperature is decreasing
    use_maximum_water_column_temp   : bool
        If true, one of the potential new indexes will be the first index after 
        the last end when the bottom temperature is the maximum temperature in 
        the water column
        
    Returns
    -------
    new_list_ends : 1darray
        List of shifted end indexes with chosen parameters
    """
    
    index_bottom_logger = darray.depth.argmax()
    not_a_pulse = np.isnan(phi)
    if use_positive_phi:
        not_a_pulse = not_a_pulse | \
                     (phi >= 0)
    if use_decreasing_temp:
        not_a_pulse = not_a_pulse | \
                     (darray[index_bottom_logger].diff('time').shift(time = 1) <= 0)
    if use_decreasing_phi:
        not_a_pulse = not_a_pulse | \
                     (phi.diff('time').shift(time=-1).shift(time = 1) <= 0)
    if use_maximum_water_column_temp:
        not_a_pulse = not_a_pulse | \
                     (darray[index_bottom_logger] == darray.max('depth'))
    
    not_a_pulse[-1] = True
    potential_new_ends = np.where(not_a_pulse)[0]
    
    new_list_ends = []
    for end in list_ends:
        progress = end/phi.size*100
        sys.stdout.write('\r' + 'Shifting ends: %.02f'%progress + r'%')
        test = potential_new_ends[potential_new_ends >= end]
        if len(test)>0:
            new_list_ends.append(potential_new_ends[potential_new_ends >= end][0])
        else:
            new_list_ends.append(phi.size-1)
    return np.array(new_list_ends)


# =============================================================================
# =============================================================================
# # Output functions
# =============================================================================
# =============================================================================

def get_output(darray, lon, lat, manual_threshold=None):
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
    list_starts, list_ends = pulses_detection(darray, lon, lat, manual_threshold=manual_threshold)
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
