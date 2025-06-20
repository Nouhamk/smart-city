from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def save_normalized_data(data):
    supabase.table("normalized_data") \
        .upsert(data, on_conflict="timestamp, region_id") \
        .execute()


def load_normalized_data(region_name, metrics, start_time, end_time):
    response = (
        supabase
        .table("normalized_data")
        .select(",".join(metrics + ["region(name)"]))  # Pas de join en supabase on réference direct la table
        .gte("timestamp", start_time)
        .lte("timestamp", end_time)
        .ilike("region.name", region_name.lower())
        .execute()
    )

    return response.data


def get_latest_timestamp():
    response = (
        supabase
        .table("normalized_data")
        .select("timestamp")
        .order("timestamp", desc=True)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]["timestamp"]
    else:
        return None

