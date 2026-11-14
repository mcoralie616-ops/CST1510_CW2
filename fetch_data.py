"""fetches earthquake data form the APi"""

import requests 
import pandas as pd 
from pathlib import Path
URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
PARAMS ={'format':'geojson','minmagnitude':'2.5','limit':'500'}
RECORDS_KEY="features"
RAW_FILE=Path("raw.csv")

def get_data(URL,PARAMS):
    """""Ask the API for data. Returns the JSON reply, or None if something went wrong."""
    try:
        response = requests.get(URL,params=PARAMS,timeout=15)
        response.raise_for_status
        return(response.json())
    except requests.RequestsException as error:
        print("Could not get the data",error)
        return None
    
def make_table(data,RECORDS_KEY):
    """Turn the JSON reply into a pandas table"""
    records = data[RECORDS_KEY] if RECORDS_KEY else data
    table=pd.json_normalize(records,sep="_")
    return table


def tidy_data(df):
    """Rename, keep and clean the columns"""
    RENAME = {
        "properties_mag": "mag",
        "properties_place": "place",
        "properties_time": "time"
    }
    KEEP = ["time", "place", "mag"]
    MUST_HAVE = ["mag"]

    df =df.rename(columns=RENAME)
    df = df[KEEP]
    df = df.dropna(subset=MUST_HAVE)
    return df

def save_data(df,path):
    """Save the table as a CSV file"""
    path.parent.mkdir(exist_ok=True)
    df.to_csv(path,index=False)
    print(f"Saved {len(df)} rows to {path}")

if __name__ == "__main__":
    data = get_data(URL,PARAMS)
    if data is not None:
        table = make_table(data,RECORDS_KEY)
        table = tidy_data(table)
        print(table.head())
        save_data(table,RAW_FILE)

    