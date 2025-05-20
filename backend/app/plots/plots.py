import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def draw_box_plot(dataframe):
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=dataframe)
    plt.title('Box Plot of Weather Metrics')
    plt.show()