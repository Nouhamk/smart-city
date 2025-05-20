import csv
import io
import logging
from pathlib import Path
from app.supabase_client import supabase

from app.mapping.openmeteo_mapping import openmeteo_mapping_attributes

logger = logging.getLogger(__name__)

def import_openmeteo_data():
    """
    Cron job to import data from csv/openmeteo.csv to Supabase table.
    Runs every hour and only imports new or updated records.
    """
    try:
        table_name = 'normalized_data'

        # CSV reading
        base_dir = Path(__file__).resolve().parent
        csv_path = base_dir / 'csv' / 'openmeteo.csv'
        if not csv_path.exists():
            logger.error(f"CSV file not found at: {csv_path}")
            return
        with open(csv_path, 'r', encoding='utf-8') as file:
            file_data = file.read()

        csv_data = csv.DictReader(io.StringIO(file_data))


        # Check for the latest timestamp in the database to avoid duplicates
        timestamp_field = 'time'
        try:
            response = supabase.table(table_name).select(timestamp_field).order(timestamp_field, desc=True).limit(1).execute()
            latest_timestamp = None
            if response.data and len(response.data) > 0:
                latest_timestamp = response.data[0].get(timestamp_field)
                logger.info(f"Latest timestamp in database: {latest_timestamp}")
        except Exception as e:
            latest_timestamp = None
            logger.warning(f"Could not get latest timestamp: {e}")


        # Convert CSV data to a list of dictionaries with mapped column names
        rows = []
        for row in csv_data:
            # Skip rows with older timestamps
            if latest_timestamp and timestamp_field in row:
                if row[timestamp_field] <= latest_timestamp:
                    continue

            # Apply mapping to column names based on openmeteo_mapping_attributes
            processed_row = {}
            for key, value in row.items():
                # If key exists in mapping, use mapped name, otherwise keep original
                if key in openmeteo_mapping_attributes:
                    mapped_key = openmeteo_mapping_attributes[key]
                else:
                    mapped_key = key

                # Convert empty strings to None
                processed_row[mapped_key] = value if value != '' else None

            rows.append(processed_row)

        if not rows:
            logger.info("No new data to import")
            return

        # Insert data into Supabase table
        response = supabase.table(table_name).insert(rows).execute()

        logger.info(f"Successfully uploaded {len(rows)} rows to {table_name}")

        return True

    except Exception as e:
        logger.error(f"Error importing OpenMeteo data: {str(e)}", exc_info=True)
        return False