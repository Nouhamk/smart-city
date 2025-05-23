from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def save_cities(data):
    response = supabase.table("region") \
        .upsert(data, on_conflict="name") \
        .execute()

    print(response)

def load_regions():
    response = supabase.table("region").select("*").execute()
    return response.data

def save_normalized_data(data):
    supabase.table("normalized_data") \
        .upsert(data, on_conflict="time, region_id") \
        .execute()


def load_normalized_data(region_name, metrics, start_time, end_time):
    response = (
        supabase
        .table("normalized_data")
        .select(",".join(metrics + ["region(name)"]))  # Pas de join en supabase on réference direct la table
        .gte("time", start_time)
        .lte("time", end_time)
        .ilike("region.name", region_name.lower())
        .execute()
    )

    return response.data


def get_latest_timestamp():
    response = (
        supabase
        .table("normalized_data")
        .select("time")
        .order("time", desc=True)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]["time"]
    else:
        return None

