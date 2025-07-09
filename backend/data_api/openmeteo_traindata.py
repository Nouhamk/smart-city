import requests

from data_api.lstm.model import train_ai
from data_api.mapping.openmeteo_mapping import convert_to_df

latitude = 40.7128  # Example: Latitude for New York City
longitude = -74.0060  # Example: Longitude for New York City
start_date = "2025-02-03"
end_date = "2025-04-23"
metrics = 'temperature_2m,apparent_temperature,relative_humidity_2m,dewpoint_2m,precipitation_probability,' \
          'precipitation,snowfall,snow_depth,wind_gusts_10m,wind_speed_10m,wind_direction_10m,surface_pressure,' \
          'visibility,cloud_cover '

url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly={metrics}"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    df_data = convert_to_df(data)
    df_data.to_csv('./csv/openmeteo_traindata.csv', index=False)

    for metric in metrics:
        train_ai(metric)
else:
    print("Error:", response.status_code, response.text)

