import os
import sys
import re

import numpy as np
import pandas as pd
import geopandas as gpd

import argparse


def full_address(df):
    """
    Concatenate each address component to a full address string
         (Street, City, State ZIP)
         
    Parameters
    ----------
        df (GeoDataFrame)

    Returns
    -------
        df (GeoDataFrame): with 'full_address' column
    """
    if 'ZIP' in df.columns:
        zip_col = 'ZIP'
    else:
        zip_col = 'ZIPCODE'

    if 'STATE' in df.columns:
        state_col = 'STATE'
    else:
        state_col = 'STNAME'

    if 'ADDRESS' in df.columns:
        addr_col = 'ADDRESS'
    elif 'ADDRESS' not in df.columns:
        addr_col = 'STREET'
    elif ('STREET' not in df.columns) and ('ADDRESS' not in df.columns):
        addr_col = 'STD_ADDR_B'

    df['Full_Address'] = df[[addr_col, 'CITY', state_col]].fillna('NaN').agg(', '.join, axis=1) + ' ' + df[zip_col].astype('str')
             
    return df


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


def get_centroid(dict):
    """
    Convert each GeoDataFrame to 'EPSG:4326'
         
    Parameters
    ----------
        dict (dictionary): GeoDataFrames of 'EPSG:4326' CRS

    Returns
    -------
        dict (dictionary): GeoDataFrames with extracted centroids from geoshapes
    """
    dict_centroids = {}
    for fname in dict:
        if 'x' in dict[fname].columns:
            dict[fname] = dict[fname].rename(columns={'x': 'source_lon', 'y': 'source_lat'})
            dict[fname]['Place_type'] = os.path.basename(fname)
            dict[fname]['source_centroid'] = dict[fname]['geometry']
        else:
            dict[fname]['source_centroid'] = dict[fname]['geometry'].centroid
            dict[fname]['source_lon'] = dict[fname]['geometry'].centroid.x
            dict[fname]['source_lat'] = dict[fname]['geometry'].centroid.y
            dict[fname]['Place_type'] = os.path.basename(fname)

        dict_centroids[fname] = keep_columns(dict[fname])
        
    return dict_centroids


def keep_columns(df):
    """
    Convert each GeoDataFrame to 'EPSG:4326'
         
    Parameters
    ----------
        df (GeoDataFrame): GeoDataFrames of 'EPSG:4326' CRS with extracted centroids

    Returns
    -------
        new_df (GeoDataFrame): GeoDataFrames with only source centroid and full address columns
    """
    cols = ['Full_Address', 'Place_type', 'source_centroid', 'source_lon', 'source_lat']
    new_df = df[cols]

    return new_df


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


def main():
    parser = argparse.ArgumentParser(
        description="Calculate centroids from geoshape files"
    )

    # args
    parser.add_argument("data_dir", required=True, help="path of geoshape files")
    parser.add_argument(
        "output_dir", required=True, help="path to save centroid geoshape files"
    )
    parser.add_argument(
        "rows", default=100, help="Number of rows to count per geoshape file"
    )

    args = parser.parse_args()

    HIFLD_path = args.data_dir
    shp_files = [
        os.path.join(root, name)
        for root, dirs, files in os.walk(HIFLD_path)
        for name in files
        if name.endswith((".shp"))
    ]

    dict_address = dict()
    for file in shp_files:
        basename = os.path.basename(file).split("/")[0]
        fname = os.path.basename(basename).split(".")[0]

        # print(file)
        df = read_shp(file, rows=args.rows)
        dict_address[fname] = full_address(df)

    dict_EPSG4326 = convert_EPSG4326(dict_address)
    dict_centroid = get_centroid(dict_EPSG4326)
    
    # save_dir = os.path.join(abs_path, 'data/HIFLD/centroids')
    save_dir = args.output_dir
    create_dir(save_dir)

    save_shp(dict_centroid, save_dir)


if __name__ == "__main__":
    print("Geoshape files with centroids saved")
