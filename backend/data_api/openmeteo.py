import requests

from data_api.mapping.openmeteo_mapping import convert_common_metrics_to_api_string, convert_to_harmonized_df


def get_openmeteo_data(region, metrics, start_date, end_date):
    latitude, longitude = region["latitude"], region["longitude"]
    openapi_metrics = convert_common_metrics_to_api_string(metrics)

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly={openapi_metrics}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        harmonized_dataframe = convert_to_harmonized_df(data, region)
        return harmonized_dataframe
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


