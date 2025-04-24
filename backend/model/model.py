import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np


# Define the model
class LSTMModel(nn.Module):
    def __init__(self):
        super(LSTMModel, self).__init__()
        self.lstm1 = nn.LSTM(input_size=6, hidden_size=128, batch_first=True)
        self.lstm2 = nn.LSTM(input_size=128, hidden_size=128, batch_first=True)
        self.fc1 = nn.Linear(128, 32)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(32, 16)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(16, 1)

    def forward(self, x):
        x, _ = self.lstm1(x)
        x, _ = self.lstm2(x)
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x


def train_ai(data_training, prediction_hour):
    global LAST_EPOCH_RESULT

    X, y = data_training.keys(), data_training.values()
    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)

    dataset = TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    model = LSTMModel()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    input_seq = torch.tensor(np.array(input_sequence), dtype=torch.float32)

    for epoch in range(NUMBER_EPOCHS):
        model.train()
        for xb, yb in dataloader:
            optimizer.zero_grad()
            output = model(xb)
            loss = criterion(output, yb)
            loss.backward()
            optimizer.step()

        # Prediction callback
        model.eval()
        with torch.no_grad():
            pred = model(input_seq)
            print(f"Epoch {epoch + 1} - Predicted Lux: {pred[0, -1, 0].item()}")
            if epoch + 1 == NUMBER_EPOCHS:
                LAST_EPOCH_RESULT = pred[:, -1, :].numpy()
                print(LAST_EPOCH_RESULT)

    torch.save(model.state_dict(), MODEL_PATH)
    return LAST_EPOCH_RESULT
