# Output Files

1. *OMOP_location_flagged_successful*: addresses that were parsed successfully from a full address string based on custom flag found in [us_address](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/usaddress.ipynb)
2. *OMOP_county_full*: same addresses as in *OMOP_location_flagged_successful* but with corrected leading zeros in "zip" and "county" added after spatial join to Census County TIGER/Line shapefile from [county_lookup](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/county_lookup.ipynb)
3. *OMOP_sample*: randomly sampled addresses from *OMOP_location_flagged_successful* that include 10 from each state plus US territories
4. *OMOP_sample_simulated_residential*: same addresses as in *OMOP_sample* but with simulated residental history fields generated in [simulated_residential_history](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/simulated_residential_history.ipynb)
5. *nominatim_keep_columns_merge_county_parsed*: contains the full address string for Nominatim input labeled `Nominatim_address` and only contains addresses where the county matched to both a spatial join to a census 2023 TIGER/line county shapefile and merge to a ZCTA crosswalk file on `zip` generated in [nominatim_parsing](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/nominatim_parsing.ipynb)
6. *omop_county_zcta_zip*: contains addresses with county names matched to both a spatial join to a census 2023 TIGER/line county shapefile and merge to a ZCTA crosswalk file on `zip` generated in [nominatim_parsing](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/nominatim_parsing.ipynb). Refer to column `county_match` to see which addresses did not match external validation
7. *nominatim_sample*: randomly sampled addresses from *nominatim_keep_columns_merge_county_parsed* with 11 addresses per state
8. *nominatim_failedAddresses_sample*: randomly sampled addresses from *nominatim_keep_columns_merge_county_parsed_failedAddresses* with 10 addresses per state and other US territories

## Deprecated Files

* *sample_spatial_join*: **IGNORE THIS FILE**
* *sample_spatial_join_OMOP*: **IGNORE THIS FILE** - parsed addresses using a custom parser from [OMOP](https://github.com/brian-cy-chang/CLAD_Geospatial/blob/main/notebooks/OMOP.ipynb) 
* *sample_spatial_join_OMOP_clean*: **IGNORE THIS FILE** - contains the same addresses as *sample_spatial_join_OMOP* but address strings were formatted with `title()` and full state name abbreviated to 2-characters 