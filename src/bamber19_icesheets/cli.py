
from bamber19_icesheets.bamber19_icesheets_preprocess import (
    bamber19_preprocess_icesheets,
)
from bamber19_icesheets.bamber19_icesheets_project import (
    bamber19_project_icesheets,
    bamber19_project_icesheets_temperaturedriven,
)
from bamber19_icesheets.bamber19_icesheets_postprocess import (
    bamber19_postprocess_icesheets,
)

import click
import os
from pathlib import Path


@click.command()
@click.option(
    "--pipeline-id",
    envvar="BAMBER19_ICESHEETS_PIPELINE_ID",
    help="Unique identifier for this instance of the module. Used to name output files.",
    required=True,
)
@click.option(
    "--pyear-start",
    envvar="BAMBER19_ICESHEETS_PYEAR_START",
    help="Projection year start [default=2020]",
    default=2020,
    type=click.IntRange(min=2020), 
)
@click.option(
    "--pyear-end",
    envvar="BAMBER19_ICESHEETS_PYEAR_END",
    help="Projection year end [default=2100]",
    default=2100,
    type=click.IntRange(max=2300),
)
@click.option(
    "--pyear-step",
    envvar="BAMBER19_ICESHEETS_PYEAR_STEP",
    help="Projection year step [default=10]",
    default=10,
    type=click.IntRange(min=1),
)
@click.option(
    "--baseyear",
    envvar="BAMBER19_ICESHEETS_BASEYEAR",
    help="Year to which projections are referenced [default = 2000]",
    default=2000,
)
@click.option(
    "--scenario",
    envvar = "BAMBER19_ICESHEETS_SCENARIO",
    help="Emissions scenario of interest [default=ssp585]",
    default="ssp585", 
    #NOTE, this is rcp85 in orig. module, updating to ssp585 per discussion in stcaf/tlm-sterodynamics issue #7
)
@click.option(
    "--climate-data-file",
    default="",
    show_default=True,
    help="NetCDF4/HDF5 file containing surface temperature data",
)
@click.option(
    "--slr-proj-mat-file",
    envvar="BAMBER19_ICESHEETS_SLR_PROJ_MAT_FILE",
    default="bamber19_icesheets_preprocess_data/SLRProjections190726core_SEJ_full.mat",
    show_default=True,
    help="Path to the SLR projections matlab file",
)
@click.option(
    "--scenario-map",
    envvar="BAMBER19_ICESHEETS_SCENARIO_MAP",
    help="Mapping of scenario names to core files",
    default={
        "rcp85": "corefileH",
        "rcp26": "corefileL",
        "tlim2.0win0.25": "corefileL",
        "tlim5.0win0.25": "corefileH",
    },
    type=dict
)
@click.option(
    "--nsamps",
    envvar="BAMBER19_ICESHEETS_NSAMPS",
    help="Number of samples to draw [default=500]",
    default=500,
)
@click.option(
    "--replace",
    envvar="BAMBER19_ICESHEETS_REPLACE",
    help="Whether to sample with replacement [default=1]",
    default=1,
    # Add that options can be 0 (false) or 1 (true)
    # type=bool,
)
@click.option(
    "--rngseed",
    envvar="BAMBER19_ICESHEETS_RNGSEED",
    help="Seed for the random number generator [default=1234]",
    default=1234,
)
@click.option(
    "--location-file",
    envvar="BAMBER19_ICESHEETS_LOCATION_FILE",
    help="Path to location file for postprocessing",
    default="location.lst",
)
@click.option(
    "--chunksize",
    type=int,
    envvar="BAMBER19_ICESHEETS_CHUNKSIZE",
    help="Chunk size for postprocessing [default=50]",
    default=50,
)
@click.option(
    "--fingerprint-dir",
    envvar="BAMBER19_ICESHEETS_FINGERPRINT_DIR",
    help="Directory to save postprocessed files to [default='']",
    default="grd_fingerprints_data/FPRINT",
)
@click.option(
    "--output-path",
    help="Directory to save postprocessed files to [default='output/']",
    default="output/",
)
def main(
    pipeline_id,
    pyear_start,
    pyear_end,
    pyear_step,
    baseyear,
    scenario,
    climate_data_file,
    slr_proj_mat_file,
    scenario_map,
    nsamps,
    rngseed,
    location_file,
    chunksize,
    fingerprint_dir,
    replace,
    output_path,
) -> None:
    """
    Application producing sea level projections from ice sheet contributions following the methods of Bamber et al., 2019. Samples of estimated global contribution to sea level are produced for each ice sheet. These are then adjusted by applying spatial fingerprints to produce localized SLR projections for each ice sheet.
    """
    click.echo("Hello from bamber-19 ice sheets!")

    # Run preprocess step
    preprocess_output = bamber19_preprocess_icesheets(
        #pipeline_id=pipeline_id,
        pyear_start=pyear_start,
        pyear_end=pyear_end,
        pyear_step=pyear_step,
        baseyear=baseyear,
        scenario=scenario,
        slr_proj_mat_fpath=slr_proj_mat_file,
        scenario_map=scenario_map,
        climate_data_file=climate_data_file,
    )
    # No fit

    # Run project step
    #if len(climate_data_file) == 0:
    if climate_data_file is None:
        project_output = bamber19_project_icesheets(
            nsamps=nsamps,
            pipeline_id=pipeline_id,
            replace=replace,
            rngseed=rngseed,
            preprocess_output=preprocess_output,
            output_path=output_path,
        )
    else:
        project_output  = (
            bamber19_project_icesheets_temperaturedriven(
                climate_data_file=climate_data_file,
                pipeline_id=pipeline_id,
                replace=replace,
                rngseed=rngseed,
                preprocess_output=preprocess_output,
                output_path=output_path,
            )
        )
    # Run postprocss step
    bamber19_postprocess_icesheets(
        projection_dict=project_output,
        location_fpath=location_file,
        chunksize=chunksize,
        fpdir=fingerprint_dir,
        pipeline_id=pipeline_id,
        output_path=output_path,
    )

if __name__ == "__main__":
    main()