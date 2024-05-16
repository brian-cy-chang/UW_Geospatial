import os
from os import listdir
from os.path import isfile, join, splitext
import sys
import csv
import re
import argparse

import numpy as np
import pandas as pd
import geopandas as gpd

import usaddress

"""USPS Publication 28 Address Standard"""
Pub28_usaddress_template = {
    "Recipient": "recipient",
    "AddressNumber": "address1",
    "AddressNumberPrefix": "address1",
    "AddressNumberSuffix": "address1",
    "StreetName": "address1",
    "StreetNamePreDirectional": "address1",
    "StreetNamePreModifier": "address1",
    "StreetNamePreType": "address1",
    "StreetNamePostDirectional": "address1",
    "StreetNamePostModifier": "address1",
    "StreetNamePostType": "address1",
    "CornerOf": "address1",
    "IntersectionSeparator": "address1",
    "LandmarkName": "address1",
    "USPSBoxGroupID": "address1",
    "USPSBoxGroupType": "address1",
    "USPSBoxID": "address1",
    "USPSBoxType": "address1",
    "BuildingName": "address2",
    "OccupancyType": "address2",
    "OccupancyIdentifier": "address2",
    "SubaddressIdentifier": "address2",
    "SubaddressType": "address2",
    "PlaceName": "city",
    "StateName": "state",
    "ZipCode": "zip_code",
}

"""Dictionary of US state full name : state abbreviation"""
us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

state_full_pattern = r"/AL|Alabama|AK|Alaska|AZ|Arizona|AR|Arkansas|CA|California|CO|Colorado|CT|Connecticut|DE|Delaware|FL|Florida|GA|Georgia|HI|Hawaii|ID|Idaho|IL|Illinois|IN|Indiana|IA|Iowa|KS|Kansas|KY|Kentucky|LA|Louisiana|ME|Maine|MD|Maryland|MA|Massachusetts|MI|Michigan|MN|Minnesota|MS|Mississippi|MO|Missouri|MT|Montana|NE|Nebraska|NV|Nevada|NH|New Hampshire|NJ|New Jersey|NM|New Mexico|NY|New York|NC|North Carolina|ND|North Dakota|OH|Ohio|OK|Oklahoma|OR|Oregon|PA|Pennsylvania|RI|Rhode Island|SC|South Carolina|SD|South Dakota|TN|Tennessee|TX|Texas|UT|Utah|VT|Vermont|VA|Virginia|WA|Washington|WV|West Virginia|WI|Wisconsin|WY|Wyoming/"
state_abbr_pattern = re.compile(r"\b(AZ|CA|...|NJ|N\.J\.|NM|N\.M\.|...)\b")
state_abbr_case = r"^([Aa][LKSZRAEPlkszraep]|[Cc][AOTaot]|[Dd][ECec]|[Ff][LMlm]|[Gg][AUau]|[Hh][Ii]|[Ii][ADLNadln]|[Kk][SYsy]|[Ll][Aa]|[Mm][ADEHINOPSTadehinopst]|[Nn][CDEHJMVYcdehjmvy]|[Oo][HKRhkr]|[Pp][ARWarw]|[Rr][Ii]|[Ss][CDcd]|[Tt][NXnx]|[Uu][Tt]|[Vv][AITait]|[Ww][AIVYaivy])$"
zip_code_pattern = r"[0-9]{5}(?:-[0-9]{4})?"

os.chdir("..")
abs_path = os.getcwd()


def create_dir(save_dir):
    """
    Creates directory if it does not exist

    Parameters
    ----------
        save_dir (str): path of desired output directory
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)


def OMOP_Dataset(address_df, address_col):
    """
    Create and populate OMOP DataFrame for development

    Parameters
    ----------
    address_df (DataFrame): initial address DataFrame
    """
    OMOP_df = pd.DataFrame(
        columns=[
            "Location_id",
            "address_1",
            "address_2",
            "city",
            "state",
            "zip",
            "county",
            "location_source_value",
            "latitude",
            "longitude",
        ]
    )

    OMOP_df["location_source_value"] = address_df.address_col
    OMOP_df["location_id"] = OMOP_df.index + 1

    # OMOP_location['Location_id'] = OMOP_location.re+1
    OMOP_df.latitude = address_df.source_lat
    OMOP_df.longitude = address_df.source_lon

    return OMOP_df


def usaddress_parse(df, tag_template=Pub28_usaddress_template):
    """
    df (DataFrame): must contain `location_source_value`

    Parameters
    ----------
    df (DataFrame): OMOP_df for address parsing
    """
    repo = pd.DataFrame()
    for idx, each in df.loc[:, ["location_source_value"]].drop_duplicates().iterrows():
        # try Pub28 parsing
        try:
            obj = usaddress.tag(each.location_source_value, tag_mapping=tag_template)

            # staging
            tmp = pd.DataFrame(obj[0], columns=obj[0].keys(), index=[idx])
            tmp["Address_type"] = obj[1]

            # development
            df.loc[idx, "address_1"] = tmp["address1"].values[0]
            df.loc[idx, "city"] = tmp["city"].values[0]
            df.loc[idx, "state"] = tmp["state"].values[0]
            df.loc[idx, "zip"] = tmp["zip_code"].values[0]
            df.loc[idx, "address_type"] = tmp["Address_type"].values[0]

            address_2 = tmp["address2"].values[0]
            if len(address_2) >= 3:
                df.loc[ind, "address_2"] = address_2
            else:
                df.loc[ind, "address_2"] = np.NaN

            repo = repo.append(tmp)

        except:
            pass

    return df


def multipleReplace(text, wordDict=us_state_to_abbrev):
    """
    Replace string value from dictionary
    """
    for key in wordDict:
        text = text.replace(key, wordDict[key])
    return text


def OMOP_clean(df):
    """
    Replace full state names with state abbreviations and
        only capitalize first string character
    """
    df["state_abbr"] = df.state.apply(lambda x: multipleReplace(str(x).strip()))

    # clean string values where only first character is capitalized
    df["address_1"] = df.address_1.apply(lambda x: str(x).strip().title())
    df["address_2"] = df.address_2.apply(
        lambda x: str(x).strip().title() if not np.NaN else x
    )
    df["city"] = df.city.apply(lambda x: str(x).strip().title())

    return df


def custom_parser(
    df,
    address_col,
    state_full_pattern,
    state_abbr_pattern,
    zip_code_pattern=r"[0-9]{5}(?:-[0-9]{4})?",
):
    """
    Parse full address string to OMOP components by Regex search

    Parameters
    ----------
    df (DataFrame): Pandas DataFrame of failed addresses

    Returns
    -------
    parse_df (DataFrame): DataFrame with parsed OMOP address components
    """
    tmp = []
    for i, row in df.iterrows():
        addr_components = row[address_col].split(",")

        # parse address if no RegEx match for 'APT'
        if len(re.findall(r"APT", row[address_col], flags=re.IGNORECASE)) == 0:
            state_zip = addr_components[2].split(" ")
            if (
                len(re.findall(state_abbr_pattern, addr_components[-1])) > 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) > 0
            ):
                row["address_1"] = addr_components[0]
                row["address_2"] = np.NaN
                row["city"] = addr_components[1]
                row["state"] = re.findall(state_abbr_pattern, addr_components[-1])[0]
                row["zip"] = re.findall(zip_code_pattern, addr_components[-1])[0]

                tmp.append(row)
            elif (
                len(re.findall(state_abbr_pattern, addr_components[-1])) > 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) == 0
            ):
                row["address_1"] = addr_components[0]
                row["address_2"] = np.NaN
                row["city"] = addr_components[1]
                row["state"] = re.findall(state_abbr_pattern, addr_components[-1])[0]
                row["zip"] = np.NaN

                tmp.append(row)

            elif (
                len(re.findall(state_abbr_pattern, addr_components[-1])) == 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) > 0
                and len(re.findall(state_full_pattern, addr_components[-1].title())) > 0
            ):
                row["address_1"] = addr_components[0]
                row["address_2"] = np.NaN
                row["city"] = addr_components[1]
                row["state"] = re.findall(
                    state_full_pattern, addr_components[-1].title()
                )[0]
                row["zip"] = re.findall(zip_code_pattern, addr_components[-1])[0]

                tmp.append(row)

            elif (
                len(re.findall(state_abbr_pattern, addr_components[-1])) == 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) == 0
            ):
                row["address_1"] = addr_components[0]
                row["address_2"] = np.NaN
                row["city"] = addr_components[1]
                row["state"] = re.findall(
                    state_full_pattern, addr_components[-1].title()
                )
                row["zip"] = np.NaN

                tmp.append(row)

        # # parse address if RegEx match for 'APT' to address_1 & address_2
        elif len(re.findall(r"APT", row[address_col], flags=re.IGNORECASE)) > 0:
            if (
                len(re.findall(state_abbr_pattern, addr_components[-1])) > 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) > 0
            ):
                base_address = addr_components[0]
                apt_string = re.findall(r"APT", row[address_col], flags=re.IGNORECASE)[
                    0
                ]
                row["address_1"] = base_address.partition(apt_string)[0]
                row["address_2"] = (
                    base_address.partition(apt_string)[1]
                    + base_address.partition(apt_string)[2]
                )
                row["city"] = addr_components[1]
                row["state"] = re.findall(state_abbr_pattern, addr_components[-1])[0]
                row["zip"] = re.findall(zip_code_pattern, addr_components[-1])[0]

                tmp.append(row)

            elif (
                len(re.findall(state_abbr_pattern, addr_components[-1])) > 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) == 0
            ):
                base_address = addr_components[0]
                apt_string = re.findall(r"APT", base_address, flags=re.IGNORECASE)[0]
                row["address_1"] = base_address.partition(apt_string)[0]
                row["address_2"] = (
                    base_address.partition(apt_string)[1]
                    + base_address.partition(apt_string)[2]
                )
                row["city"] = addr_components[1]
                row["state"] = re.findall(state_abbr_pattern, addr_components[-1])[0]
                row["zip"] = np.NaN

                tmp.append(row)

            elif (
                len(re.findall(state_abbr_pattern, addr_components[-1])) == 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) > 0
                and len(re.findall(state_full_pattern, addr_components[-1].title())) > 0
            ):
                base_address = addr_components[0]
                apt_string = re.findall(r"APT", base_address, flags=re.IGNORECASE)[0]
                row["address_1"] = base_address.partition(apt_string)[0]
                row["address_2"] = (
                    base_address.partition(apt_string)[1]
                    + base_address.partition(apt_string)[2]
                )
                row["city"] = addr_components[1]
                row["state"] = re.findall(
                    state_full_pattern, addr_components[-1].title()
                )[0]
                row["zip"] = re.findall(zip_code_pattern, addr_components[-1])[0]

                tmp.append(row)

            elif (
                len(re.findall(state_abbr_pattern, addr_components[-1])) == 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) == 0
            ):
                base_address = addr_components[0]
                apt_string = re.findall(r"APT", base_address, flags=re.IGNORECASE)[0]
                row["address_1"] = base_address.partition(apt_string)[0]
                row["address_2"] = (
                    base_address.partition(apt_string)[1]
                    + base_address.partition(apt_string)[2]
                )
                row["city"] = addr_components[1]
                row["state"] = re.findall(
                    state_full_pattern, addr_components[-1].title()
                )
                row["zip"] = np.NaN

                tmp.append(row)

        # # parse address if RegEx match for 'Suite' to to address_1 & address_2
        elif len(re.findall(r"SUITE", row[address_col], flags=re.IGNORECASE)) > 0:
            if (
                len(re.findall(state_abbr_pattern, addr_components[-1])) > 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) > 0
            ):
                base_address = addr_components[0]
                suite_str = re.findall(r"SUITE", base_address, flags=re.IGNORECASE)[0]
                row["address_1"] = base_address.partition(suite_str)[0]
                row["address_2"] = (
                    base_address.partition(suite_str)[1]
                    + base_address.partition(suite_str)[2]
                )
                row["city"] = addr_components[1]
                row["state"] = re.findall(state_abbr_pattern, addr_components[-1])[0]
                row["zip"] = re.findall(zip_code_pattern, addr_components[-1])[0]

                tmp.append(row)

            elif (
                len(re.findall(state_abbr_pattern, addr_components[-1])) > 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) == 0
            ):
                base_address = addr_components[0]
                suite_str = re.findall(r"SUITE", base_address, flags=re.IGNORECASE)[0]
                row["address_1"] = base_address.partition(suite_str)[0]
                row["address_2"] = (
                    base_address.partition(suite_str)[1]
                    + base_address.partition(suite_str)[2]
                )
                row["city"] = addr_components[1]
                row["state"] = re.findall(state_abbr_pattern, addr_components[-1])[0]
                row["zip"] = np.NaN

                tmp.append(row)

            elif (
                len(re.findall(state_abbr_pattern, addr_components[-1])) == 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) > 0
                and len(re.findall(state_full_pattern, addr_components[-1].title())) > 0
            ):
                base_address = addr_components[0]
                suite_str = re.findall(r"SUITE", base_address, flags=re.IGNORECASE)[0]
                row["address_1"] = base_address.partition(suite_str)[0]
                row["address_2"] = (
                    base_address.partition(suite_str)[1]
                    + base_address.partition(suite_str)[2]
                )
                row["city"] = addr_components[1]
                row["state"] = re.findall(
                    state_full_pattern, addr_components[-1].title()
                )[0]
                row["zip"] = re.findall(zip_code_pattern, addr_components[-1])[0]

                tmp.append(row)

            elif (
                len(re.findall(state_abbr_pattern, addr_components[-1])) == 0
                and len(re.findall(zip_code_pattern, addr_components[-1])) == 0
            ):
                base_address = addr_components[0]
                suite_str = re.findall(r"SUITE", base_address, flags=re.IGNORECASE)[0]
                row["address_1"] = base_address.partition(suite_str)[0]
                row["address_2"] = (
                    base_address.partition(suite_str)[1]
                    + base_address.partition(suite_str)[2]
                )
                row["city"] = addr_components[1]
                row["state"] = re.findall(
                    state_full_pattern, addr_components[-1].title()
                )
                row["zip"] = np.NaN

                tmp.append(row)

    return pd.DataFrame(tmp)


def custom_flag(x):
    """
    Post-hoc data quality check of parsed addresses
    """
    if "PO" in str(x.address_1) or "P.O." in str(x.address_1):
        return "FAILED DUE TO PO BOX ADDRESS"
    if re.match("APT", x.address_1, re.IGNORECASE) or re.match(
        "SUITE", x.address_1, re.IGNORECASE
    ):
        return "FAILED DUE TO STREET ADDRESS IN LINE_1 IS FLIPPED WITH LINE_2"
    elif not x.address_1[0].isdigit():
        return "FAILED DUE TO STREET ADDRESS STARTS WITH LETTER"
    # check address_1 only contains alphanumeric characters (spaces are ok)
    elif any(not c.isalnum() and not c.isspace() for c in x.address_1):
        return "FAILED DUE TO PRESENCE OF SPECIAL CHARACTERS"
    elif len(x.state_abbr) > 2:
        return "FAILED DUE TO INCORRECT STATE FORMAT"
    elif x[["address_1", "city", "state", "zip"]].isnull().any():
        return "FAILED DUE TO INCOMPLETE PARSING"
    else:
        return "SUCCESSFUL ADDRESS"


def main():
    parser = argparse.ArgumentParser(description="Parse addresses to OMOP components")

    # args
    parser.add_argument("address_dir", required=True, help="path of address file (csv)")
    parser.add_argument("address_col", required=True, help="column name of full address string")
    parser.add_argument(
        "output_dir", required=True, help="path to save parsed address file"
    )

    address_df = pd.read_csv(args.address_dir)
    address_drop = address_df.drop_duplicates(subset=args.address_col)

    OMOP_df = OMOP_Dataset(address_drop, address_col=args.address_col)

    # perform parsing with usaddress library
    OMOP_address = usaddress_parse(OMOP_df)
    OMOP_address = OMOP_clean(OMOP_address)

    # filter failed address parsing
    OMOP_address["state_abbr"] = OMOP_address["state_abbr"].astype(str)
    OMOP_state_failed = OMOP_address.loc[OMOP_address.state_abbr.str.len() > 2]

    failed_address_parsed = custom_parser(
        df=OMOP_state_failed,
        address_col=args.address_col,
        state_full_pattern=state_full_pattern,
        state_abbr_pattern=state_abbr_pattern,
    )

    # replace full state names for failed_address_parsed
    failed_address_parsed["state_abbr"] = failed_address_parsed.state.apply(
        lambda x: multipleReplace(str(x).strip(), us_state_to_abbrev)
    )

    # update OMOP_location with addresses parsed with custom parser
    OMOP_address_updated = failed_address_parsed.combine_first(OMOP_address)

    # data quality flag for final set of parsed addresses
    OMOP_address_updated["flag"] = OMOP_address_updated.apply(
        lambda x: custom_flag(x), axis=1
    )

    save_dir = os.path.join(abs_path, args.output_dir)
    OMOP_address_updated.to_csv(save_dir, index=False)


if __name__ == "__main__":
    main()
    print("Address parsing completed")
