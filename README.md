# CLAD Geospatial
This repository provides examples for handling geoshape files from [Homeland Infrastructure Foundation-Level Data (HIFLD)](https://hifld-geoplatform.hub.arcgis.com/search).

## 1. Calculate Centroids for HIFLD Geoshape Files

Run `calculate_centroid.py` to calculate centroids and extract longitude and latitude from EPSG:4326 coordinate system from polygons. 

```
python calculate_centroid.py \
    --data_dir <directory of geoshape files with polygons> \
    --output_dir <directory to save centroids geoshape files> \
    --rows <number of rows> # default set to 100 rows per geoshape file
```
Below is an example of directories for HIFLD files
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