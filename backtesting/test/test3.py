import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fetch import fetch_data
from calculate import calculate_values, cal_resistance, cal_support
import math


df = fetch_data("BTCUSDT", "1h", 1000)
df = calculate_values(df)

resistance = cal_resistance(df)
support = cal_support(df)
print(support)
