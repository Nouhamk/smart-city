import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

OUTBOUND_RATIO = 1.75
def remove_outliers(df):
    def remove_outliner(df, column):
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - OUTBOUND_RATIO * IQR
        upper_bound = Q3 + OUTBOUND_RATIO * IQR
        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

    for column in df.columns:
        df = remove_outliner(df, column)

# Remove outliers from each column


