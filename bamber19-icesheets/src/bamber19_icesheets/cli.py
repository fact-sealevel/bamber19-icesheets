from bamber19_icesheets.bamber19_icesheets_preprocess import (
    bamber19_preprocess_icesheets,
)


import click 

""" 
Args to pass to click:
- pipeline_id, pyear_start, pyear_end, pyear_Step,
scenario, baseyear, climate_data_file, 
slr_proj_mat_fpath, 
scenario_map,

"""

@click.command()
@click.option(
    "--pipeline-id",
    envvar="BAMBER19_ICESHEETS_PREPROCESS_PIPELINE_ID",
    help="Unique identifier for this instance of the module.",
    required=True,
)

@click.option(
    "--pyear-start",
    envvar="BAMBER19_ICESHEETS_PREPROCESS_PYEAR_START",
    help="Projection year start [default=2020]",
    default=2000,
    type=click.IntRange(min=2000),
)
@click.option(
    "--pyear-end",
    envvar="BAMBER19_ICESHEETS_PREPROCESS_PYEAR_END",
    help="Projection year end [default=2100]",
    default=2100,
    type=click.IntRange(max=2300),
)
@click.option(
    "--pyear-step",
    envvar="BAMBER19_ICESHEETS_PREPROCESS_PYEAR_STEP",
    help="Projection year step [default=10]",
    default=10,
    type=click.IntRange(min=1),
)
@click.option(
    "--baseyear",
    envvar="BAMBER19_ICESHEETS_PREPROCESS_BASEYEAR",
    help="Year to which projections are referenced [default = 2000]",
    default=2000,
    type=click.IntRange(2000, 2010),
)
@click.option(
    "--scenario",
    envvar = "BAMBER19_ICESHEETS_PREPROCESS_SCENARIO",
    help="Emissions scenario of interest [default=rcp85]",
    default="rcp85",
)
@click.option(
    "--climate-data-file",
    envvar="BAMBER19_ICESHEETS_PREPROCESS_CLIMATE_DATA_FILE",
    help="NetCDF4/HDF5 file containing surface temperature data",
    default="",
)
@click.option(
    "--slr-proj-mat-fpath",
    help = "Path to the SLR projections matlab file",
    default="/Users/emmamarshall/Desktop/facts_work/facts_v1/facts/modules-data/bamber19_icesheets_preprocess_data/SLRProjections190726core_SEJ_full.mat"
)
@click.option(
    "--scenario-map",
    help="Mapping of scenario names to core files",
    default={
									  	"rcp85": 'corefileH',
										"rcp26": 'corefileL',
										"tlim2.0win0.25": 'corefileL', 
										"tlim5.0win0.25": 'corefileH'}
)

def main(
    pipeline_id,
    pyear_start,
    pyear_end,
    pyear_step,
    baseyear,
    climate_data_file,
    slr_proj_mat_fpath,
    scenario_map,
) -> None:
    """
    TODO: Add. 
    """
    click.echo("Hello from bamber-19 ice sheets!")

    out_dict = bamber19_preprocess_icesheets(
        pipeline_id=pipeline_id,
        pyear_start= pyear_start,
        pyear_end= pyear_end,
        pyear_step= pyear_step,
        baseyear= baseyear,
        scenario = scenario,
        slr_proj_mat_fpath= slr_proj_mat_fpath,
        scenario_map= scenario_map,
        climate_data_file= climate_data_file,
    )
    # TODO: Ad next scripts of bamber19 ice sheets module that use the preprocess results below. 
    