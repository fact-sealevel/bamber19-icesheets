import numpy as np
import time
import h5py
import xarray as xr
import os

""" bamber19_project_icesheets.py

This is the projection stage for the Bamber et al. 2019 ice sheet component of the IPCC AR6 module set.

Parameters:
nsamps              Number of samples to produce
replace             Allow sampling with replacement
rngseed             Seed for the random number generator
pipeline_id         Unique identifier to attach to this pipeline
climate_data_file   FAIR-outputted climate data file


Output:
"{pipeline_id}_(AIS|EAIS|WAIS|GIS)_globalsl.nc" = Sampled global projections in netCDF file

"""


def bamber19_project_icesheets(
    nsamps, pipeline_id, replace, rngseed, 
    preprocess_output
):
    """This is called if a climate data file is NOT provided."""

    years = preprocess_output["targyears"]
    scenario = preprocess_output["scenario"]
    baseyear = preprocess_output["baseyear"]
    ais_samples = preprocess_output["ais_samps"]
    eais_samples = preprocess_output["eais_samps"]
    wais_samples = preprocess_output["wais_samps"]
    gis_samples = preprocess_output["gis_samps"]

    # Generate the sample indices
    rng = np.random.default_rng(rngseed)
    sample_inds = rng.choice(ais_samples.shape[0], size=nsamps, replace=replace)

    # Store the samples for AIS components
    eais_samps = eais_samples[sample_inds, :]
    wais_samps = wais_samples[sample_inds, :]
    ais_samps = ais_samples[sample_inds, :]
    gis_samps = gis_samples[sample_inds, :]

    ## In original bamber19_project_icesheets(), WriteOutput() is called and 'scenario' is passed.
    ## However, in WriteOutput(), 'scenario' isn't used, its hardcoded  as 'temperature-driven'.
    icesheets_output = {
        "eais_samps": eais_samps,
        "wais_samps": wais_samps,
        "ais_samps": ais_samps,
        "gis_samps": gis_samps,
        "years": years,
        "scenario": scenario,  # 'temperature-driven', BUG? See above comment.
        "baseyear": baseyear,
    }
    return icesheets_output


def bamber19_project_icesheets_temperaturedriven(
    climate_data_file, pipeline_id, replace, rngseed, 
    preprocess_output: dict, output_path:str
):
    """This is called if a climate data file is provided."""

    years = preprocess_output["targyears"]
    scenario = preprocess_output["scenario"]
    baseyear = preprocess_output["baseyear"]
    ais_samplesH = preprocess_output["ais_sampsH"]
    eais_samplesH = preprocess_output["eais_sampsH"]
    wais_samplesH = preprocess_output["wais_sampsH"]
    gis_samplesH = preprocess_output["gis_sampsH"]
    ais_samplesL = preprocess_output["ais_sampsL"]
    eais_samplesL = preprocess_output["eais_sampsL"]
    wais_samplesL = preprocess_output["wais_sampsL"]
    gis_samplesL = preprocess_output["gis_sampsL"]

    rng = np.random.default_rng(rngseed)

    # Identify which samples to draw from (high v. low) according to scenario arg.
    useHigh = pickScenario(
        climate_data_file=climate_data_file, scenario=scenario, rng=rng
    )

    nsamps = useHigh.size
    # Generate the sample indices
    sample_inds = rng.choice(ais_samplesL.shape[0], size=nsamps, replace=replace)
    # Store the samples for AIS components
    eais_samps = eais_samplesL[sample_inds, :]
    wais_samps = wais_samplesL[sample_inds, :]
    ais_samps = ais_samplesL[sample_inds, :]
    gis_samps = gis_samplesL[sample_inds, :]

    eais_samps[useHigh, :] = eais_samplesH[sample_inds[useHigh], :]
    wais_samps[useHigh, :] = wais_samplesH[sample_inds[useHigh], :]
    ais_samps[useHigh, :] = ais_samplesH[sample_inds[useHigh], :]
    gis_samps[useHigh, :] = gis_samplesH[sample_inds[useHigh], :]

    # This should be equivalent to what's in {}_projections.pkl
    projections_output = {
        "eais_samps": eais_samps,
        "wais_samps": wais_samps,
        "ais_samps": ais_samps,
        "gis_samps": gis_samps,
        "years": years,
        "scenario": scenario,  # 'temperature-driven', BUG? See above comment.
        "baseyear": baseyear,
    }

    # Also want to create xr.Datasets to replace the projections written to .ncs.
    years = np.asarray(years, dtype=np.int32)
    samples = np.arange(nsamps, dtype=np.int64)
    locations = np.array([-1], dtype=np.int64)  # single “location”, value -1

    # data: (samples, years, locations)
    def make_projection_ds(ice_source, global_samps):
        data = np.asarray(global_samps, dtype=np.float32)[:, :, np.newaxis]

        ds = xr.Dataset(
            data_vars={
                # data variable
                "sea_level_change": (
                    ("samples", "years", "locations"),
                    data,
                    {"units": "mm"},
                ),
                # plain variables over 'locations' (not coords, to match your layout)
                "lat": (
                    ("locations",),
                    np.array([np.float32(np.inf)], dtype=np.float32),
                ),
                "lon": (
                    ("locations",),
                    np.array([np.float32(np.inf)], dtype=np.float32),
                ),
            },
            coords={
                # coordinate variables with same names as dims
                "years": (("years",), years),
                "samples": (("samples",), samples),
                "locations": (("locations",), locations),
            },
            attrs={
                "description": f"Global SLR contribution from {ice_source} from the Bamber et al. 2019 IPCC AR6 workflow",
                "history": "Created " + time.ctime(time.time()),
                "source": f"FACTS: {pipeline_id}",
                "scenario": scenario,
                "baseyear": baseyear,
            },
        )
        return ds

    ds_eais = make_projection_ds("EAIS", eais_samps)
    ds_wais = make_projection_ds("WAIS", wais_samps)
    ds_ais = make_projection_ds("AIS", ais_samps)
    ds_gis = make_projection_ds("GIS", gis_samps)

    gis_nc_global_outpath = os.path.join(
        output_path, "{0}_{1}_globalsl.nc".format(pipeline_id, "GIS")
        )
    print('Writing GIS global SLR to: ', gis_nc_global_outpath) 
    ds_gis.to_netcdf(gis_nc_global_outpath)

    wais_nc_global_outpath = os.path.join(
        output_path, "{0}_{1}_globalsl.nc".format(pipeline_id, "WAIS")
        )
    print('Writing WAIS global SLR to: ', wais_nc_global_outpath)
    ds_wais.to_netcdf(wais_nc_global_outpath)
    
    eais_nc_global_outpath = os.path.join(
        output_path, "{0}_{1}_globalsl.nc".format(pipeline_id, "EAIS")
        )
    print('Writing EAIS global SLR to: ', eais_nc_global_outpath)
    ds_eais.to_netcdf(eais_nc_global_outpath)
    
    ais_nc_global_outpath = os.path.join(
        output_path, "{0}_{1}_globalsl.nc".format(pipeline_id, "AIS")
        )
    print('Writing AIS global SLR to: ', ais_nc_global_outpath)
    ds_ais.to_netcdf(ais_nc_global_outpath)


    #projection_ds_dict = {
    #    "EAIS": ds_eais,
    #    "WAIS": ds_wais,
    #    "AIS": ds_ais,
    #    "GIS": ds_gis,
    #}
    return projections_output#, projection_ds_dict


def GetSATData(
    climate_data_file,  # NOTE was fname
    scenario,
    refyear_start=1850,
    refyear_end=1900,
    year_start=1900,
    year_end=2300,
):
    """ "
    This function takes a filename (climate_data_file) and other args. Reads an hdf5 file that has surface_temperature for different scenarios.
    - Looks at number of ensemble members for that scenario,
    - Extracts the years available in the data,
    - Trims to range of years requested in inputs,
    - Normalize, crop temp series,
    - Return normalized SAT (Surface air temp) & time arrays and number of ensemble members.
    """

    # Open the climate data file
    print("target module reached")

    df_ssp = h5py.File(climate_data_file, "r")

    # Extract surface temperature for specified scenario
    if scenario not in df_ssp.keys():
        raise ValueError(
            "Scenario {} not found in climate data file {}".format(
                scenario, climate_data_file
            )
        )
    ssp_folder = df_ssp.get(scenario)
    sat_ssp = ssp_folder.get("surface_temperature")

    # Get number of ensemble members from the data
    _, nens = sat_ssp.shape

    # Extract the years available 
    sat_years = ssp_folder["years"][()]
    print('sat years shape: ', sat_years.shape)
    #This should also work? 
    #sat_years = df_ssp['sat_ssp']['years'][:]
    #ds = xr.open_dataset(climate_data_file, group=scenario)
    #sat_years = ds["years"].values
    #print('sat years shape: ', sat_years.shape)
    # Which indices align with the reference and trim years
    refyear_start_idx = np.flatnonzero(sat_years == refyear_start)[0]
    refyear_end_idx = np.flatnonzero(sat_years == refyear_end)[0]  # + 1
    year_start_idx = np.flatnonzero(sat_years == year_start)[0]
    year_end_idx = np.flatnonzero(sat_years == year_end)[0] + 1

    # Normalize and crop temperature series
    Time = np.arange(year_start, year_end + 1)
    SATave = np.mean(sat_ssp[refyear_start_idx:refyear_end_idx, :], axis=0)
    SAT = sat_ssp[year_start_idx:year_end_idx, :] - SATave
    # Close the h5 file
    df_ssp.close()

    return (SAT, Time, nens)


def pickScenario(climate_data_file, scenario, rng):
    """This function picks which samples to draw from (high v. low).
    It calls GetSATData() which returns a normalized SAT and time array and number of ensemble members.
    It then finds integrated SAT over 2000-2099, converts integrated temp into a normalized variable between low and high scenarios.
    It then returns a boolean array 'useHigh' which indicates which samples to draw from high scenario.

    """

    SAT, Time, NumTensemble = GetSATData(climate_data_file, scenario)

    # find integrated SAT over 2000-2099
    x2 = np.where((Time[:] < 2100) * (Time[:] >= 2000))
    SAT2 = SAT[x2]
    iSAT = SAT2.sum(axis=0)

    # convert integrated temperature into a normalized variable between low and high scenarios

    # Bamber 19 low scenario: 0.7 C in 2000, 1.5 C in 2050,
    # 2.0 C in 2100 = 70 + 20 + 40 + 12.5 = 142.5 C*yr if I've done this correctly

    # Bamber 19 high scenario: 0.7 C in 2000, 2.0 C in 2050, 5.0 C in 2100 =
    # 70 + 32.5 + 65 + 75 = 242.5 C*yr if I've done this correctly

    iSAT_marker = np.array([142.5, 242.5])

    f2 = np.minimum(
        1, np.maximum(0, (iSAT - iSAT_marker[0]) / (iSAT_marker[1] - iSAT_marker[0]))
    )
    weights = f2

    selector = rng.random(iSAT.size)
    useHigh = selector < weights
    return useHigh
