# Due to memory constraints, we'll use a more memory-efficient approach for calculating the distances
# We will use the NearestNeighbors approach from scikit-learn
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

# 데이터 로드 및 정규화
data = pd.read_csv("backtesting/data/data.csv")
data.drop(columns="time", inplace=True)
scaler = MinMaxScaler()
data.replace([np.inf, -np.inf], np.nan, inplace=True)
data.fillna(data.mean(), inplace=True)
data_normalized = data.copy()
data_normalized[["delta", "volume_R", "up_tail", "down_tail"]] = scaler.fit_transform(
    data[["delta", "volume_R", "up_tail", "down_tail"]]
)


# Using NearestNeighbors to find the closest patterns
nbrs = NearestNeighbors(n_neighbors=2, algorithm="ball_tree").fit(
    data_normalized[["delta", "volume_R", "up_tail", "down_tail"]]
)
distances, indices = nbrs.kneighbors(
    data_normalized[["delta", "volume_R", "up_tail", "down_tail"]]
)

# Get the indices of the most similar past patterns for the last 5 entries
most_similar_indices = indices[-5:, 1]

# Predict the delta values for the next 5 periods based on the most similar past patterns
predicted_deltas = data.iloc[most_similar_indices]["delta"].tolist()
predicted_up_tails = data.iloc[most_similar_indices]["up_tail"].to_list()
predicted_down_tails = data.iloc[most_similar_indices]["down_tail"].to_list()

print("Predicted deltas for the next 5 periods:", predicted_deltas)
print("Predicted up tails for the next 5 periods:", predicted_up_tails)
print("Predicted down tails for the next 5 periods:", predicted_down_tails)
