import os
from datetime import date, datetime, timedelta

import torch

from data_api.data.data import get_data_common
from data_api.lstm.train_all_models import PACKET_SIZE, preprocess_train_data
from data_api.mapping.metrics import get_all_metrics
from data_api.supabase.database import load_regions, get_latest_timestamp_by_cities, merge_upsert_prediction

from data_api.supabase.database import load_normalized_data

PREDICTION_METRICS = ["temperature"]

def write_predictions():
    all_metrics = get_all_metrics()
    all_regions = load_regions()
    latest_timestamp_by_cities = get_latest_timestamp_by_cities()

    for metric in PREDICTION_METRICS:
        model = torch.load(f'./../../data_api/models/{metric}.pt')

        for region in all_regions:
            latest_timestamp = next(filter(
                lambda x: x["region_id"] == region["id"],
                latest_timestamp_by_cities
            ), None)["latest_time"]


            prediction_timestamp = (datetime.fromisoformat(latest_timestamp) + timedelta(hours=1)).isoformat()

            known_data = sorted(
                get_data_common([region["name"]], None, None,  None),
                key=lambda x: x["time"],
            )
            known_data = known_data + [known_data[len(known_data) - 1]]
            preprocessed_data, _ = preprocess_train_data(known_data, metric)
            x_prediction = preprocessed_data[len(preprocessed_data) - 1]

            y_prediction = model(torch.tensor(x_prediction, dtype=torch.float32).unsqueeze(0)).item()

            prediction = {
                "time": prediction_timestamp,
                "region_id": region["id"],
                metric: y_prediction
            }

            merge_upsert_prediction(prediction)




write_predictions()