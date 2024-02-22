import os
import sys
import re

import numpy as np
import pandas as pd
import geopandas as gpd

import argparse


def full_address(df):
    if "ZIP" in df.columns:
        zip_col = "ZIP"
    else:
        zip_col = "ZIPCODE"

    if "STATE" in df.columns:
        state_col = "STATE"
    else:
        state_col = "STNAME"

    if "ADDRESS" in df.columns:
        addr_col = "ADDRESS"
    elif "ADDRESS" not in df.columns:
        addr_col = "STREET"
    elif ("STREET" not in df.columns) and ("ADDRESS" not in df.columns):
        addr_col = "STD_ADDR_B"

    df["Full_Address"] = (
        df[[addr_col, "CITY", state_col]].fillna("NaN").agg(", ".join, axis=1)
        + " "
        + df[zip_col].astype("str")
    )

    return df


def read_shp(file, rows=100):
    df = gpd.read_file(file, rows=rows)

    return df


def convert_EPSG4326(dict):
    """
    dict from full_address
    maybe want to store source data before conversion
    """
    for fname in dict:
        dict[fname] = dict[fname].to_crs("EPSG:4326")

    return dict


def get_centroid(dict):
    """
    Returns Point object or a coordinate tuple (x, y)
    """
    for fname in dict:
        if "x" in dict[fname].columns:
            dict[fname] = dict[fname].rename(
                columns={"x": "source_lon", "y": "source_lat"}
            )
            dict[fname]["Place_type"] = os.path.basename(fname)
        else:
            dict[fname]["source_centroid"] = dict[fname]["geometry"].centroid
            dict[fname]["source_lon"] = dict[fname]["geometry"].centroid.x
            dict[fname]["source_lat"] = dict[fname]["geometry"].centroid.y
            dict[fname]["Place_type"] = os.path.basename(fname)

    return dict


def keep_columns(dict):
    """
    Keep full address string and calculated centroid (lon/lat)
    """
    cols = ["Full_Address", "Place_type", "source_centroid", "source_lon", "source_lat"]
    new_dict = {}
    for fname in dict:
        print(fname)
        new_dict[fname] = dict[fname][cols]

    return new_dict


def save_shp(dict, save_dir):
    for fname in dict:
        # dict[fname]['source_centroid'] = gpd.GeoSeries.from_wkt(dict[fname]['source_centroid'])
        shp_file = dict[fname].set_geometry("source_centroid")
        # shp_file = gpd.GeoDataFrame(dict[fname], geometry=dict[fname]['source_centroid'])
        # shp_file.to_file(os.path.join(save_dir, ('{}.shp'.format(fname))), driver='ESRI Shapefile')
        save_path = os.path.join(save_dir, f"{fname}")
        create_dir(save_path)
        shp_file.to_file(save_path, driver="ESRI Shapefile")


def create_dir(save_dir):
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
    final_dict = keep_columns(dict_centroid)

    # save_dir = os.path.join(abs_path, 'data/HIFLD/centroids')
    save_dir = args.output_dir
    create_dir(save_dir)

    save_shp(final_dict, save_dir)


if __name__ == "__main__":
    print("Geoshape files with centroids saved")
