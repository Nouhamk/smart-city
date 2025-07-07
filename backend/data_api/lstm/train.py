import random
from math import ceil

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt

from backend.data_api.lstm.model import LSTMModel

NUMBER_EPOCHS = 20
BASE_MODEL_PATH = 'C:/Users/Tristan/Desktop/TAF/smart-city/backend/models'


def train_ai(X, y, metric, plot=False):
    X = X[ceil(len(X) * 0.9):]
    y = y[ceil(len(y) * 0.9):]
    global LAST_EPOCH_RESULT

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

        # Epoch prediction logging
        model.eval()
        with torch.no_grad():
            index = random.randint(0, len(y_tensor) - 1)
            index2 = random.randint(0, len(y_tensor) - 1)
            index3 = random.randint(0, len(y_tensor) - 1)
            pred = model(x_tensor[index].unsqueeze(0)).item()
            pred2 = model(x_tensor[index2].unsqueeze(0)).item()
            pred3 = model(x_tensor[index3].unsqueeze(0)).item()
            print(f"Epoch {epoch + 1} - Loss: {avg_loss:.4f} | MAE: {avg_mae:.4f} | Predicted: {pred:.2f} | Expected: {y_tensor[index].item():.2f}")
            print(f"Epoch {epoch + 1} - Loss: {avg_loss:.4f} | MAE: {avg_mae:.4f} | Predicted: {pred2:.2f} | Expected: {y_tensor[index2].item():.2f}")
            print(f"Epoch {epoch + 1} - Loss: {avg_loss:.4f} | MAE: {avg_mae:.4f} | Predicted: {pred3:.2f} | Expected: {y_tensor[index3].item():.2f}")

    # Save model
    torch.save(model, f"{BASE_MODEL_PATH}/{metric}.pt")

    if plot:
        plot_model_training(epoch_losses, epoch_maes, best_epoch)

    return


def plot_model_training(epoch_losses, epoch_maes, best_epoch):
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


# train_ai('temperature_2m')
