import pandas as pd
from fetch import fetch_data
from calculate import calculate_ema, calculate_values
from entry_logic import (
    ha_reverse_long,
    ha_medium_long,
    ha_trend_long,
    ha_reverse_short,
    ha_medium_short,
    ha_trend_short,
)

# 초기 자금 설정
initial_capital = 1000
capital = initial_capital
margin = 0
leverage = 5
position = 0  # 포지션: 0 - 없음, 1 - 매수, -1 - 매도
entry_price = 0

# 익절, 손절 조건 설정 (비율)
stop_loss_ratio = 0.01

# 백테스트 결과를 저장할 변수 초기화
win_count = 0
loss_count = 0

volume_coff = 1.5

df: pd.DataFrame = fetch_data(symbol="BTCUSDT", interval="1h", numbers=8770)
df["EMA10"] = calculate_ema(df, 10)
df["EMA20"] = calculate_ema(df, 20)
df["EMA50"] = calculate_ema(df, 50)
df = calculate_values(df)

# 백테스트 실행
for i in range(70, len(df)):
    if capital <= 0:
        break

    h_r_long = ha_reverse_long(df, i, volume_coff)
    h_m_long = ha_medium_long(df, i, volume_coff)
    h_t_long = ha_trend_long(df, i, volume_coff)

    h_r_short = ha_reverse_short(df, i, volume_coff)
    h_m_short = ha_medium_short(df, i, volume_coff)
    h_t_short = ha_trend_short(df, i, volume_coff)

    if position == 1:
        # 스탑 로스
        stop_loss_price = entry_price * (1 - stop_loss_ratio)
        if stop_loss_price >= df.at[i, "low"]:
            loss = margin * leverage * stop_loss_ratio
            if entry_price < stop_loss_price:
                capital += loss
                win_count += 1
                margin = 0
                position = 0
            elif entry_price > stop_loss_price:
                capital -= loss
                loss_count += 1
                margin = 0
                position = 0

        # 숏 조건인 경우
        elif h_r_short:
            take_profit_ratio = abs(df.at[i, "close"] - entry_price) / entry_price
            profit = margin * leverage * take_profit_ratio
            if entry_price < df.at[i, "close"]:
                capital += profit
                win_count += 1
                margin = 0
                position = 0
            elif entry_price > df.at[i, "close"]:
                capital -= profit
                loss_count += 1
                margin = 0
                position = 0

        # 하이킨아시 역봉
        elif df.at[i, "ha_open"] > df.at[i, "ha_close"]:
            take_profit_ratio = abs(df.at[i, "close"] - entry_price) / entry_price
            profit = margin * leverage * take_profit_ratio
            if entry_price < df.at[i, "close"]:
                capital += profit
                win_count += 1
                margin = 0
                position = 0
            elif entry_price > df.at[i, "close"]:
                capital -= profit
                loss_count += 1
                margin = 0
                position = 0

    elif position == -1:
        # 스탑로스
        stop_loss_price = entry_price * (1 + stop_loss_ratio)
        if stop_loss_price <= df.at[i, "high"]:
            loss = margin * leverage * stop_loss_ratio
            if entry_price > stop_loss_price:
                capital += loss
                win_count += 1
                margin = 0
                position = 0
            elif entry_price < stop_loss_price:
                capital -= loss
                loss_count += 1
                margin = 0
                position = 0

        # 롱 조건인 경우
        elif h_r_long:
            take_profit_ratio = abs(df.at[i, "close"] - entry_price) / entry_price
            profit = margin * leverage * take_profit_ratio
            if entry_price > df.at[i, "close"]:
                capital += profit
                win_count += 1
                margin = 0
                position = 0
            elif entry_price < df.at[i, "close"]:
                capital -= profit
                loss_count += 1
                margin = 0
                position = 0

        # 하이킨아시 역봉
        elif df.at[i, "ha_open"] < df.at[i, "ha_close"]:
            take_profit_ratio = abs(df.at[i, "close"] - entry_price) / entry_price
            profit = margin * leverage * take_profit_ratio
            if entry_price > df.at[i, "close"]:
                capital += profit
                win_count += 1
                margin = 0
                position = 0
            elif entry_price < df.at[i, "close"]:
                capital -= profit
                loss_count += 1
                margin = 0
                position = 0

    if position == 0:  # 포지션이 없다면
        if h_t_long or h_m_long:
            position = 1
            margin = capital / 4
            capital -= margin * leverage * (0.1 / 100)
            entry_price = df.at[i, "close"]

        elif h_t_short or h_m_short:
            position = -1
            margin = capital / 4
            capital -= margin * leverage * (0.1 / 100)
            entry_price = df.at[i, "close"]


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
