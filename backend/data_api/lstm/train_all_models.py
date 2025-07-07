from datetime import datetime

from flatbuffers.number_types import np

from backend.data_api.routes import get_data_common
from backend.data_api.lstm.train import train_ai
from backend.data_api.mapping.metrics import get_all_metrics

PACKET_SIZE = 12

def preprocess_train_data(data, metric):
    distincts_regions = set(map(lambda x: x["region"]["name"], data))
    regions_as_double = list(enumerate(distincts_regions))
    metric_index = list(data[0].keys()).index(metric)

    transformed_data_grouped_by_region = [
        [
            [
                float(list(filter(lambda x: x[1] == row["region"]["name"], regions_as_double))[0][0]),
                datetime.fromisoformat(row["time"]).timestamp(),
                *[value for key, value in row.items() if key not in ["time", "region_id", "region"]]
            ]
            for row in list(filter(
                lambda x: x["region"]["name"] == region,
                data
            ))
        ]
        for region in distincts_regions
    ]

    transformed_data_packets = [
        np.array(transformed_data_one_region[index_left: index_left + (PACKET_SIZE + 1)])
        for transformed_data_one_region in transformed_data_grouped_by_region
        for index_left in range(len(transformed_data_one_region) - (PACKET_SIZE + 1))
    ]

    transformed_data_normalized = [min_max_normalize(data) for data in transformed_data_packets]

    X, _ = np.split(np.array(transformed_data_normalized), [PACKET_SIZE], axis=1)
    _, y = np.split(np.array(transformed_data_packets), [PACKET_SIZE], axis=1)

    y = y[:,:,metric_index]

    return X, y

def min_max_normalize(arr):
    min_vals = arr.min(axis=0)
    max_vals = arr.max(axis=0)
    return (arr - min_vals) / (max_vals - min_vals + 1e-8)

def train_all_models():
    all_metrics = get_all_metrics()
    data_train = get_data_common()
    for metric in all_metrics[6:]:
        X, y = preprocess_train_data(data_train, metric)
        train_ai(X, y, metric)

train_all_models()