import pandas as pd

openmeteo_to_common_mapping = {
    "temperature_2m": "temperature",
    "apparent_temperature": "apparent_temperature",
    "relative_humidity_2m": "humidity",
    "dewpoint_2m": "dewpoint",
    "precipitation_probability": "precipitation_probability",
    "precipitation": "precipitation",
    "snowfall": "snow",
    "snow_depth": "snow depth",
    "wind_gusts_10m": "wind_gust",
    "wind_speed_10m": "wind_speed",
    "wind_direction_10m": "wind_direction",
    "surface_pressure": "pressure",
    "visibility": "visibility",
    "cloud_cover": "cloudcover"
}

common_to_openmeteo_mapping = {v: k for k, v in openmeteo_to_common_mapping.items()}



def map_to_common_data(openmeteo_data):
    common_data = {}
    common_data["latitude"] = openmeteo_data["latitude"]
    common_data["longitude"] = openmeteo_data["longitude"]
    common_data["unit"] = openmeteo_data["hourly_units"]["temperature_2m"]
    common_data["data"] = [
        {
            "time": openmeteo_data["hourly"]["time"][index],
            "data": {
                openmeteo_mapping_attributes[key]:
                    value[index] for key, value in filter(lambda x: x[0] != "time", openmeteo_data["hourly"].items())
            }
        }
        for index in range(len(openmeteo_data["hourly"]["time"]))
    ]

    return common_data


def convert_to_df(openmeteo_data):
    df = pd.DataFrame(openmeteo_data["hourly"])
    df['time'] = pd.to_datetime(df['time'])
    return df

print(openmeteo_mapping_attributes)