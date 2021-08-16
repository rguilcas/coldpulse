import sys
import numpy as np
import pandas as pd
from .threshold import make_tsi_threshold_from_climatology

def pulses_detection(darray, input_dir):
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

    sys.stdout.write('\r'+'Computing TSI threshold ...')
    sys.stdout.flush()
    tsi_threshold = make_tsi_threshold_from_climatology(darray, input_dir)
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
