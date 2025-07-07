import numpy as np
import torch
from matplotlib import pyplot as plt

from backend.api.routes import get_data_common
from backend.lstm.train import train_ai
from backend.lstm.train_all_models import preprocess_train_data
from backend.mapping.metrics import get_all_metrics

metric = "humidity"
NBR_ROW_TRAIN = 1000
NBR_ROW_CHECK = 100

def check_model():
    data_train = get_data_common()
    x_train, y_train = preprocess_train_data(data_train, metric)[:NBR_ROW_TRAIN + NBR_ROW_CHECK]
    ((x_train, y_train), (x_checks, y_checks)) = (
        (x_train[-NBR_ROW_TRAIN:-NBR_ROW_CHECK], y_train[-NBR_ROW_TRAIN:-NBR_ROW_CHECK]),
        (x_train[-NBR_ROW_CHECK:], y_train[-NBR_ROW_CHECK:])
    )
    # train_ai(x_train, y_train, metric)

    model = torch.load(f'C:/Users/Tristan/Desktop/TAF/smart-city/backend/models/{metric}.pt')

    checks_expected = y_checks
    checks_actual = []
    for x_check in torch.from_numpy(x_checks.astype(np.float32)):
        check_actual = model(x_check.unsqueeze(0)).item()
        checks_actual.append(check_actual)

    plt.plot(checks_expected, label='Expected', marker='o')
    plt.plot(np.array(checks_actual), label='Actual', marker='x')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Comparison of Expected vs Actual')
    plt.legend()
    plt.grid(True)
    plt.show()

check_model()