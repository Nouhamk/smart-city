import pandas as pd

from data_api.mapping.common import list_to_string_api

openmeteo_to_common_mapping = {
    "temperature_2m": "temperature",
    "apparent_temperature": "apparent_temperature",
    "relative_humidity_2m": "humidity",
    "dewpoint_2m": "dew_point",
    "precipitation_probability": "precipitation_probability",
    "precipitation": "precipitation",
    "snowfall": "snow",
    "snow_depth": "snow_depth",
    "wind_gusts_10m": "wind_gust",
    "wind_speed_10m": "wind_speed",
    "wind_direction_10m": "wind_direction",
    "surface_pressure": "pressure",
    "visibility": "visibility",
    "cloud_cover": "cloud_cover"
}

common_to_openmeteo_mapping = {v: k for k, v in openmeteo_to_common_mapping.items()}

def get_common_to_openmeteo_mapping():
    return common_to_openmeteo_mapping

def convert_common_metrics_to_api_string(metrics):
    return list_to_string_api([get_common_to_openmeteo_mapping()[metric] for metric in metrics])

def map_to_common_data(openmeteo_data):
    common_data = {}
    common_data["latitude"] = openmeteo_data["latitude"]
    common_data["longitude"] = openmeteo_data["longitude"]
    common_data["unit"] = openmeteo_data["hourly_units"]["temperature_2m"]
    common_data["data"] = [
        {
            "time": openmeteo_data["hourly"]["time"][index],
            "data": {
                openmeteo_to_common_mapping[key]:
                    value[index] for key, value in filter(lambda x: x[0] != "time", openmeteo_data["hourly"].items())
            }
        }
        for index in range(len(openmeteo_data["hourly"]["time"]))
    ]

    return common_data


def convert_to_harmonized_df(openmeteo_data, region):
    data = openmeteo_data["hourly"]
    harminzed_data = {common_metric: data[openmeteo_metric] for openmeteo_metric, common_metric in openmeteo_to_common_mapping.items()}

    df = pd.DataFrame(harminzed_data)
    df['time'] = data["time"]
    df['region_id'] = region["id"]
    return df