# bamber19-icesheets

An application producing sea level projections by sampling from the Structured Expert Judgement ice sheet projections of Bamber et al. (2019). 

>[!CAUTION]
> This is a prototype. It is likely to change in breaking ways. It might delete all your data. Don't use it in production.

## Example

This application can run on emissions-projected climate data. For example, you can use the output `climate.nc` file from the [fair model container](https://github.com/stcaf-org/fair-temperature). Additional input data is located in this repository.

There are multiple ways to run the application. You can clone the repository and run the program in a Docker container built from the provided `Dockerfile` or using `uv`. Alternatively, you can run the scripts that are hosted remotely on GitHub using `uvx --from`.

### Setup
If you clone the directory, make sure that the data sub-directory is in the root directory. 
```shell
git clone -b fix_history_package git@github.com:e-marshall/bamber19-icesheets.git
```
If you don't clone the repository, create a new directory and from here, create download the necessary data to prepare for the run. 
```shell
# Input data we will pass to the container
mkdir -p ./data/input
curl -sL https://zenodo.org/records/7478192/files/bamber19_icesheets_preprocess_data.tgz | tar -zx -C ./data/input

echo "New_York	12	40.70	-74.01" > ./data/input/location.lst

# Output projections will appear here
mkdir -p ./data/output
```

### Run in a container
After you've cloned the repo and downloaded the necessary data, from the root directory, create a docker image that we will use to run the application:
```shell
docker build -t bamber19-icesheets .
```

Then, create a container based on the image (`docker run --rm`), mount volumes for both the input and output data sub-directories and set the working directory to the location of the app in the container (`-w`). Then, call the application, passing the desired input arguments and making sure that the paths for each input argument are relative to the mounted volumes:
```shell
docker run --rm -v ./data/input:/mnt/bamber_data_in:ro -v ./data/output:/mnt/bamber_data_out bamber19-icesheets --pipeline-id YOUR_PIPELINE_ID --slr-proj-mat-file /mnt/bamber_data_in/SLRProjections190726core_SEJ_full.mat --climate-data-file /mnt/bamber_data_in/fair_out/bamber19.ssp585.temperature.fair.temperature_climate.nc --location-file /mnt/bamber_data_in/location.lst --fingerprint-dir /mnt/bamber_data_in/grd_fingerprints_data/FPRINT --output-path /mnt/bamber_data_out 
```
### Running locally

After cloning the repository, from the root directory, run the application using `uv`:
```shell
uv run bamber19-icesheets --pipeline-id YOUR_PIPELINE_ID \
--climate-data-file path/to/data/input/fair_out/bamber19.ssp585.temperature.fair.temperature_climate.nc \
--scenario 'ssp585' \
--slr-proj-mat-file path/to/data/input/SLRProjections190726core_SEJ_full.mat \
--location-file path/to/data/input/location.lst \
--fingerprint-dir path/to/data/input/grd_fingerprints_data/FPRINT \
--output-path path/to/data/output
```
### Run remote scripts
To run without cloning & building a container on your local machine:
```shell
 uvx --from git+https://github.com/e-marshall/bamber19-icesheets.git@fix_history_package \
 bamber19-icesheets --pipeline-id YOUR_PIPELINE_ID \
 --climate-data-file path/to/data/input/fair_out/bamber19.ssp585.temperature.fair.temperature_climate.nc \
 --scenario 'ssp585' \
 --slr-proj-mat-file path/to/data/input/SLRProjections190726core_SEJ_full.mat \
 --location-file path/to/data/input/location.lst \
 --fingerprint-dir path/to/data/input/grd_fingerprints_data/FPRINT \
 --output-path path/to/data/output
```

## Features
Several options and configurations are available when running the container. 

```shell
Usage: bamber19-icesheets [OPTIONS]

  Application producing sea level projections from ice sheet contributions
  following the methods of Bamber et al., 2019. Samples of estimated global
  contribution to sea level are produced for each ice sheet. These are then
  adjusted by applying spatial fingerprints to produce localized SLR
  projections for each ice sheet.

Options:
  --pipeline-id TEXT           Unique identifier for this instance of the
                               module. Used to name output files.  [required]
  --pyear-start INTEGER RANGE  Projection year start [default=2020]  [x>=2020]
  --pyear-end INTEGER RANGE    Projection year end [default=2100]  [x<=2300]
  --pyear-step INTEGER RANGE   Projection year step [default=10]  [x>=1]
  --baseyear INTEGER           Year to which projections are referenced
                               [default = 2000]
  --scenario TEXT              Emissions scenario of interest [default=ssp585]
  --climate-data-file TEXT     NetCDF4/HDF5 file containing surface
                               temperature data  [default: ""]
  --slr-proj-mat-file TEXT     Path to the SLR projections matlab file
                               [default: bamber19_icesheets_preprocess_data/SL
                               RProjections190726core_SEJ_full.mat]
  --scenario-map DICT          Mapping of scenario names to core files
  --nsamps INTEGER             Number of samples to draw [default=500]
  --replace INTEGER            Whether to sample with replacement [default=1]
  --rngseed INTEGER            Seed for the random number generator
                               [default=1234]
  --location-file TEXT         Path to location file for postprocessing
  --chunksize INTEGER          Chunk size for postprocessing [default=50]
  --fingerprint-dir TEXT       Directory to save postprocessed files to
                               [default='']
  --output-path TEXT           Directory to save postprocessed files to
                               [default='output/']
  --help                       Show this message and exit.
```

See this help documentation by passing the `--help` flag when running the application in any of the options above. For example: 

```shell
uvx --from git+https://github.com/e-marshall/bamber19-icesheets.git@fix_history_package bamber19-icesheets --help
```   

```shell
uv run bamber19-icesheets --help 
```

## Results
If this module runs successfully, output projections will appear in `./data/output`. For each ice sheet (EAIS, WAIS, AIS, GIS), two netCDF files are written: one of projections of ice sheet contribution to global sea-level change and one of sampled projections of ice sheet contribution to local sea-level change. 

## Notes
(these probably belong elsewhere but have them here for now)
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
