import argparse
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


def make_projection_ds(
    ice_source, global_samps, years, samples, locations, scenario, baseyear
):
    """
    Create an xarray Dataset for global sea level rise projections from ice sheet samples.

    Parameters
    ----------
    ice_source : str
        Name of the ice sheet source (e.g., 'EAIS', 'WAIS', 'AIS', 'GIS').
    global_samps : array-like
        Array of global sea level change samples, shape (samples, years).
    years : array-like
        Array of projection years.
    samples : array-like
        Array of sample indices.
    locations : array-like
        Array of location indices (typically a single value for global projections).
    scenario : str
        Emissions scenario name.
    baseyear : int
        Reference year for projections.

    Returns
    -------
    xarray.Dataset
        Dataset containing sea level change data and metadata, with dimensions ('samples', 'years', 'locations').

    Notes
    -----
    - The returned dataset includes variables for sea level change, latitude, and longitude, as well as metadata attributes.
    - Latitude and longitude are set to NaN (np.inf) for global projections.
    """
    data = np.asarray(global_samps, dtype=np.float32)[:, :, np.newaxis]

    ds = xr.Dataset(
        data_vars={
            # data variable
            "sea_level_change": (
                ("samples", "years", "locations"),
                data,
                {"units": "mm"},
            ),
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
            "years": (("years",), years),
            "samples": (("samples",), samples),
            "locations": (("locations",), locations),
        },
        attrs={
            "description": f"Global SLR contribution from {ice_source} from the Bamber et al. 2019 IPCC AR6 workflow",
            "history": "Created " + time.ctime(time.time()),
            "scenario": scenario,
            "baseyear": baseyear,
        },
    )
    return ds


def bamber19_project_icesheets(
    nsamps,
    replace, 
    rngseed, 
    preprocess_output, 
    output_AIS_glslr_file,
    output_GIS_glslr_file,
    output_WAIS_glslr_file,
    output_EAIS_glslr_file,
):
    """
    Generate and save global sea level rise projections for ice sheets (if no climate data file is passed).

    This function samples from preprocessed ice sheet projections, creates xarray Datasets for each
    ice sheet component, and writes the results to NetCDF file if path is provided. It is used when a climate data file
    is not provided.

    Parameters
    ----------
    nsamps : int
        Number of samples to generate.
    replace : bool
        Whether to sample with replacement.
    rngseed : int
        Seed for the random number generator.
    preprocess_output : dict
        Dictionary containing preprocessed output, including arrays for 'ais_samps', 'eais_samps',
        'wais_samps', 'gis_samps', 'targyears', 'scenario', and 'baseyear'.
    output_path : str
        Directory path where NetCDF output files will be saved.

    Returns
    -------
    dict
        Dictionary containing sampled arrays for each ice sheet component, years, scenario, and baseyear.

    Notes
    -----
    - NetCDF files for each ice sheet component (AIS, EAIS, WAIS, GIS) are written to if file path for that ice sheet is provided.
    - The function assumes the preprocessed output dictionary contains the required keys and arrays.
    """
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
    # not sure if intended or not
    icesheets_output = {
        "eais_samps": eais_samps,
        "wais_samps": wais_samps,
        "ais_samps": ais_samps,
        "gis_samps": gis_samps,
        "years": years,
        "scenario": 'temperature-driven', # leaving as is (not using scenario obj for now)
        "baseyear": baseyear,
    }

    # Adding this to mimic what happens in temperature-driven situation.
    # This is writing the global slr projections (w/o fingerprints) generated
    # When no climate data file is provided.
    years = np.asarray(years, dtype=np.int32)
    samples = np.arange(nsamps, dtype=np.int64)
    locations = np.array([-1], dtype=np.int64)  # single “location”, value -1

    if output_EAIS_glslr_file is not None:
        ds_eais = make_projection_ds(
            ice_source="EAIS",
            global_samps=eais_samps,
            years=years,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_eais.to_netcdf(output_EAIS_glslr_file)

    if output_WAIS_glslr_file is not None:
        ds_wais = make_projection_ds(
            ice_source="WAIS",
            global_samps=wais_samps,
            years=years,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_wais.to_netcdf(output_WAIS_glslr_file)

    if output_AIS_glslr_file is not None:
        ds_ais = make_projection_ds(
            ice_source="AIS",
            global_samps=ais_samps,
            years=years,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_ais.to_netcdf(output_AIS_glslr_file)

    if output_GIS_glslr_file is not None:
        ds_gis = make_projection_ds(
            ice_source="GIS",
            global_samps=gis_samps,
            years=years,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_gis.to_netcdf(output_GIS_glslr_file)

    return icesheets_output


def bamber19_project_icesheets_temperaturedriven(
    climate_data_file,
    replace,
    rngseed,
    preprocess_output: dict,
    output_EAIS_gslr_file,
    output_WAIS_gslr_file,
    output_GIS_gslr_file,
    output_AIS_gslr_file
):
    """
    Generate and save global sea level rise projections for ice sheets (temperature-driven).

    This function samples from preprocessed high and low scenario ice sheet projections, determines
    which samples to draw from each scenario based on climate data, creates xarray Datasets for each
    ice sheet component, and writes the results to NetCDF files if path provided. It is used when a climate data file
    is provided.

    Parameters
    ----------
    climate_data_file : str
        Path to the climate data file (HDF5/NetCDF) containing surface temperature data.
    replace : bool
        Whether to sample with replacement.
    rngseed : int
        Seed for the random number generator.
    preprocess_output : dict
        Dictionary containing preprocessed output, including arrays for 'ais_sampsH', 'eais_sampsH',
        'wais_sampsH', 'gis_sampsH', 'ais_sampsL', 'eais_sampsL', 'wais_sampsL', 'gis_sampsL',
        'targyears', 'scenario', and 'baseyear'.
    output_path : str
        Directory path where NetCDF output files will be saved.

    Returns
    -------
    dict
        Dictionary containing sampled arrays for each ice sheet component, years, scenario, and baseyear.

    Notes
    -----
    - NetCDF files for each ice sheet component (AIS, EAIS, WAIS, GIS) are written if file path for that ice sheet is provided.
    - The function determines which samples to draw from high or low scenario using the provided climate data.
    - The function assumes the preprocessed output dictionary contains the required keys and arrays.
    """

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
    icesheets_output = {
        "eais_samps": eais_samps,
        "wais_samps": wais_samps,
        "ais_samps": ais_samps,
        "gis_samps": gis_samps,
        "years": years,
        "scenario": scenario,  # this was hard-coded to 'temperature-driven', not sure why?
        "baseyear": baseyear,
    }

    # Also want to create xr.Datasets to replace the projections written to .ncs.
    years = np.asarray(years, dtype=np.int32)
    samples = np.arange(nsamps, dtype=np.int64)
    locations = np.array([-1], dtype=np.int64)  # single “location”, value -1

    # data: (samples, years, locations)
    if output_EAIS_gslr_file is not None:
         
        ds_eais = make_projection_ds(
            "EAIS", eais_samps, years, samples, locations, scenario, baseyear
        )
        ds_eais.to_netcdf(output_EAIS_gslr_file)

    if output_WAIS_gslr_file is not None:
         
        ds_wais = make_projection_ds(
            "WAIS", wais_samps, years, samples, locations, scenario, baseyear
        )
        ds_wais.to_netcdf(output_WAIS_gslr_file)

    if output_AIS_gslr_file is not None:
         
        ds_ais = make_projection_ds(
            "AIS", ais_samps, years, samples, locations, scenario, baseyear
        )
        ds_ais.to_netcdf(output_AIS_gslr_file)

    if output_GIS_gslr_file is not None:
         
        ds_gis = make_projection_ds(
            "GIS", gis_samps, years, samples, locations, scenario, baseyear
        )
        ds_gis.to_netcdf(output_GIS_gslr_file)

    return icesheets_output  


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
    # Needed to make one change here - orig. tried to get years from df_ssp obj.
    # like this: sat_years = df_ssp['year'][()], didn't work. related to which fair file it expected?
    sat_years = ssp_folder["years"][()]
    
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

if __name__ == '__main__':

	# Initialize the command-line argument parser
	parser = argparse.ArgumentParser(description="Run the IPCC AR6 Bamber et al. 2019 ice sheet projection stage.",\
	epilog="Note: This is meant to be run as part of the ipccar6 module set within the Framework for the Assessment of Changes To Sea-level (FACTS)")

	# Define the command line arguments to be expected
	parser.add_argument('--nsamps', help="Number of samples to draw (default = 10)", default=10, type=int)
	parser.add_argument('--replace', help="Allow sampling with replacement (default = 1)", choices=(0,1), type=int, default=1)
	parser.add_argument('--seed', help="Seed for the random number generator (default = 1234)", default=1234, type=int)
	parser.add_argument('--pipeline_id', help="Unique identifier for this instance of the module")
	parser.add_argument('--climate_data_file', help="NetCDF4/HDF5 file containing surface temperature data", type=str, default="")


	# Parse the arguments
	args = parser.parse_args()

	if len(args.climate_data_file) == 0:
		# Run the preprocessing stage with the user defined RCP scenario
		bamber19_project_icesheets(args.nsamps, args.pipeline_id, args.replace, args.seed)
	else:
		bamber19_project_icesheets_temperaturedriven(args.climate_data_file,args.pipeline_id, args.replace, args.seed)

	exit()