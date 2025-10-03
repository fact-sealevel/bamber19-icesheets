import argparse
import numpy as np
import os
import time
import xarray as xr
import dask.array as da

from bamber19_icesheets.read_locationfile import ReadLocationFile
from bamber19_icesheets.AssignFP import AssignFP

""" bamber19_postprocess_icesheets.py

This script runs the ice sheet post-processing task for the IPCC AR6 Bamber icesheet workflow. This task
uses the global projections from the 'bamber19_project_icesheets' script and applies
spatially resolved fingerprints to the ice sheet contribution. The result is a netCDF4
file that contains spatially and temporally resolved samples of ice sheet contributions
to local sea-level rise

Parameters:
locationfilename = File that contains poinst for localization

Output: NetCDF file containing local contributions from ice sheets

"""


def bamber19_postprocess_icesheets(
    projection_dict: dict,
    location_fpath: str,  # (need to pass full path) was: locationfilename,
    chunksize: int,
    fpdir: str,  # path to dir holding fingerprint .ncs
    output_EAIS_lslr_file: str,
    output_WAIS_lslr_file: str,
    output_GIS_lslr_file: str,
    output_AIS_lslr_file: str,
) -> None:
    """
    Postprocess global ice sheet projections to generate local sea level rise (SLR) at specified locations.

    This function applies spatial fingerprints to global ice sheet projections, producing localized SLR
    projections for each ice sheet. The results are saved as NetCDF files for each ice sheet and the total AIS.

    Parameters
    ----------
    projection_dict : dict
        Dictionary containing global projection arrays for 'eais_samps', 'wais_samps', 'gis_samps',
        'years', 'scenario', and 'baseyear'.
    location_fpath : str
        Path to the file containing location/site information (IDs, latitudes, longitudes).
    chunksize : int
        Chunk size for dask array rechunking (for memory efficiency).
    fpdir : str
        Directory containing fingerprint NetCDF files (e.g., 'fprint_gis.nc', 'fprint_wais.nc', 'fprint_eais.nc').
    output_path : str
        Directory where the output NetCDF files will be saved.

    Returns
    -------
    None
        Writes NetCDF files for each ice sheet component (GIS, WAIS, EAIS, AIS) if path to file for that ice sheet is provided.

    Notes
    -----
    - The function reads location data, applies fingerprints, and generates xarray Datasets for each component.
    - The function assumes the input projection dictionary and fingerprint files are correctly formatted.
    """
    eais_samps = projection_dict["eais_samps"]
    wais_samps = projection_dict["wais_samps"]
    gis_samps = projection_dict["gis_samps"]
    targyears = projection_dict["years"]
    scenario = projection_dict["scenario"]
    baseyear = projection_dict["baseyear"]

    # Read / parse location data
    (_, site_ids, site_lats, site_lons) = ReadLocationFile(location_fpath)

    # Get some dimension data from the loaded data structures
    nsamps = eais_samps.shape[0]

    # commented out from original, these aren't needed?
    # nyears = len(targyears)
    # nsites = len(site_ids)

    gisfp = da.array(
        AssignFP(os.path.join(fpdir, "fprint_gis.nc"), site_lats, site_lons)
    )
    waisfp = da.array(
        AssignFP(os.path.join(fpdir, "fprint_wais.nc"), site_lats, site_lons)
    )
    eaisfp = da.array(
        AssignFP(os.path.join(fpdir, "fprint_eais.nc"), site_lats, site_lons)
    )

    # Rechunk the fingerprints for memory
    gisfp = gisfp.rechunk(chunksize)
    waisfp = waisfp.rechunk(chunksize)
    eaisfp = eaisfp.rechunk(chunksize)

    # Apply the fingerprints to the projections
    gissl = np.multiply.outer(gis_samps, gisfp)
    waissl = np.multiply.outer(wais_samps, waisfp)
    eaissl = np.multiply.outer(eais_samps, eaisfp)

    # Add up the east and west components for AIS total
    aissl = waissl + eaissl

    # Define the missing value for the netCDF files
    nc_missing_value = np.nan  # np.iinfo(np.int16).min

    # Create the xarray data structures for the localized projections
    ncvar_attributes = {
        "description": "Local SLR contributions from icesheets according to Bamber Icesheet workflow",
        "history": "Created " + time.ctime(time.time()),
        "source": "SLR Framework: Bamber icesheet workflow",
        "scenario": scenario,
        "baseyear": baseyear,
    }
    if output_GIS_lslr_file is not None:
        gis_out = xr.Dataset(
            {
                "sea_level_change": (
                    ("samples", "years", "locations"),
                    gissl,
                    {"units": "mm", "missing_value": nc_missing_value},
                ),
                "lat": (("locations"), site_lats),
                "lon": (("locations"), site_lons),
            },
            coords={
                "years": targyears,
                "locations": site_ids,
                "samples": np.arange(nsamps),
            },
            attrs=ncvar_attributes,
        )
        gis_out.to_netcdf(
            output_GIS_lslr_file,
            encoding={
                "sea_level_change": {
                    "dtype": "f4",
                    "zlib": True,
                    "complevel": 4,
                    "_FillValue": nc_missing_value,
                }
            },
        )

    if output_WAIS_lslr_file is not None:
        wais_out = xr.Dataset(
            {
                "sea_level_change": (
                    ("samples", "years", "locations"),
                    waissl,
                    {"units": "mm", "missing_value": nc_missing_value},
                ),
                "lat": (("locations"), site_lats),
                "lon": (("locations"), site_lons),
            },
            coords={
                "years": targyears,
                "locations": site_ids,
                "samples": np.arange(nsamps),
            },
            attrs=ncvar_attributes,
        )
        wais_out.to_netcdf(
            output_WAIS_lslr_file,
            encoding={
                "sea_level_change": {
                    "dtype": "f4",
                    "zlib": True,
                    "complevel": 4,
                    "_FillValue": nc_missing_value,
                }
            },
        )

    if output_EAIS_lslr_file is not None:
        eais_out = xr.Dataset(
            {
                "sea_level_change": (
                    ("samples", "years", "locations"),
                    eaissl,
                    {"units": "mm", "missing_value": nc_missing_value},
                ),
                "lat": (("locations"), site_lats),
                "lon": (("locations"), site_lons),
            },
            coords={
                "years": targyears,
                "locations": site_ids,
                "samples": np.arange(nsamps),
            },
            attrs=ncvar_attributes,
        )
        eais_out.to_netcdf(
            output_EAIS_lslr_file,
            encoding={
                "sea_level_change": {
                    "dtype": "f4",
                    "zlib": True,
                    "complevel": 4,
                    "_FillValue": nc_missing_value,
                }
            },
        )

    if output_AIS_lslr_file is not None:
        ais_out = xr.Dataset(
            {
                "sea_level_change": (
                    ("samples", "years", "locations"),
                    aissl,
                    {"units": "mm", "missing_value": nc_missing_value},
                ),
                "lat": (("locations"), site_lats),
                "lon": (("locations"), site_lons),
            },
            coords={
                "years": targyears,
                "locations": site_ids,
                "samples": np.arange(nsamps),
            },
            attrs=ncvar_attributes,
        )
        ais_out.to_netcdf(
            output_AIS_lslr_file,
            encoding={
                "sea_level_change": {
                    "dtype": "f4",
                    "zlib": True,
                    "complevel": 4,
                    "_FillValue": nc_missing_value,
                }
            },
        )


if __name__ == "__main__":
    # Initialize the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Run the post-processing stage for the IPCC AR6 Bamber Icesheet SLR projection workflow",
        epilog="Note: This is meant to be run as part of the Framework for the Assessment of Changes To Sea-level (FACTS)",
    )

    # Define the command line arguments to be expected
    parser.add_argument(
        "--locationfile",
        help="File that contains name, id, lat, and lon of points for localization",
        default="location.lst",
    )
    parser.add_argument(
        "--chunksize",
        help="Number of locations to process at a time [default=50]",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--pipeline_id", help="Unique identifier for this instance of the module"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Run the postprocessing for the parameters specified from the command line argument
    bamber19_postprocess_icesheets(args.locationfile, args.chunksize, args.pipeline_id)

    # Done
    exit()
