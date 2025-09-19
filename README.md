# bamber19-icesheets

An application producing sea level projections by sampling from the Structured Expert Judgement ice sheet projections of Bamber et al. (2019). 

>[!CAUTION]
> This is a prototype. It is likely to change in breaking ways. It might delete all your data. Don't use it in production.

## Example

This application can run on emissions-projected climate data. For example, you can use the output `climate.nc` file from the [fair model container](https://github.com/stcaf-org/fair-temperature). Additional input data is located in this repository.

First, create a new directory and download the required input data to prepare for the run. 

```shell
# Input data we will pass to the container
mkdir -p ./data/input
curl -sL https://zenodo.org/records/7478192/files/bamber19_icesheets_preprocess_data.tgz | tar -zx -C ./data/input

echo "New_York	12	40.70	-74.01" > ./data/input/location.lst

# Output projections will appear here
mkdir -p ./data/output
```
Now, run the CLI app (TODO: add docker + change this, just a stand-in for now):

```shell 
uv run bamber19-icesheets --pipeline-id bamber19_ssp585_dummy_run --climate-data-file data/input/bamber19.ssp585.temperature.fair.temperature_climate.nc --scenario 'ssp585' --pyear-start 2020 --pyear-end 2150 --nsamps 500 --baseyear 2000 

```

## Features
Several options and configurations are available when running the container. 
```shell
TO DO INSERT
```

See this help documentation by running: 
```shell
TO DO INSERT
```

## Results
If this module runs successfully, output projections will appear in `./data/output`. For each ice sheet (EAIS, WAIS, AIS, GIS), two netCDF files are written: one of projections of ice sheet contribution to global sea-level change and one of sampled projections of ice sheet contribution to local sea-level change. 

## Notes
- All input arguments in the [original module](https://github.com/stcaf-org/bamber19-icesheets/tree/main/modules/bamber19/icesheets) are defined in `cli.py` and passed to `main()`. 

- Where necessary, new arguments are created to replace hard-coded paths and other variables in the original. 

- Unless noted, default values for input args that exist in the original module are taken from the original module.

- `--climate-data-file`
This is the output of the Climate step (a FAIR temperature model run) in a FACTS v.1 experiment. It is not required to run this module. However, not passing a climate data file encodes other assumtions in the bamber19 run which can cause errors depending on other input arguments. For example, if no climate data is passed, this implies that the scenario is either 'rcp85' or 'rcp26' or temperature targets 'tlim2.0win0.25' or 'tlim5.0win0.25'. The default scenario for bamber19-icesheets is 'ssp585';if no climate data file is passed, a scenario argument must be passed to specify one of the above-mentioned options. 
    >[!NOTE] These options are specified in the `scenario_map` input argument and used in `bamber19_preprocess_icesheets()` in the `bamber19_icesheets_preprocess.py` script.

- `--nsamps`
If a FAIR output file is passed, the number of samples in the FAIR output file that is passed must match `--nsamps` specified for the Bamber19-icesheets run. Additionally, this module expects a `climate.nc` file for that argument, from which it uses the temperature variable. If a `gsat.nc` is passed, a TODO ADD error will be raised. The default value is updated from 10 in original to 500.

- `--baseyear`
The `--baseyear` passed to `bamber19-icesheets` must match the base year used to in the FAIR temperature modeling step. 

- `--pyear-start`
This value must be greater than or equal to 2020 and must be a multiple of 10 (this is to match the temporal resolution of the data in the input file, `SLRProjections190726Score_SEJ_full.mat`).

- `--pyear-step`
This value must be a multiple of 10. This is to match the temporal resolution of the data in the input file, `SLRProjections190726Score_SEJ_full.mat`.

- `--pyear-end`
This can be any integer. It *should* be any integer > `pyear-start` (or some minimum time window?); currently, you can pass any value for `pyear-end` and if it less than or equal to `pyear-start`, the program will write the expected netcdfs with `years` dimensions of length zero.


## Support

Source code is available online at https://github.com/stcaf-org/bamber19-icesheets. This software is open source, available under the MIT license.

Please file issues in the issue tracker at https://github.com/stcaf-org/bamber19-icesheets/issues.
