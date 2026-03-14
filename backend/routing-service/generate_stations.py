import pandas as pd
import json
import logging
import re
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXCEL_PATH = "../../BUS DE CONSTANTINE.xlsx"
OUTPUT_PATH = "stations.json"

def slugify(text):
    if pd.isna(text):
        return ""
    text = str(text).upper()
    text = re.sub(r'[^A-Z0-9]+', '_', text)
    return text.strip('_')

def parse_coords(coord_str):
    if pd.isna(coord_str):
        return None, None
    parts = str(coord_str).split(',')
    if len(parts) == 2:
        try:
            return float(parts[0].strip()), float(parts[1].strip())
        except ValueError:
            pass
    return None, None

def generate_stations():
    logger.info(f"Loading data from {EXCEL_PATH}...")
    df = pd.read_excel(EXCEL_PATH)
    
    stations = {}
    
    for index, row in df.iterrows():
        # Process departure stop
        dep_name = row['Depart']
        dep_id = slugify(dep_name)
        dep_lat, dep_lon = parse_coords(row['Localisation'])
        
        if dep_id and dep_lat and dep_lon:
            if dep_id not in stations:
                stations[dep_id] = {'id': dep_id, 'name': dep_name.strip(), 'lat': dep_lat, 'lon': dep_lon}
                
        # Process arrival stop
        arr_name = row['Arrive']
        arr_id = slugify(arr_name)
        arr_lat, arr_lon = parse_coords(row['Localisation.1'])
        
        if arr_id and arr_lat and arr_lon:
            if arr_id not in stations:
                stations[arr_id] = {'id': arr_id, 'name': arr_name.strip(), 'lat': arr_lat, 'lon': arr_lon}

    station_list = list(stations.values())
    
    logger.info(f"Extracted {len(station_list)} unique stations.")
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(station_list, f, indent=2)
        
    logger.info(f"Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_stations()
