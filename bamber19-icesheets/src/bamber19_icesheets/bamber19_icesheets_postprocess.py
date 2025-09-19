import numpy as np
import os
import time
from bamber19_icesheets.read_locationfile import ReadLocationFile
from bamber19_icesheets.AssignFP import AssignFP

import xarray as xr
import dask.array as da


def bamber19_postprocess_icesheets(
    projection_dict: dict,
    location_fpath: str,  # (need to pass full path) was: locationfilename,
    chunksize: int,
    fpdir: str,  # path to dir holding fingerprint .ncs
    pipeline_id: str,
    output_path: str,
) -> None:
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
    # TODO check if we want to write or return these.
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
