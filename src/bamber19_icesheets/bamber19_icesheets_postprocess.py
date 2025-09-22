import argparse
import numpy as np
import os
import time
import xarray as xr
import dask.array as da

from bamber19_icesheets.read_locationfile import ReadLocationFile
from bamber19_icesheets.AssignFP import AssignFP

''' bamber19_postprocess_icesheets.py

This script runs the ice sheet post-processing task for the IPCC AR6 Bamber icesheet workflow. This task
uses the global projections from the 'bamber19_project_icesheets' script and applies
spatially resolved fingerprints to the ice sheet contribution. The result is a netCDF4
file that contains spatially and temporally resolved samples of ice sheet contributions
to local sea-level rise

Parameters:
locationfilename = File that contains poinst for localization
pipeline_id = Unique identifer for the pipeline running this code

Output: NetCDF file containing local contributions from ice sheets

'''

def bamber19_postprocess_icesheets(
    projection_dict: dict,
    location_fpath: str,  # (need to pass full path) was: locationfilename,
    chunksize: int,
    fpdir: str,  # path to dir holding fingerprint .ncs
    pipeline_id: str,
    output_path: str,
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
    pipeline_id : str
        Unique identifier for the pipeline run.
    output_path : str
        Directory where the output NetCDF files will be saved.

    Returns
    -------
    None
        Writes NetCDF files for each ice sheet component (GIS, WAIS, EAIS, AIS) to `output_path`.

    Notes
    -----
    - The function reads location data, applies fingerprints, and generates xarray Datasets for each component.
    - Output files are named as '{pipeline_id}_{component}_localsl.nc'.
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

    #commented out from original, these aren't needed?
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

    # Write the netcdf output files
    gis_nc_outpath = os.path.join(
        output_path, "{0}_{1}_localsl.nc".format(pipeline_id, "GIS")
    )
    print("Writing GIS local SLR to: ", gis_nc_outpath)
    gis_out.to_netcdf(
        gis_nc_outpath,
        encoding={
            "sea_level_change": {
                "dtype": "f4",
                "zlib": True,
                "complevel": 4,
                "_FillValue": nc_missing_value,
            }
        },
    )

    wais_nc_path = os.path.join(
        output_path, "{0}_{1}_localsl.nc".format(pipeline_id, "WAIS")
    )
    print("Writing WAIS local SLR to: ", wais_nc_path)
    wais_out.to_netcdf(
        wais_nc_path,
        encoding={
            "sea_level_change": {
                "dtype": "f4",
                "zlib": True,
                "complevel": 4,
                "_FillValue": nc_missing_value,
            }
        },
    )
    eais_nc_path = os.path.join(
        output_path, "{0}_{1}_localsl.nc".format(pipeline_id, "EAIS")
    )
    print("Writing EAIS local SLR to: ", eais_nc_path)
    eais_out.to_netcdf(
        eais_nc_path,
        encoding={
            "sea_level_change": {
                "dtype": "f4",
                "zlib": True,
                "complevel": 4,
                "_FillValue": nc_missing_value,
            }
        },
    )
    ais_nc_path = os.path.join(
        output_path, "{0}_{1}_localsl.nc".format(pipeline_id, "AIS")
    )
    print("Writing AIS local SLR to: ", ais_nc_path)
    ais_out.to_netcdf(
        ais_nc_path,
        encoding={
            "sea_level_change": {
                "dtype": "f4",
                "zlib": True,
                "complevel": 4,
                "_FillValue": nc_missing_value,
            }
        },
    )

    # wais_out.to_netcdf("{0}_{1}_localsl.nc".format(pipeline_id, "WAIS"), encoding={"sea_level_change": {"dtype": "f4", "zlib": True, "complevel":4, "_FillValue": nc_missing_value}})
    # eais_out.to_netcdf("{0}_{1}_localsl.nc".format(pipeline_id, "EAIS"), encoding={"sea_level_change": {"dtype": "f4", "zlib": True, "complevel":4, "_FillValue": nc_missing_value}})
    # ais_out.to_netcdf("{0}_{1}_localsl.nc".format(pipeline_id, "AIS"), encoding={"sea_level_change": {"dtype": "f4", "zlib": True, "complevel":4, "_FillValue": nc_missing_value}})

if __name__ == '__main__':

	# Initialize the command-line argument parser
	parser = argparse.ArgumentParser(description="Run the post-processing stage for the IPCC AR6 Bamber Icesheet SLR projection workflow",\
	epilog="Note: This is meant to be run as part of the Framework for the Assessment of Changes To Sea-level (FACTS)")

	# Define the command line arguments to be expected
	parser.add_argument('--locationfile', help="File that contains name, id, lat, and lon of points for localization", default="location.lst")
	parser.add_argument('--chunksize', help="Number of locations to process at a time [default=50]", type=int, default=50)
	parser.add_argument('--pipeline_id', help="Unique identifier for this instance of the module")

	# Parse the arguments
	args = parser.parse_args()

	# Run the postprocessing for the parameters specified from the command line argument
	bamber19_postprocess_icesheets(args.locationfile, args.chunksize, args.pipeline_id)

	# Done
	exit()