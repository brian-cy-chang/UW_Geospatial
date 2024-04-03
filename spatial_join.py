import os
import sys
import re
import csv

import numpy as np
import pandas as pd
import geopandas as gpd

import argparse

def read_shp(file, rows=100):
    """
    Read geoshapes file

    Parameters
    ----------
        rows (int): number of rows per file to read

    Returns
    -------
        df (GeoDataFrame)
    """
    df = gpd.read_file(file, rows=rows)

    return df

def convert_EPSG4326(dict):
    """
    Convert each GeoDataFrame to 'EPSG:4326'
         
    Parameters
    ----------
        dict (dictionary): of GeoDataFrames

    Returns
    -------
        dict (dictionary): GeoDataFrames of 'EPSG:4326' CRS
    """
    for fname in dict:
        dict[fname] = dict[fname].to_crs("EPSG:4326")

    return dict

def spatial_join(dict, gdf, filetype, how='left'):
    """
    Spatial join centroids to geoshape file

    Parameters
    ----------
        dict (dictionary): of GeoDataFrames
        gdf (GeoDataFrame): of land shapes
        filetype (str): from args.filetype ('tribal' or 'rural')
        how (parameter): sjoin parameter, default = 'left'

    Returns
    -------
        dict_sjoin (dictionary): GeoDataFrames of 'EPSG:4326' CRS
    """
    dict_sjoin = {}
    for fname in dict:
        df = dict[fname].sjoin(tribal, how=how)
        
        # if centroid in tribal polygon, label as 1
        if filetype == 'tribal':
            df['Tribal'] = df.index_right.apply(lambda x: 0 if pd.isna(x) else 1) 
            dict_sjoin[fname] = df
        elif filetype == 'rural':
            df['Rural'] = df.index_right.apply(lambda x: 0 if pd.isna(x) else 1) 
            dict_sjoin[fname] = df
        elif filetype == 'other':
            df['Other'] = df.index_right.apply(lambda x: 0 if pd.isna(x) else 1) 
            dict_sjoin[fname] = df

    return dict_sjoin    

def save_shp(dict, save_dir):
    """
    Save each GeoDataFrame to individual geoshape files
         
    Parameters
    ----------
        dict (dictionary): GeoDataFrames of 'EPSG:4326' CRS with extracted centroids
        save_dir (str): path of desired output directory
    """
    for fname in dict:
        shp_file = dict[fname].set_geometry('source_centroid')
        
        save_path = os.path.join(save_dir, f"{fname}")
        create_dir(save_path)
        
        shp_file.to_file(save_path, driver='ESRI Shapefile')

def create_dir(save_dir):
    """
    Creates directory if it does not exist
         
    Parameters
    ----------
        save_dir (str): path of desired output directory
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

def summary_sjoin(dict_sjoin, output_dir):
    """
    Print summary statistics of dict_sjoin

    Parameters
    ----------
        dict_sjoin (dictionary): of spatial join GeoDataFrames
        output_dir (str): path to save summary_df csv file

    Returns
    -------
        summary_df (DataFrame): total counts spatial join results
    """
    summary_gdf = []
    for fname in dict_sjoin:
        # print(k, dict_sjoin[k].groupby('Tribal')['Full_Addre'].count())
        tmp = {}
        
        if 'Tribal' in dict_sjoin[fname].columns:
            tmp['Dataset'] = fname
            tmp['not_tribal'] = dict_sjoin[fname].Tribal.value_counts().tolist()[0]
            tmp['tribal'] = dict_sjoin[fname].shape[0] - dict_sjoin[fname].Tribal.value_counts().tolist()[0]
            summary_gdf.append(tmp)
        elif 'Rural' in dict_sjoin[fname].columns:
            tmp['Dataset'] = fname
            tmp['not_rural'] = dict_sjoin[fname].Rural.value_counts().tolist()[0]
            tmp['rural'] = dict_sjoin[fname].shape[0] - dict_sjoin[fname].Rural.value_counts().tolist()[0]
            summary_gdf.append(tmp)
        elif 'Other' in dict_sjoin[fname].columns:
            tmp['Dataset'] = fname
            tmp['not_rural'] = dict_sjoin[fname].Other.value_counts().tolist()[0]
            tmp['rural'] = dict_sjoin[fname].shape[0] - dict_sjoin[fname].Other.value_counts().tolist()[0]
            summary_gdf.append(tmp)
            
    summary_df = pd.DataFrame(summary_gdf)
    summary_df.to_csv(os.path.join(output_dir, 'summary.csv'), index=False)

    return summary_df

def main():
    parser = argparse.ArgumentParser(
        description="Spatial join geoshape files"
    )

    # args
    parser.add_argument("data_dir", required=True, help="path of geoshape files")
    parser.add_argument(
        "output_dir", required=True, help="path to save spatial joined geoshape files"
    )
    parser.add_argument(
        "rows", default=100, help="Number of rows to count per geoshape file"
    )
    parser.add_argument(
        "geoshape", required=True, help="path to land geoshapes file"
    )
    parser.add_argument(
        "filetype", required=True, help="land type of geoshape file", choices=['tribal', 'rural', 'other']
    )

    args = parser.parse_args()

    HIFLD_path = args.data_dir
    shp_files = [
        os.path.join(root, name)
        for root, dirs, files in os.walk(HIFLD_path)
        for name in files
        if name.endswith((".shp"))
    ]
    geoshape_file = [
        os.path.join(root, name)
        for root, dirs, files in os.walk(args.geoshape)
        for name in files
        if name.endswith((".shp"))
    ]
    geoshape_gdf = gpd.read_file(geoshape_file)

    centroids_dict = dict()
    for file in shp_files:
        basename = os.path.basename(file).split('/')[0]
        fname = os.path.basename(basename).split('.')[0]

        # print(file)
        df = read_shp(file, rows=args.rows)
        centroids_dict[fname] = df

    dict_EPSG4326 = convert_EPSG4326(centroids_dict)
    geoshapes_4326 = geoshape_gdf.to_crs("EPSG:4326")

    dict_sjoin = spatial_join(dict_EPSG4326, geoshapes_4326, args.filetype)

    save_dir = args.output_dir
    create_dir(save_dir)

    summary_df = summary_sjoin(dict_sjoin, save_dir)
    print(summary_df.to_string())

if __name__ == "__main__":
    main()
    print("Spatial join files saved")
