import pandas as pd

visualcrossing_to_common_mapping = {
    "temp": "temperature",
    "feelslike": "apparent_temperature",
    "humidity": "humidity",
    "dew": "dew_point",
    "Precipitation Probability": "precipitation_probability",
    "Precipitation (rain + showers + snow)": "precipitation",
    "snow": "snow",
    "snowdepth": "snow_depth",
    "windgust": "wind_gust",
    "windspeed": "wind_speed",
    "winddir": "wind_direction",
    "pressure": "pressure",
    "visibility": "visibility",
    "cloud_cover": "cloud_cover"
}

common_to_visualcrossing_mapping = {v: k for k, v in visualcrossing_to_common_mapping.items()}

def map_to_common_data(visualcrossing_data):
    common_data = {}
    common_data["latitude"] = visualcrossing_data["latitude"]
    common_data["longitude"] = visualcrossing_data["longitude"]
    common_data["unit"] = None #!!
    common_data["data"] = [
        {
            "time": visualcrossing_data["days"][index]["datetime"],
            "data": {
                visualcrossing_to_common_mapping[key]:
                    value[index] for key, value in filter(lambda x: x[0] != "datetime", visualcrossing_data["days"][index].items())
            }
        }
        for index in range(len(visualcrossing_data["days"]))
    ]

    return common_data


def convert_to_df(visualcrossing_data):
    pass
    # df = pd.DataFrame(visualcrossing_data)
    # df['time'] = pd.to_datetime(df['time'])
    # return df

