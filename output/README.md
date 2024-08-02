# Output Files

* *OMOP_location_flagged_successful*: addresses that were parsed successfully from a full address string based on custom flag found in [us_address](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/usaddress.ipynb)
* *OMOP_county_full*: same addresses as in *OMOP_location_flagged_successful* but with corrected leading zeros in "zip" and "county" added after spatial join to Census County TIGER/Line shapefile
* *OMOP_sample*: randomly sampled addresses from *OMOP_location_flagged_successful* that include 10 from each state plus US territories
* *OMOP_sample_simulated_residential*: same addresses as in *OMOP_sample* but with simulated residental history fields generated in [simulated_residential_history](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/simulated_residential_history.ipynb)

* *sample_spatial_join*: **IGNORE THIS FILE**
* *sample_spatial_join_OMOP*: **IGNORE THIS FILE** - parsed addresses using a custom parser from [OMOP](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/OMOP.ipynb) 
* *sample_spatial_join_OMOP_CLEAN*: **IGNORE THIS FILE** - contains the same addresses as *sample_spatial_join_OMOP* but address strings were formatted with `title()` and full state name abbreviated to 2-characters 