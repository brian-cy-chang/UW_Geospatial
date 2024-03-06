# CLAD Geospatial
This repository provides instructions and examples for handling geoshape files from [Homeland Infrastructure Foundation-Level Data (HIFLD)](https://hifld-geoplatform.hub.arcgis.com/search) in Python. The goal is to extract centroid coordinates from geoshape polygons and spatial join to US tribal lands data to label as urban, rural, or tribal addresses.

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
    --rows <number of rows> # default set to 100 rows per geoshape file
```