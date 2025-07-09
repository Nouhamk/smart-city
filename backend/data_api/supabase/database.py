from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Region functions
def save_cities(data):
    response = supabase.table("region") \
        .upsert(data, on_conflict="name") \
        .execute()
    print(response)

def load_regions():
    response = supabase.table("region").select("*").execute()
    return response.data

# Normalized data functions
def save_normalized_data(data):
    supabase.table("normalized_data") \
        .upsert(data, on_conflict="time, region_id") \
        .execute()

def load_normalized_data(start_time, end_time, regions, metrics):
    regions_lowered = list(map(lambda region: region.lower(), regions))

    response = (
        supabase
        .table("normalized_data")
        .select(",".join(["time", "region_id", "region(name)"] + metrics))
        .gte("time", start_time)
        .lte("time", end_time)
        .in_("region.name", regions_lowered)
        .execute()
    )
    return list(filter(lambda x: x["region"] is not None, response.data))

def load_predictions(start_time, regions, metrics):
    regions_lowered = list(map(lambda region: region.lower(), regions))

    response = (
        supabase
        .table("predictions")
        .select(",".join(["time", "region_id", "region(name)"] + metrics))
        .gte("time", start_time)
        .in_("region.name", regions_lowered)
        .execute()
    )
    return list(filter(lambda x: x["region"] is not None, response.data))

def get_latest_timestamp_by_cities():
    response = supabase.rpc("get_latest_time_by_region_id").execute()
    return response.data

def merge_upsert_prediction(prediction_row):
    prediction_from_timestamp = load_prediction_from_timestamp(prediction_row["time"])
    if not prediction_from_timestamp:
        supabase.table("predictions") \
            .insert([prediction_row]) \
            .execute()
        return

    metric = next(filter(lambda x: x != "time", list(prediction_row.keys())), None)
    prediction_from_timestamp[metric] = prediction_row[metric]
    supabase.table("predictions") \
        .upsert([prediction_row], on_conflict="time, region_id") \
        .execute()


def load_prediction_from_timestamp(timestamp):
    response = (
        supabase.table("predictions")
        .select("*")
        .eq("time", timestamp)
        .execute()
    )

    return next(iter(response.data), None)