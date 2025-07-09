import numpy as np
import torch
from matplotlib import pyplot as plt

from data_api.data.data import get_data_common
from data_api.lstm.train_all_models import preprocess_train_data

metric = "humidity"
NBR_ROW_TRAIN = 1000
NBR_ROW_CHECK = 100

def check_model():
    data_train = get_data_common(regions=["paris"])
    x, y = preprocess_train_data(data_train, metric)[:NBR_ROW_TRAIN + NBR_ROW_CHECK]
    ((x_train, y_train), (x_checks, y_checks)) = (
        (x[-NBR_ROW_TRAIN:-NBR_ROW_CHECK], y[-NBR_ROW_TRAIN:-NBR_ROW_CHECK]),
        (x[-NBR_ROW_CHECK:], y[-NBR_ROW_CHECK:])
    )
    # train_ai(x_train, y_train, metric)

    model = torch.load(f'./data_api/models/{metric}.pt')

    checks_expected = y_checks
    checks_actual = []
    for x_check in torch.from_numpy(x_checks.astype(np.float32)):
        check_actual = model(x_check.unsqueeze(0)).item()
        checks_actual.append(check_actual)

    plt.plot(checks_expected, label='Expected', marker='o')
    plt.plot(np.array(checks_actual), label='Actual', marker='x')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title(f'Comparison of Expected {metric} vs Actual {metric}')
    plt.legend()
    plt.grid(True)
    plt.show()

# check_model()