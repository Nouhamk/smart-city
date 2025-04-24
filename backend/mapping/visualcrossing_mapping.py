import pandas as pd


visualcrossing_mapping_attributes = {
    "temp": "temperature",
    "feelslike": "apparent_temperature",
    "humidity": "humidity",
    "dew": "dewpoint",
    "Precipitation Probability": "precipprob",
    "Precipitation (rain + showers + snow)": "precip",
    "snow": "snow",
    "snowdepth": "snow depth",
    "windgust": "wind_gust",
    "windspeed": "wind_speed",
    "winddir": "wind_direction",
    "pressure": "pressure",
    "visibility": "visibility",
    "cloudcover": "cloudcover"
}

def map_to_common_data(visualcrossing_data):
    common_data = {}
    common_data["latitude"] = visualcrossing_data["latitude"]
    common_data["longitude"] = visualcrossing_data["longitude"]
    common_data["unit"] = None #!!
    common_data["data"] = [
        {
            "time": visualcrossing_data["days"][index]["datetime"],
            "data": {
                visualcrossing_mapping_attributes[key]: 
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

