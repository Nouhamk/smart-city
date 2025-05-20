import requests

from backend.app.mapping.openmeteo_mapping import convert_to_df

latitude = 40.7128  # Example: Latitude for New York City
longitude = -74.0060  # Example: Longitude for New York City
start_date = "2025-02-20"
end_date = "2025-03-01"
metrics = "temperature_2m,relative_humidity_2m"

url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly={metrics}"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    df_data = convert_to_df(data)
    df_data.to_csv('./csv/openmeteo.csv', index=False)

else:
    print("Error:", response.status_code, response.text)

