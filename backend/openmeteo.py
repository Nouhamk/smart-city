import requests

from backend.mapping.openmeteo_mapping import map_to_common_data, convert_to_df

def get_openmeteo_data(region_name, metrics, start_time, end_time):
    longitude, latitude = get_coordonates(region_name)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_time}&end_date={end_time}&hourly={metrics}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

