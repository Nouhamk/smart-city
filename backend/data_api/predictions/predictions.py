from datetime import date

from data_api.mapping.metrics import get_all_metrics
from data_api.supabase.database import load_regions, get_latest_timestamp_by_cities

from data_api.supabase.database import load_normalized_data

PREDICTION_METRICS = ["temperature", "humidity"]

def write_predictions():
    all_metrics = get_all_metrics()
    all_regions = load_regions()
    latest_timestamp_by_cities = get_latest_timestamp_by_cities()

    end_date = date.today()

    for region in all_regions:
        start_time_predictions = list(filter(
            lambda x: x["region_id"] == region["id"],
            latest_timestamp_by_cities
        ))[0]["latest_time"][:10]

        start_time_data_training = load_normalized_data(start_time_predictions, end_date, [region], PREDICTION_METRICS)
        print(start_time_data_training)

write_predictions()