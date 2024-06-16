import pandas as pd
from fetch import fetch_data
from calculate import calculate_ema, calculate_values
from entry_logic import (
    reverse_long,
    middle_long,
    ha_trend_long,
    reverse_short,
    middle_short,
    ha_trend_short,
    simple_long,
    simple_short,
)

# 초기 자금 설정
initial_capital = 1000
capital = initial_capital
margin = 0
leverage = 7
position = 0  # 포지션: 0 - 없음, 1 - 매수, -1 - 매도
entry_price = 0

# 익절, 손절 조건 설정 (비율)
take_profit_ratio = 0.02
stop_loss_ratio = 0.01

# 백테스트 결과를 저장할 변수 초기화
win_count = 0
loss_count = 0

volume_coff = 1.5

df: pd.DataFrame = fetch_data(symbol="BTCUSDT", interval="1h", numbers=790)
df["EMA10"] = calculate_ema(df, 10)
df["EMA20"] = calculate_ema(df, 20)
df["EMA50"] = calculate_ema(df, 50)
df = calculate_values(df)

# 백테스트 실행
for i in range(70, len(df)):
    if capital <= 0:
        break

    r_long = reverse_long(df, i, 1.5)
    m_long = middle_long(df, i, volume_coff)
    h_t_long = ha_trend_long(df, i, volume_coff)

    r_short = reverse_short(df, i, 1.5)
    m_short = middle_short(df, i, volume_coff)
    h_t_short = ha_trend_short(df, i, volume_coff)

    s_long = simple_long(df, i)
    s_short = simple_short(df, i)

    if position == 1:

        # 숏 조건인 경우
        if r_short or m_short or h_t_short:
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

        # 롱 조건인 경우
        if r_long or m_long or h_t_long:
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
        if h_t_long or m_long:
            position = 1
            margin = capital / 4
            capital -= margin * leverage * (0.1 / 100)
            entry_price = df.at[i, "close"]

        elif h_t_short or m_short:
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
