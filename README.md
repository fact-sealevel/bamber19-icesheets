# bamber19-icesheets

An application producing sea level projections by sampling from the Structured Expert Judgement ice sheet projections of Bamber et al. (2019). 

>[!CAUTION]
> This is a prototype. It is likely to change in breaking ways. It might delete all your data. Don't use it in production.

## Example

This application can run on emissions-projected climate data. For example, you can use the output `climate.nc` file from the [FAIR model container](https://github.com/fact-sealevel/fair-temperature). Additional input data is located in this repository.

### Setup

Clone the repository and create directories to hold input and output data. 

```shell
git clone git@github.com:fact-sealevel/bamber19-icesheets.git
```

Download input data using the following Zenodo records:

```shell
# Input data we will pass to the container
mkdir -p ./data/input
curl -sL https://zenodo.org/record/7478192/files/bamber19_icesheets_preprocess_data.tgz | tar -zx -C ./data/input
# Fingerprint input data for postprocessing step
curl -sL https://zenodo.org/record/7478192/files/grd_fingerprints_data.tgz | tar -zx -C ./data/input

echo "New_York	12	40.70	-74.01" > ./data/input/location.lst

# Output projections will appear here
mkdir -p ./data/output
```

Next, run the container associated with this package. For example: 



```shell
docker run --rm \
  -v ./data/input:/mnt/bamber_data_in:ro \
  -v ./data/output:/mnt/bamber_data_out \
  ghcr.io/fact-sealevel/bamber19-icesheets:0.1.0 \
  --pipeline-id MY_PIPELINE_ID \
  --slr-proj-mat-file /mnt/bamber_data_in/SLRProjections190726core_SEJ_full.mat \
  --location-file /mnt/bamber_data_in/location.lst \
  --fingerprint-dir /mnt/bamber_data_in/FPRINT \
  --output-EAIS-lslr-file /mnt/bamber_data_out/output_eais_lslr.nc \
  --output-WAIS-lslr-file /mnt/bamber_data_out/output_wais_lslr.nc \
  --output-GIS-lslr-file /mnt/bamber_data_out/output_gis_lslr.nc \
  --output-AIS-lslr-file /mnt/bamber_data_out/output_ais_lslr.nc \
  --output-EAIS-gslr-file /mnt/bamber_data_out/output_eais_gslr.nc \
  --output-WAIS-gslr-file /mnt/bamber_data_out/output_wais_gslr.nc \
  --output-GIS-gslr-file /mnt/bamber_data_out/output_gis_gslr.nc \
  --output-AIS-gslr-file /mnt/bamber_data_out/output_ais_gslr.nc 
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
  --pipeline-id TEXT              Unique identifier for this instance of the
                                  module.
  --pyear-start INTEGER RANGE     Projection year start  [default: 2020;
                                  x>=2020]
  --pyear-end INTEGER RANGE       Projection year end  [default: 2100;
                                  x<=2300]
  --pyear-step INTEGER RANGE      Projection year step  [default: 10; x>=1]
  --baseyear INTEGER              Year to which projections are referenced
                                  [default: 2000]
  --scenario [rcp26|rcp45|rcp85|ssp119|ssp126|ssp245|ssp370|ssp585]
                                  Emissions scenario of interest  [default:
                                  rcp85]
  --climate-data-file TEXT        NetCDF4/HDF5 file containing surface
                                  temperature data
  --slr-proj-mat-file TEXT        Path to the SLR projections matlab file
                                  [required]
  --nsamps INTEGER                Number of samples to draw  [default: 500]
  --replace INTEGER RANGE         Whether to sample with replacement
                                  [default: 1; 0<=x<=1]
  --rngseed INTEGER               Seed for the random number generator
                                  [default: 1234]
  --location-file TEXT            Path to file that contains name, id, lat,
                                  and lon of points for localization
                                  [required]
  --chunksize INTEGER             Number of locations to process at a time
                                  [default: 50]
  --fingerprint-dir TEXT          Path to directory containing fingerprint
                                  files  [required]
  --output-EAIS-lslr-file TEXT    Path to write EAIS contribution to local SLR
                                  output file. If not provided, file will not
                                  be written.
  --output-WAIS-lslr-file TEXT    Path to write WAIS contribution to local SLR
                                  output file. If not provided, file will not
                                  be written.
  --output-GIS-lslr-file TEXT     Path to write GIS contribution to local SLR
                                  output file. If not provided, file will not
                                  be written.
  --output-AIS-lslr-file TEXT     Path to write AIS contribution to local SLR
                                  output file. If not provided, file will not
                                  be written.
  --output-EAIS-gslr-file TEXT    Path to write EAIS contribution to global
                                  SLR output file. If not provided, file will
                                  not be written.
  --output-WAIS-gslr-file TEXT    Path to write WAIS contribution to global
                                  SLR output file. If not provided, file will
                                  not be written.
  --output-GIS-gslr-file TEXT     Path to write GIS contribution to global SLR
                                  output file. If not provided, file will not
                                  be written.
  --output-AIS-gslr-file TEXT     Path to write AIS contribution to global SLR
                                  output file. If not provided, file will not
                                  be written.
  --help                          Show this message and exit.
```

See this help documentation by passing the `--help` flag when running the application, for example: 

```shell
docker run --rm bamber19-icesheets --help
```   

## Results
If this module runs successfully, output projections will appear in `./data/output`. For each ice sheet (EAIS, WAIS, AIS, GIS), two NetCDF files may be written: one of projections of ice sheet contribution to global sea-level change and one of sampled projections of ice sheet contribution to local sea-level change. 

## Build the container locally
You can build the container with Docker by cloning the repository locally and then running the following command from the repository root:

```shell
docker build -t bamber19-icesheets .

```

## Support

Source code is available online at https://github.com/fact-sealevel/bamber19-icesheets. This software is open source, available under the MIT license.

Please file issues in the issue tracker at https://github.com/fact-sealevel/bamber19-icesheets/issues.
