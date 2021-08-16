
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
