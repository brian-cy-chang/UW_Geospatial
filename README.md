# CLAD Geospatial
This repository provides instructions and examples for handling geoshape files from [Homeland Infrastructure Foundation-Level Data (HIFLD)](https://hifld-geoplatform.hub.arcgis.com/search) in Python. The goal is to extract centroid coordinates from geoshape polygons and spatial join to public US geospatial data to label as urban, rural, or tribal addresses.

## Getting Started
1. Download geoshape files from [Homeland Infrastructure Foundation-Level Data (HIFLD)](https://hifld-geoplatform.hub.arcgis.com/search) to a local directory. Simply add more geoshape files as desired. An example directory structure is shown below.
```
├───data
│   ├───HIFLD
│   │   ├───All_Places_Of_Worship
│   │   ├───FDIC_Insured_Banks
│   │   ├───Fire_Stations
│   │   ├───Prison_Boundaries
│   │   ├───Public_Schools
│   │   └───Urgent_Care_Facilities
├───figures
└───notebooks
```
2. Set up an Anaconda environment and install necessary packages with the command:<br> `pip install -r requirements.txt`<br>
Refer to the [Anaconda documentation](https://docs.anaconda.com/free/anaconda/install/index.html) as needed.

## Calculating Centroids for HIFLD Geoshape Files
1. Start with the [Jupyter notebook](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/calculate_centroid.ipynb) that provides examples on calculating and extracting centroids from geoshape files. This also explores geoshape data types and coordinate reference systems.

2. Depending on the data structure of certain geoshape files, some adjustments may be necessary to specific functions for calculating centroids.
    *  The function `full_address` parses individual address components based on column name strings for a given GeoDataFrame via a rule-based approach to generate a full address string (Street, City, State 5-digit ZIP). An additional rule may have to be written to handle additional geoshape files.

3. If you want to run a Python script, run `calculate_centroid.py` from the command line.

```
python calculate_centroid.py \
    --data_dir <directory of HIFLD geoshape files> \
    --output_dir <directory to save centroids geoshape files> \
    --rows <number of rows to read from data_dir> # default set to 100 rows per geoshape file
```

4. Example output geoshape files with the extracted centroids from select HIFLD datasets are shown [here](https://github.com/brian-cy-chang/CLAD_Geospatial/tree/main/output/HIFLD/centroids). An example output is also shown below.

| Full_Address                                                              | Place_type         | source_centroid                             | source_lon    | source_lat  |
|---------------------------------------------------------------------------|--------------------|---------------------------------------------|---------------|-------------|
| "100 North Tryon St, Charlotte, North Carolina 28202"                     | FDIC_Insured_Banks | POINT (-72.8786479999999 41.601435)         | -72.878648    | 41.601435   |
| "2 Elm Street, Camden, Maine 04843"                                       | FDIC_Insured_Banks | POINT (-68.4246209999999 44.5413260000001)  | -68.424621    | 44.541326   |


## Using spatial join to determine rurality
1. Start with the [Jupyter notebook](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/spatial_join.ipynb) that provides examples on spatial joining centroids to a Washington state tribal lands geoshape file. This also explores basic summary statistics.

2. Depending on the data structure and type of land geoshape file you are using for spatial joining, some adjustments may be necessary.
    * The function `spatial_join` accounts for either rural or tribal geoshape files to determine if a centroid falls within a geoshape polygon designated as either rural or tribal.

3. If you want to run a Python script, run `spatial_join.py` from the command line.

 ```
python spatial_join.py \
    --data_dir <directory of HIFLD centroid geoshape files> \
    --output_dir <directory to save spatial join geoshape files> \
    --rows <number of rows to read from data_dir> # default set to 100 rows per geoshape file
    --geoshape <directory of land geoshape file> \
    --filetype <type of land data> # choose from ['tribal', 'rural', 'other']
```