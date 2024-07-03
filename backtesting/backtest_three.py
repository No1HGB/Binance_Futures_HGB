import pandas as pd
from fetch import fetch_data
from calculate import calculate_ema, calculate_values, cal_resistance, cal_support
from entry_logic import (
    ha_long,
    ha_short,
    reverse_long,
    reverse_short,
    ha_trend_long,
    ha_trend_short,
)

# 초기값 설정
initial_capital = 1000
capital = initial_capital
margin = 0
leverage = 5
position = 0  # 포지션: 0 - 없음, 1 - 매수, -1 - 매도
entry_price = 0
take_profit_price = 0
stop_loss_price = 0

# 익절, 손절 조건 설정
take_profit_ratio = 0.02
stop_loss_ratio = 0.015

# 백테스트 결과를 저장할 변수 초기화
win_count = 0
loss_count = 0

df: pd.DataFrame = fetch_data(symbol="BTCUSDT", interval="1h", numbers=1200)
df["EMA10"] = calculate_ema(df, 10)
df["EMA20"] = calculate_ema(df, 20)
df["EMA50"] = calculate_ema(df, 50)
df = calculate_values(df)

# 백테스트 실행
for i in range(51, len(df)):
    if capital <= 0:
        break

    h_long = ha_long(df, i, 1.4)
    h_short = ha_short(df, i, 1.4)
    h_t_long = ha_trend_long(df, i, 1.4)
    h_t_short = ha_trend_short(df, i, 1.4)

    if position == 1:
        current_price = df.at[i, "close"]

        if stop_loss_price >= df.at[i, "low"] and stop_loss_price <= df.at[i, "high"]:
            loss = margin * leverage * stop_loss_ratio

            capital -= loss
            loss_count += 1
            margin = 0
            position = 0

        elif (
            take_profit_price >= df.at[i, "low"]
            and take_profit_price <= df.at[i, "high"]
        ):
            profit = (
                margin * leverage * abs(take_profit_price - entry_price) / entry_price
            )

            capital += profit
            win_count += 1
            margin = 0
            position = 0

        elif h_short or h_t_short:
            profit_loss = (
                margin * leverage * (current_price - entry_price) / entry_price
            )

            if profit_loss > 0:
                capital += profit_loss
                win_count += 1
                margin = 0
                position = 0
            else:
                capital += profit_loss
                loss_count += 1
                margin = 0
                position = 0

    elif position == -1:
        current_price = df.at[i, "close"]

        if stop_loss_price >= df.at[i, "low"] and stop_loss_price <= df.at[i, "high"]:
            loss = margin * leverage * stop_loss_ratio

            capital -= loss
            loss_count += 1
            margin = 0
            position = 0

        elif (
            take_profit_price >= df.at[i, "low"]
            and take_profit_price <= df.at[i, "high"]
        ):
            profit = (
                margin * leverage * abs(take_profit_price - entry_price) / entry_price
            )

            capital += profit
            win_count += 1
            margin = 0
            position = 0

        elif h_long or h_t_long:
            profit_loss = (
                margin * leverage * (entry_price - current_price) / entry_price
            )

            if profit_loss > 0:
                capital += profit_loss
                win_count += 1
                margin = 0
                position = 0
            else:
                capital += profit_loss
                loss_count += 1
                margin = 0
                position = 0

    if position == 0:  # 포지션이 없다면
        if h_long or h_t_long:

            position = 1
            margin = capital / 4
            capital -= margin * leverage * (0.1 / 100)
            entry_price = df.at[i, "close"]

            # 손절가 설정
            stop_loss_price = entry_price * (1 - stop_loss_ratio)

            # 익절가 설정
            df_tail = df.iloc[i - 150 : i]
            resistance = cal_resistance(df_tail)
            if resistance >= entry_price * (1 + 0.01):
                take_profit_price = resistance * (1 - 0.001)
            else:
                take_profit_price = entry_price * (1 + take_profit_ratio)

        elif h_short or h_t_short:

            position = -1
            margin = capital / 4
            capital -= margin * leverage * (0.1 / 100)
            entry_price = df.at[i, "close"]

            # 손절가 설정
            stop_loss_price = entry_price * (1 + stop_loss_ratio)

            # 익절가 설정
            df_tail = df.iloc[i - 150 : i]
            support = cal_support(df_tail)
            if support <= entry_price * (1 - 0.01):
                take_profit_price = support * (1 + 0.001)
            else:
                take_profit_price = entry_price * (1 - take_profit_ratio)


# 백테스트 결과 계산
total_trades = win_count + loss_count
win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
final_capital = capital

# 결과 출력
print(f"Total Trades: {total_trades}")
print(f"Wins: {win_count}")
print(f"Losses: {loss_count}")
print(f"Win Rate: {win_rate:.2f}%")
print(f"Final Capital: {final_capital:.2f}")
