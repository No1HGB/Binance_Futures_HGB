import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

# 데이터 로드 및 정규화
data = pd.read_csv("backtesting/data/data.csv")
data.drop(columns="time", inplace=True)
scaler = MinMaxScaler()
# data.replace([np.inf, -np.inf], np.nan, inplace=True)
# data.fillna(data.mean(), inplace=True)
data_normalized = data.copy()
data_normalized[
    [
        "delta",
        "volume_R",
        "delta1",
        "delta2",
        "delta3",
        "delta4",
        "delta5",
        "delta6",
        "delta7",
        "delta8",
        "delta9",
        "delta10",
        "delta11",
        "delta12",
        "delta13",
        "delta14",
        "delta15",
        "delta16",
        "delta17",
        "delta18",
        "delta19",
        "delta20",
        "delta21",
        "delta22",
        "delta23",
        "delta24",
        "EMA50_D",
        "EMA200_D",
    ]
] = scaler.fit_transform(
    data[
        [
            "delta",
            "volume_R",
            "delta1",
            "delta2",
            "delta3",
            "delta4",
            "delta5",
            "delta6",
            "delta7",
            "delta8",
            "delta9",
            "delta10",
            "delta11",
            "delta12",
            "delta13",
            "delta14",
            "delta15",
            "delta16",
            "delta17",
            "delta18",
            "delta19",
            "delta20",
            "delta21",
            "delta22",
            "delta23",
            "delta24",
            "EMA50_D",
            "EMA200_D",
        ]
    ]
)

# Using NearestNeighbors to find the closest patterns
nbrs = NearestNeighbors(n_neighbors=3, algorithm="ball_tree").fit(
    data_normalized[
        [
            "delta",
            "volume_R",
            "delta1",
            "delta2",
            "delta3",
            "delta4",
            "delta5",
            "delta6",
            "delta7",
            "delta8",
            "delta9",
            "delta10",
            "delta11",
            "delta12",
            "delta13",
            "delta14",
            "delta15",
            "delta16",
            "delta17",
            "delta18",
            "delta19",
            "delta20",
            "delta21",
            "delta22",
            "delta23",
            "delta24",
            "EMA50_D",
            "EMA200_D",
        ]
    ]
)

# 가장 마지막 데이터 포인트와 가장 가까운 5개의 포인트 찾기
last_point = (
    data_normalized[
        [
            "delta",
            "volume_R",
            "delta1",
            "delta2",
            "delta3",
            "delta4",
            "delta5",
            "delta6",
            "delta7",
            "delta8",
            "delta9",
            "delta10",
            "delta11",
            "delta12",
            "delta13",
            "delta14",
            "delta15",
            "delta16",
            "delta17",
            "delta18",
            "delta19",
            "delta20",
            "delta21",
            "delta22",
            "delta23",
            "delta24",
            "EMA50_D",
            "EMA200_D",
        ]
    ]
    .iloc[-1]
    .to_frame()
    .T
)

distances, indices = nbrs.kneighbors(last_point)

# Get the indices of the most similar past patterns for the last entry (excluding itself)
most_similar_indices = indices[0, 1:6]

# Predict the delta values for the next 5 periods based on the most similar past patterns
predicted_deltas = data.iloc[most_similar_indices]["delta"].tolist()

print("Predicted deltas for the next 5 periods:", predicted_deltas)
