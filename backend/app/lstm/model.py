import pandas
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt

data = (pandas
    .read_csv("C:/Users/Tristan/Desktop/TAF/smart-city/backend/csv/openmeteo_traindata.csv")
    .to_dict(orient='records')
)

NUMBER_EPOCHS = 50
PACKET_SIZE = 12
BASE_MODEL_PATH = 'C:/Users/Tristan/Desktop/TAF/smart-city/backend/models'


# Define the model
class LSTMModel(nn.Module):
    def __init__(self):
        super(LSTMModel, self).__init__()
        self.lstm1 = nn.LSTM(input_size=14, hidden_size=128, batch_first=True)
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


def train_ai(metric):
    global LAST_EPOCH_RESULT

    X = [[
        list(data[i].values())[1::]
         for i in range(being_index, being_index + PACKET_SIZE)
        ]
        for being_index in range(len(data) - PACKET_SIZE)
    ]

    y = [data[i][metric] for i in range(PACKET_SIZE, len(data))]

    x_tensor = torch.tensor(X, dtype=torch.float32)  # [batch, seq_len, 1]
    y_tensor = torch.tensor(y, dtype=torch.float32) # [batch, 1]

    dataset = TensorDataset(x_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    model = LSTMModel()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Metrics tracking
    epoch_losses = []
    epoch_maes = []
    best_loss = float('inf')
    best_epoch = -1
    best_pred = None

    for epoch in range(NUMBER_EPOCHS):
        model.train()
        running_loss = 0.0
        running_mae = 0.0

        for xb, yb in dataloader:
            optimizer.zero_grad()
            output = model(xb)
            loss = criterion(output, yb)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            running_mae += torch.abs(output - yb).mean().item()

        avg_loss = running_loss / len(dataloader)
        avg_mae = running_mae / len(dataloader)
        epoch_losses.append(avg_loss)
        epoch_maes.append(avg_mae)

        # Save best epoch
        if avg_loss < best_loss:
            best_loss = avg_loss
            best_epoch = epoch + 1
            model.eval()
            with torch.no_grad():
                best_pred = model(x_tensor[-1].unsqueeze(0)).item()

        # Epoch prediction logging
        model.eval()
        with torch.no_grad():
            pred = model(x_tensor[-1].unsqueeze(0))
            print(
                f"Epoch {epoch + 1} - Loss: {avg_loss:.4f} | MAE: {avg_mae:.4f} | Predicted: {pred[0][0].item():.2f} | Expected: {y_tensor[-1].item():.2f}")
            if epoch + 1 == NUMBER_EPOCHS:
                LAST_EPOCH_RESULT = pred[0][0].item()

    # Save model
    torch.save(model.state_dict(), f"{BASE_MODEL_PATH}/{metric}.pt")

    # Plot metrics
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(epoch_losses, label='MSE Loss')
    plt.axvline(best_epoch - 1, color='red', linestyle='--', label='Best Epoch')
    plt.title('Loss per Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(epoch_maes, label='MAE')
    plt.axvline(best_epoch - 1, color='red', linestyle='--', label='Best Epoch')
    plt.title('MAE per Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('MAE')
    plt.legend()

    plt.tight_layout()
    plt.show()

    print(f"Prediction at Best Epoch: {best_pred:.2f}")

    return LAST_EPOCH_RESULT


train_ai('temperature_2m')
