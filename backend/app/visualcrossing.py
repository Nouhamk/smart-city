import requests

from backend.app.mapping.visualcrossing_mapping import map_to_common_data

api_key = "85b2d49aeced8fb9fe7d3e6a8aa8c2c6"
location = "New York,NY"
start_date = "2024-02-28"
end_date = "2024-03-01"
metrics = "temp,humidity"

url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{start_date}/{end_date}?include=hours&key={api_key}&elements={metrics}"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(map_to_common_data(data))
else:
    print("Error:", response.status_code, response.text)
