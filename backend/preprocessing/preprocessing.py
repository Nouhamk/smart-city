
GROUP_SIZE = 6
def preprocess_data():
    pass

def get_training_data(pandas_df, column_to_predict):
    collected_data = pandas_df.to_dict(orient='records')
    training_data = {collected_data[i]["time"]: collected_data[i][column_to_predict] for i in range(GROUP_SIZE)}
    return training_data