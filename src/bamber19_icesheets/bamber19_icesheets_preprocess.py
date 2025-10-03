import argparse
import sys
import numpy as np
import scipy.io

""" bamber19_preprocess_icesheets.py

This runs the preprocessing stage for the Bamber et al. 2019 ice sheet component of the IPCC AR6
workflow.

Parameters:
pipeline_id = Unique identifier for the pipeline running this code

"""


def bamber19_preprocess_icesheets(
    pyear_start,
    pyear_end,
    pyear_step,
    baseyear,
    scenario,
    slr_proj_mat_fpath: str,
    climate_data_file: str,
) -> dict:
    """
    Preprocess Bamber et al. 2019 ice sheet projections for the IPCC AR6 workflow.

    Loads MATLAB .mat data, extracts samples for WAIS, EAIS, and GIS, and returns processed data
    for the specified scenario and climate data file configuration.

    Parameters
    ----------
    pyear_start : int
        Start year for projections.
    pyear_end : int
        End year for projections.
    pyear_step : int
        Step size between projection years.
    baseyear : int
        Reference year for centering projections.
    scenario : str
        Emissions scenario name (e.g., 'rcp85').
    slr_proj_mat_fpath : str
        File path to the MATLAB .mat file containing SLR projections.
    climate_data_file : str
        Path to climate data file. If not None, both high and low scenario samples are extracted.

    Returns
    -------
    dict
        Dictionary containing processed samples and metadata. If `climate_data_file` is provided,
        returns both high and low scenario samples; otherwise, returns samples for the specified scenario.

    Notes
    -----
    - Requires the MATLAB .mat file to have the expected structure and keys.
    """

    # Define the target years for projections
    targyears = np.arange(pyear_start, pyear_end + 1, pyear_step)

    # Load the MATLAB .mat data file
    mat = scipy.io.loadmat(slr_proj_mat_fpath)

    if climate_data_file is not None:
        # If a climate data file is provided, extract both high and low scenario samples
        wais_sampsH, eais_sampsH, gis_sampsH = ExtractSamples(
            mat=mat, this_corefile="corefileH", targyears=targyears, baseyear=baseyear
        )
        wais_sampsL, eais_sampsL, gis_sampsL = ExtractSamples(
            mat=mat, this_corefile="corefileL", targyears=targyears, baseyear=baseyear
        )

        # Combine EAIS and WAIS samples for total AIS
        ais_sampsH = eais_sampsH + wais_sampsH
        ais_sampsL = eais_sampsL + wais_sampsL

        out_data_all = {
            "eais_sampsH": eais_sampsH,
            "wais_sampsH": wais_sampsH,
            "ais_sampsH": ais_sampsH,
            "gis_sampsH": gis_sampsH,
            "eais_sampsL": eais_sampsL,
            "wais_sampsL": wais_sampsL,
            "ais_sampsL": ais_sampsL,
            "gis_sampsL": gis_sampsL,
            "targyears": targyears,
            "baseyear": baseyear,
            "scenario": scenario,
        }
        return out_data_all

    # If no climate data file provided
    else:
        scenario_map = {
            "rcp85": "corefileH",
            "rcp26": "corefileL",
            "tlim2.0win0.25": "corefileL",
            "tlim5.0win0.25": "corefileH",
        }
        this_corefile = scenario_map[scenario]
        wais_samps, eais_samps, gis_samps = ExtractSamples(
            mat=mat, this_corefile=this_corefile, targyears=targyears, baseyear=baseyear
        )
        ais_samps = eais_samps + wais_samps
        out_data_scen = {
            "eais_samps": eais_samps,
            "wais_samps": wais_samps,
            "ais_samps": ais_samps,
            "gis_samps": gis_samps,
            "scenario": scenario,
            "targyears": targyears,
            "baseyear": baseyear,
        }
        return out_data_scen


def ExtractSamples(mat, this_corefile, targyears, baseyear):
    """
    Extract samples for WAIS, EAIS, and GIS from the MATLAB core file for a given scenario.

    Parameters
    ----------
    mat : dict
        Loaded MATLAB .mat data containing projection samples and years.
    this_corefile : str
        Key for the scenario in the .mat file (e.g., 'corefileH', 'corefileL').
    targyears : array-like
        Target years for which projections are required.
    baseyear : int
        Reference year to which projections are centered.

    Returns
    -------
    tuple of np.ndarray
        Tuple containing arrays for (wais_samps, eais_samps, gis_samps), each with shape (n_samples, n_years),
        centered to the baseyear and subset to the target years.

    Notes
    -----
    - The function assumes the .mat file structure matches the expected format for Bamber et al. 2019 projections.
    - The returned arrays are centered by subtracting the value at the baseyear for each sample.

    """
    # Get the years available from the MATLAB core file
    mat_years = np.squeeze(mat[this_corefile][0, 0][27])
    # Determine which MATLAB year indices match our target years
    mat_years_idx = np.isin(mat_years, targyears)
    # Get the samples from the MATLAB core file
    samps = mat[this_corefile][0, 0][21]

    # Extract the samples for each ice sheet (EAIS, WAIS, GIS)
    eais_samps = samps[:, 20, :]
    wais_samps = samps[:, 19, :]
    gis_samps = samps[:, 18, :]
    # Get the values for the baseyear of interest for each sample
    eais_refs = np.apply_along_axis(
        FindRefVals, axis=1, arr=eais_samps, years=mat_years, baseyear=baseyear
    )
    wais_refs = np.apply_along_axis(
        FindRefVals, axis=1, arr=wais_samps, years=mat_years, baseyear=baseyear
    )
    gis_refs = np.apply_along_axis(
        FindRefVals, axis=1, arr=gis_samps, years=mat_years, baseyear=baseyear
    )

    # Center the projections to the reference period (subtract baseyear value)
    eais_samps -= eais_refs[:, np.newaxis]
    wais_samps -= wais_refs[:, np.newaxis]
    gis_samps -= gis_refs[:, np.newaxis]

    # Subset for the target years
    eais_samps = eais_samps[:, mat_years_idx]
    wais_samps = wais_samps[:, mat_years_idx]
    gis_samps = gis_samps[:, mat_years_idx]
    return wais_samps, eais_samps, gis_samps


def FindRefVals(timeseries, years, baseyear):
    # Append a zero to the beginning of the timeseries at year 2000
    timeseries = np.append(np.array([0.0]), timeseries)
    years = np.append(np.array([2000]), years)

    # Interpolate to the appropriate base year
    ref_val = np.interp(baseyear, years, timeseries, left=0.0)

    # Return the value
    return ref_val


if __name__ == "__main__":
    # Initialize the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Run the pre-processing stage for the IPCC AR6 Bamber et al. 2019 ice sheet workflow",
        epilog="Note: This is meant to be run as part of the IPCC AR6 module within the Framework for the Assessment of Changes To Sea-level (FACTS)",
    )

    # Define the command line arguments to be expected
    parser.add_argument(
        "--pipeline_id", help="Unique identifier for this instance of the module"
    )
    parser.add_argument(
        "--pyear_start",
        help="Projection year start [default=2020]",
        default=2020,
        type=int,
    )
    parser.add_argument(
        "--pyear_end", help="Projection year end [default=2100]", default=2100, type=int
    )
    parser.add_argument(
        "--pyear_step", help="Projection year step [default=10]", default=10, type=int
    )
    parser.add_argument(
        "--scenario",
        help="Emissions scenario of interest [default=rcp85]",
        type=str,
        default="rcp85",
    )
    parser.add_argument(
        "--baseyear",
        help="Year to which projections are referenced [default = 2000]",
        default=2000,
        type=int,
    )
    parser.add_argument(
        "--climate_data_file",
        help="NetCDF4/HDF5 file containing surface temperature data",
        type=str,
        default="",
    )

    # Parse the arguments
    args = parser.parse_args()

    if len(args.climate_data_file) == 0:
        bamber19_preprocess_icesheets(
            args.pyear_start,
            args.pyear_end,
            args.pyear_step,
            args.baseyear,
            args.scenario,
            args.pipeline_id,
        )
    else:
        bamber19_preprocess_icesheets(
            args.pyear_start,
            args.pyear_end,
            args.pyear_step,
            args.baseyear,
            args.scenario,
            args.pipeline_id,
            args.climate_data_file,
        )

    # Done
    sys.exit()
