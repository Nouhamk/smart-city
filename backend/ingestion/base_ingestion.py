from datetime import datetime, date

from backend.ingestion.cities_ingestion import save_cities_to_supabase, get_all_regions
from backend.mapping.metrics import get_all_metrics
from backend.openmeteo import get_openmeteo_data
from backend.supabase.database import save_normalized_data, load_regions
from backend.visualcrossing import get_visualcrossing_data

START_DATE_INGESTION = '2025-03-01'
END_DATE_INGESTION = '2025-05-23'

def ingest_all_available_cities():
    save_cities_to_supabase()

def ingestion(ingest_cities=False, fixed_end_date=False):
    if ingest_cities:
        ingest_all_available_cities()

    all_metrics = get_all_metrics()
    all_regions = load_regions()
    start_date = START_DATE_INGESTION
    end_date = END_DATE_INGESTION if fixed_end_date else date.today()

    all_data = []

    for region in all_regions:
        openmeteo_dataframe = get_openmeteo_data(region, all_metrics, start_date, end_date)
        openmeteo_data = openmeteo_dataframe.to_dict('records')
        # visualcrossing_data = get_visualcrossing_data(region, all_metrics, start_date, end_date)

        # faire fonction qui join les deux sources
        harmonized_data = openmeteo_data

        all_data += harmonized_data

    save_normalized_data(all_data)


ingestion()