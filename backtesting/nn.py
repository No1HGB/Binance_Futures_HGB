import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

# 데이터 로드 및 정규화
data = pd.read_csv("backtesting/data/data.csv")
data.drop(columns="time", inplace=True)
data.drop(data.index[-51:], inplace=True)
print(data.iloc[-1]["delta"])
# scaler = MinMaxScaler()
data.replace([np.inf, -np.inf], np.nan, inplace=True)
data.fillna(data.mean(), inplace=True)
data_normalized = data.copy()
data_points = ["delta", "volume_R"] + [f"delta{i}" for i in range(1, 120)]
# data_normalized[data_points] = scaler.fit_transform(data[data_points])

# Using NearestNeighbors to find the closest patterns
nbrs = NearestNeighbors(n_neighbors=6, algorithm="ball_tree").fit(
    data_normalized[data_points]
)

last_point = data_normalized[data_points].iloc[-1].to_frame().T

distances, indices = nbrs.kneighbors(last_point)

most_similar_indices = indices[0, 1:6]

# 다음 인덱스의 delta 값을 도출 (원본 데이터 기준)
predicted_deltas = []
for idx in most_similar_indices:
    next_idx = idx + 1
    if next_idx < len(data):  # 다음 인덱스가 데이터 범위를 넘지 않는지 확인
        predicted_deltas.append(data.iloc[next_idx]["delta"])

print(distances)
print(most_similar_indices)
print("Predicted five deltas from next indices:", predicted_deltas)
