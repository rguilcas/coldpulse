import os
import xarray as xr
from tqdm import tqdm
from haversine import haversine
import pkg_resources


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

def read_godas_grid():
    """
    Reads the NCEP-GODAS file contained in the package to get the grid coordinates.
    
    Returns
    -------
    dataarray : xarray dataarray
        Grid coordinates of NCEP-GODAS as a dataarray
    """
    stream = pkg_resources.resource_stream(__name__, "data/godas_grid_level.nc")
    dataarray = xr.open_dataarray(stream)
    return dataarray

def find_nearest_nonnan_neigbour(longitude, latitude, max_depth):
    """
    Finds the nearest non NaN GODAS neighbour of a given point.

    Parameters
    ----------
    longitude : float
        Longitude of the location studied
    latitude : float
        Latitude of the location studied

    Returns
    -------
    nearest_longitude : float
        Longitude of the nearest non NaN neighbour
    nearest_latitude : float
        Latitude of the nearest non NaN neighbour
    """
    multidepth_grids = read_godas_grid() 
    reference_map = multidepth_grids.sel(level=max_depth, method='bfill')
    stacked_reference_map = reference_map.stack(coordinates = ('lon','lat'))
    no_nan_map = stacked_reference_map.dropna('coordinates')
    squared_distance = (no_nan_map.coordinates.lon-longitude)**2 \
                     + (no_nan_map.coordinates.lat-latitude)**2
    nearest_neighbour = squared_distance.loc[squared_distance==squared_distance.min()]
    nearest_longitude = nearest_neighbour.coordinates.lon.values
    nearest_latitude = nearest_neighbour.coordinates.lat.values
    minimal_distance = haversine((latitude, longitude),
                                 (nearest_latitude, nearest_longitude))
    if minimal_distance > 100:
        print( "!!!CAREFUL!!! The nearest GODAS gridpoint is %.01fkm away, results may not be great.\
            \n Please, check your input longitude and latitude."%minimal_distance)
    else:
        print( "The nearest GODAS gridpoint is %.01fkm away"%minimal_distance)
    return nearest_longitude[0], nearest_latitude[0]

def extract_data_online_godas(lon, lat, max_depth, input_dir):
    """
    Download the required GODAS data to get the 40 year temperature climatology.
    Saves the data as a .nc file following:
        NCEP-GODAS_potential-temperature_[lon]_[lat]_[max-depth].nc

    Parameters
    ----------
    lon : float
        Longitude of the location studied
    lat : float
        Latitude of the location studied

    Returns
    -------
    file_name : string
        Name of the extracted godas climatology data 
    """
    nearest_longitude, nearest_latitude = find_nearest_nonnan_neigbour(lon, lat, max_depth)
    
    file_name = "NCEP-GODAS_potential-temperature_%.01fE_%.01fN_%dm.nc"%(nearest_longitude,
                                                                         nearest_latitude,
                                                                         max_depth)
    if not file_name in os.listdir():
        print("Downloading climatology data, this may take some time...")
        chunks = dict(lon=50,
                      lat=50,
                      time=12,
                      level=5)

        all_monthly_godas_extract = []
        year_climatology = range(1980, 2020)
        for year in tqdm(year_climatology):
             monthly_godas = xr.open_dataset('https://psl.noaa.gov/thredds/fileServer/Datasets/godas/pottmp.%s.nc'%year,
                                            chunks=chunks)
            all_monthly_godas_extract.append(monthly_godas.sel(lon=nearest_longitude,
                                                               lat=nearest_latitude,
                                                               method='nearest').dropna('level'))
        full_godas_extract = xr.concat(all_monthly_godas_extract, dim='time')
        full_godas_extract = full_godas_extract.rename(level='depth')
        full_godas_extract['pottmp'] = full_godas_extract.pottmp - 273.15
        full_godas_extract.pottmp.to_dataset().to_netcdf('%s'%(file_name))
    else:
        print("Data already downloaded")
    return file_name
    
def make_tsi_threshold_from_climatology(darray, input_dir):
    """
    Compute TSI threshold using NCEP-GODAS, 40 year cimatological mean and std

    Parameters
    ----------
    darray : xarray DataArray
        Input temperature data
    lon : float
        Longitude of the location studied
    lat : float
        Latitude of the location studied

    Returns
    -------
    threshold : float
        TSI threshold computed from NCEP-GODAS climatology

    """
    max_depth = darray.depth.max().values
    longitude = darray.longitude.values
    latitude = darray.latitude.values
    godas_data_file_name = extract_data_online_godas(longitude, latitude, max_depth, input_dir)
    godas_ocean_temp = xr.open_dataarray(godas_data_file_name)
    local_temp = godas_ocean_temp.interp(depth=darray.depth)      
    phi = compute_temperature_stratification_index(local_temp)
    threshold = (phi.mean()-phi.std()).values
    return threshold
