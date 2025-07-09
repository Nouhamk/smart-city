from datetime import datetime
from functools import reduce
from itertools import pairwise

import numpy as np

from data_api.data.data import get_data_common
from data_api.lstm.train import train_ai
from data_api.mapping.metrics import get_all_metrics

PACKET_SIZE = 8

def preprocess_train_data(data, metric):
    exclusion_list = ["time", "region_id", "region"]
    sorted_data = sorted(data, key=lambda x: (x["region_id"], x["time"]))
    index_metric = list(filter(
        lambda x: x not in exclusion_list,
        data[0].keys()
    )).index(metric)

    features_data = [
        [
            *[value for key, value in row.items() if key not in exclusion_list]
        ]
        for row in sorted_data
    ]

    diff_indexes = [0] + [
        index
        for (index, (left, right)) in enumerate(pairwise(sorted_data))
        if left["region_id"] != right["region_id"]
    ] + [len(sorted_data) - 1]

    regions_index_tuple = [(left, right - PACKET_SIZE) for (left, right) in pairwise(diff_indexes)]

    features_data_no_cross_region = reduce(lambda x, y: x + y, [features_data[left:right] for left, right in regions_index_tuple])

    transformed_data_packets = [
        np.array(features_data_no_cross_region[index_left: index_left + (PACKET_SIZE + 1)])
        for index_left in range(len(features_data_no_cross_region) - (PACKET_SIZE + 1))
    ]

    transformed_data_normalized = [min_max_normalize(data) for data in transformed_data_packets]

    X, _ = np.split(np.array(transformed_data_normalized), [PACKET_SIZE], axis=1)
    _, y = np.split(np.array(transformed_data_packets), [PACKET_SIZE], axis=1)

    y = y[:,:,index_metric]

    return X, y

def min_max_normalize(arr):
    min_vals = arr.min(axis=0)
    max_vals = arr.max(axis=0)
    return (arr - min_vals) / (max_vals - min_vals + 1e-8)

def train_all_models():
    all_metrics = get_all_metrics()
    data_train = get_data_common()
    for metric in all_metrics[0:1]:
        X, y = preprocess_train_data(data_train, metric)
        train_ai(X, y, metric)

# train_all_models()