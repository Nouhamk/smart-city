import requests

api_key = "85b2d49aeced8fb9fe7d3e6a8aa8c2c6"

def get_visualcrossing_data(region_name, metrics, start_time, end_time):
    # longitude, latitude = get_coorindates(region_name)
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{region_name}/{start_time}/{end_time}?include=hours&key={api_key}&elements={metrics}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")



