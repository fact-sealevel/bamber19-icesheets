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


@click.command()
@click.option(
    "--pipeline-id",
    #envvar="BAMBER19_ICESHEETS_PREPROCESS_PIPELINE_ID",
    help="Unique identifier for this instance of the module.",
    required=True,
)
@click.option(
    "--pyear-start",
    #envvar="BAMBER19_ICESHEETS_PREPROCESS_PYEAR_START",
    help="Projection year start [default=2020]",
    default=2020,
    type=click.IntRange(min=2000),
)
@click.option(
    "--pyear-end",
    #envvar="BAMBER19_ICESHEETS_PREPROCESS_PYEAR_END",
    help="Projection year end [default=2100]",
    default=2100,
    type=click.IntRange(max=2300),
)
@click.option(
    "--pyear-step",
    #envvar="BAMBER19_ICESHEETS_PREPROCESS_PYEAR_STEP",
    help="Projection year step [default=10]",
    default=10,
    type=click.IntRange(min=1),
)
@click.option(
    "--baseyear",
    # envvar="BAMBER19_ICESHEETS_PREPROCESS_BASEYEAR",
    help="Year to which projections are referenced [default = 2000]",
    default=2000,
    type=click.IntRange(2000, 2010),
)
@click.option(
    "--scenario",
    # envvar = "BAMBER19_ICESHEETS_PREPROCESS_SCENARIO",
    help="Emissions scenario of interest [default=rcp85]",
    default="rcp85",
)
@click.option(
    "--climate-data-file",
    # envvar="BAMBER19_ICESHEETS_PREPROCESS_CLIMATE_DATA_FILE",
    help="NetCDF4/HDF5 file containing surface temperature data",
    default="",
)
@click.option(
    "--slr-proj-mat-fpath",
    help="Path to the SLR projections matlab file",
    default="/Users/emmamarshall/Desktop/facts_work/facts_v1/facts/modules-data/bamber19_icesheets_preprocess_data/SLRProjections190726core_SEJ_full.mat",
)
@click.option(
    "--scenario-map",
    help="Mapping of scenario names to core files",
    default={
        "rcp85": "corefileH",
        "rcp26": "corefileL",
        "tlim2.0win0.25": "corefileL",
        "tlim5.0win0.25": "corefileH",
    },
)
@click.option(
    "--nsamps",
    help="Number of samples to draw [default=20000]",
    default=20000,
)
@click.option(
    "--replace",
    #envvar="BAMBER19_ICESHEETS_PROJECT_REPLACE",
    help="Whether to sample with replacement [default=1]",
    default=1,
    # Add that options can be 0 (false) or 1 (true)
    # type=bool,
)
@click.option(
    "--rngseed",
    help="Seed for the random number generator [default=1234]",
    default=1234,
)
@click.option(
    "--location-fpath",
    help="Path to location file for postprocessing",
    default="/Users/emmamarshall/Desktop/facts_work/facts_v2/initial_facts_modules_work/data/input/location.lst",
)
@click.option(
    "--chunksize",
    help="Chunk size for postprocessing [default=50]",
    default=50,
)
@click.option(
    "--fpdir",
    help="Directory to save postprocessed files to [default='']",
    default="/Users/emmamarshall/Desktop/facts_work/facts_v1/facts/modules-data/grd_fingerprints_data/FPRINT",
)
@click.option(
    "--output-path",
    help="Directory to save postprocessed files to [default='']",
    default="data/output/",
)
def main(
    pipeline_id,
    pyear_start,
    pyear_end,
    pyear_step,
    baseyear,
    scenario,
    climate_data_file,
    slr_proj_mat_fpath,
    scenario_map,
    nsamps,
    rngseed,
    location_fpath,
    chunksize,
    fpdir,
    replace,
    output_path,
) -> None:
    """
    TODO: Add.
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
        slr_proj_mat_fpath=slr_proj_mat_fpath,
        scenario_map=scenario_map,
        climate_data_file=climate_data_file,
    )
    # No fit

    # Run project step
    print("Len climate data file: ", len(climate_data_file))
    if len(climate_data_file) == 0:
        print("About to call bamber19_project_icesheets()")
        project_output = bamber19_project_icesheets(
            nsamps=nsamps,
            pipeline_id=pipeline_id,
            replace=replace,
            rngseed=rngseed,
            preprocess_output=preprocess_output,
        )
    else:
        project_output, projections_ds_dict = (
            bamber19_project_icesheets_temperaturedriven(
                climate_data_file=climate_data_file,
                pipeline_id=pipeline_id,
                replace=replace,
                rngseed=rngseed,
                preprocess_output=preprocess_output,
            )
        )
    # Run postprocss step
    bamber19_postprocess_icesheets(
        projection_dict=project_output,
        location_fpath=location_fpath,
        chunksize=chunksize,
        fpdir=fpdir,
        pipeline_id=pipeline_id,
        output_path=output_path,
    )
