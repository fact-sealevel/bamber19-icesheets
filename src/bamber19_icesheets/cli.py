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
    envvar="BAMBER19_ICESHEETS_PIPELINE_ID",
    help="Unique identifier for this instance of the module.",
    required=False,
    type=str,
)
@click.option(
    "--pyear-start",
    envvar="BAMBER19_ICESHEETS_PYEAR_START",
    help="Projection year start",
    default=2020,
    type=click.IntRange(min=2020),
    show_default=True,
)
@click.option(
    "--pyear-end",
    envvar="BAMBER19_ICESHEETS_PYEAR_END",
    help="Projection year end",
    default=2100,
    type=click.IntRange(max=2300),
    show_default=True,
)
@click.option(
    "--pyear-step",
    envvar="BAMBER19_ICESHEETS_PYEAR_STEP",
    help="Projection year step",
    default=10,
    show_default=True,
    type=click.IntRange(min=1),
)
@click.option(
    "--baseyear",
    envvar="BAMBER19_ICESHEETS_BASEYEAR",
    help="Year to which projections are referenced",
    default=2000,
    show_default=True,
    type=int,
)
@click.option(
    "--scenario",
    envvar="BAMBER19_ICESHEETS_SCENARIO",
    help="Emissions scenario of interest",
    default="rcp85",
    type=click.Choice(
        ["rcp26", "rcp45", "rcp85", "ssp119", "ssp126", "ssp245", "ssp370", "ssp585"],
        case_sensitive=False,
    ),
    show_default=True,
)
@click.option(
    "--climate-data-file",
    default=None,
    envvar="BAMBER19_ICESHEETS_CLIMATE_DATA_FILE",
    help="NetCDF4/HDF5 file containing surface temperature data",
)
@click.option(
    "--slr-proj-mat-file",
    envvar="BAMBER19_ICESHEETS_SLR_PROJ_MAT_FILE",
    help="Path to the SLR projections matlab file",
    required=True,
)
@click.option(
    "--nsamps",
    envvar="BAMBER19_ICESHEETS_NSAMPS",
    help="Number of samples to draw",
    default=500,
    show_default=True,
    type=int,
)
@click.option(
    "--replace",
    envvar="BAMBER19_ICESHEETS_REPLACE",
    help="Whether to sample with replacement",
    default=1,
    type=click.IntRange(min=0, max=1),
    show_default=True,
)
@click.option(
    "--rngseed",
    envvar="BAMBER19_ICESHEETS_RNGSEED",
    help="Seed for the random number generator",
    default=1234,
    type=int,
    show_default=True,
)
@click.option(
    "--location-file",
    envvar="BAMBER19_ICESHEETS_LOCATION_FILE",
    help="Path to file that contains name, id, lat, and lon of points for localization",
    required=True,
    type=str,
)
@click.option(
    "--chunksize",
    envvar="BAMBER19_ICESHEETS_CHUNKSIZE",
    help="Number of locations to process at a time",
    default=50,
    show_default=True,
    type=int,
)
@click.option(
    "--fingerprint-dir",
    envvar="BAMBER19_ICESHEETS_FINGERPRINT_DIR",
    help="Path to directory containing fingerprint files",
    required=True,
)
@click.option(
    "--output-EAIS-lslr-file",
    envvar="BAMBER19_ICESHEETS_OUTPUT_EAIS_LSLR_FILE",
    help="Path to write EAIS contribution to local SLR output file. If not provided, file will not be written.",
    type=str,
    required=False,
)
@click.option(
    "--output-WAIS-lslr-file",
    envvar="BAMBER19_ICESHEETS_OUTPUT_WAIS_LSLR_FILE",
    help="Path to write WAIS contribution to local SLR output file. If not provided, file will not be written.",
    type=str,
    required=False,
)
@click.option(
    "--output-GIS-lslr-file",
    envvar="BAMBER19_ICESHEETS_OUTPUT_GIS_LSLR_FILE",
    help="Path to write GIS contribution to local SLR output file. If not provided, file will not be written.",
    type=str,
    required=False,
)
@click.option(
    "--output-AIS-lslr-file",
    envvar="BAMBER19_ICESHEETS_OUTPUT_AIS_LSLR_FILE",
    help="Path to write AIS contribution to local SLR output file. If not provided, file will not be written.",
    type=str,
    required=False,
)
@click.option(
    "--output-EAIS-gslr-file",
    envvar="BAMBER19_ICESHEETS_OUTPUT_EAIS_GSLR_FILE",
    help="Path to write EAIS contribution to global SLR output file. If not provided, file will not be written.",
    type=str,
    required=False,
)
@click.option(
    "--output-WAIS-gslr-file",
    envvar="BAMBER19_ICESHEETS_OUTPUT_WAIS_GSLR_FILE",
    help="Path to write WAIS contribution to global SLR output file. If not provided, file will not be written.",
    type=str,
    required=False,
)
@click.option(
    "--output-GIS-gslr-file",
    envvar="BAMBER19_ICESHEETS_OUTPUT_GIS_GSLR_FILE",
    help="Path to write GIS contribution to global SLR output file. If not provided, file will not be written.",
    type=str,
    required=False,
)
@click.option(
    "--output-AIS-gslr-file",
    envvar="BAMBER19_ICESHEETS_OUTPUT_AIS_GSLR_FILE",
    help="Path to write AIS contribution to global SLR output file. If not provided, file will not be written.",
    type=str,
    required=False,
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
    nsamps,
    rngseed,
    location_file,
    chunksize,
    fingerprint_dir,
    replace,
    output_eais_lslr_file,
    output_wais_lslr_file,
    output_gis_lslr_file,
    output_ais_lslr_file,
    output_eais_gslr_file,
    output_wais_gslr_file,
    output_gis_gslr_file,
    output_ais_gslr_file,
) -> None:
    """
    Application producing sea level projections from ice sheet contributions following the methods of Bamber et al., 2019. Samples of estimated global contribution to sea level are produced for each ice sheet. These are then adjusted by applying spatial fingerprints to produce localized SLR projections for each ice sheet.
    """
    click.echo("Hello from bamber-19 ice sheets!")

    # Run preprocess step
    preprocess_output = bamber19_preprocess_icesheets(
        pyear_start=pyear_start,
        pyear_end=pyear_end,
        pyear_step=pyear_step,
        baseyear=baseyear,
        scenario=scenario,
        slr_proj_mat_fpath=slr_proj_mat_file,
        climate_data_file=climate_data_file,
    )
    # Run project step
    if climate_data_file is None:
        project_output = bamber19_project_icesheets(
            nsamps=nsamps,
            replace=replace,
            rngseed=rngseed,
            preprocess_output=preprocess_output,
            output_AIS_gslr_file=output_ais_gslr_file,
            output_GIS_gslr_file=output_gis_gslr_file,
            output_WAIS_gslr_file=output_wais_gslr_file,
            output_EAIS_gslr_file=output_eais_gslr_file,
        )
    else:
        project_output = bamber19_project_icesheets_temperaturedriven(
            climate_data_file=climate_data_file,
            replace=replace,
            rngseed=rngseed,
            preprocess_output=preprocess_output,
            output_AIS_gslr_file=output_ais_gslr_file,
            output_GIS_gslr_file=output_gis_gslr_file,
            output_WAIS_gslr_file=output_wais_gslr_file,
            output_EAIS_gslr_file=output_eais_gslr_file,
        )
    # Run postprocss step
    bamber19_postprocess_icesheets(
        projection_dict=project_output,
        location_fpath=location_file,
        chunksize=chunksize,
        fpdir=fingerprint_dir,
        output_EAIS_lslr_file=output_eais_lslr_file,
        output_WAIS_lslr_file=output_wais_lslr_file,
        output_GIS_lslr_file=output_gis_lslr_file,
        output_AIS_lslr_file=output_ais_lslr_file,
    )


if __name__ == "__main__":
    main()
