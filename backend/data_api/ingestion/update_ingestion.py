from datetime import date

from data_api.mapping.metrics import get_all_metrics
from data_api.openmeteo import get_openmeteo_data
from data_api.supabase.database import save_normalized_data, load_regions, get_latest_timestamp_by_cities


def update_ingestion(end_date = date.today()):
    all_metrics = get_all_metrics()
    all_regions = load_regions()
    latest_timestamp_by_cities = get_latest_timestamp_by_cities()

    all_data = []

    for region in all_regions:
        start_time = list(filter(
            lambda x: x["region_id"] == region["id"],
            latest_timestamp_by_cities
        ))[0]["latest_time"][:10]

        openmeteo_dataframe = get_openmeteo_data(region, all_metrics, start_time, end_date)
        openmeteo_data = openmeteo_dataframe.to_dict('records')
        # visualcrossing_data = get_visualcrossing_data(region, all_metrics, start_date, end_date)

        # faire fonction qui join les deux sources
        harmonized_data = openmeteo_data

        all_data += harmonized_data

    save_normalized_data(all_data)

# update_ingestion()