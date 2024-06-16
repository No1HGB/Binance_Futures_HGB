import pandas as pd
from fetch import fetch_data
from calculate import calculate_ema, calculate_values
from entry_logic import (
    just_long,
    just_short,
    reverse_long,
    reverse_short,
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
volume_coff = 1.5

# 백테스트 결과를 저장할 변수 초기화
win_count = 0
loss_count = 0

df: pd.DataFrame = fetch_data(symbol="ETHUSDT", interval="1h", numbers=1000)
df["EMA10"] = calculate_ema(df, 10)
df["EMA20"] = calculate_ema(df, 20)
df["EMA50"] = calculate_ema(df, 50)
df["EMA200"] = calculate_ema(df, 200)
df = calculate_values(df)


# 백테스트 실행
for i in range(100, len(df)):
    if capital <= 0:
        break

    long = just_long(df, i)
    short = just_short(df, i)
    r_long = reverse_long(df, i, volume_coff)
    r_short = reverse_short(df, i, volume_coff)

    if position == 1:

        take_profit_price = entry_price * (1 + take_profit_ratio)
        stop_loss_price = entry_price * (1 - stop_loss_ratio)

        if take_profit_price <= df.at[i, "high"]:
            profit = (
                margin * leverage * ((take_profit_price - entry_price) / entry_price)
            )
            if profit > 0:
                capital += profit
                win_count += 1
                margin = 0
                position = 0
            elif profit < 0:
                capital += profit
                loss_count += 1
                margin = 0
                position = 0

        elif stop_loss_price >= df.at[i, "close"]:
            loss = margin * leverage * (df.at[i, "close"] - entry_price) / entry_price
            if loss > 0:
                capital += loss
                win_count += 1
                margin = 0
                position = 0
            elif loss < 0:
                capital += loss
                loss_count += 1
                margin = 0
                position = 0

        elif short or r_short:
            profit_loss = (
                margin * leverage * (df.at[i, "close"] - entry_price) / entry_price
            )
            if profit_loss > 0:
                capital += profit_loss
                win_count += 1
                margin = 0
                position = 0
            elif profit_loss < 0:
                capital += profit_loss
                loss_count += 1
                margin = 0
                position = 0

    elif position == -1:
        take_profit_price = entry_price * (1 - take_profit_ratio)
        stop_loss_price = entry_price * (1 + stop_loss_ratio)

        if take_profit_price >= df.at[i, "low"]:
            profit = (
                margin * leverage * ((entry_price - take_profit_price) / entry_price)
            )
            if profit > 0:
                capital += profit
                win_count += 1
                margin = 0
                position = 0
            elif profit < 0:
                capital += profit
                loss_count += 1
                margin = 0
                position = 0

        elif stop_loss_price <= df.at[i, "close"]:
            loss = margin * leverage * (entry_price - df.at[i, "close"]) / entry_price
            if loss > 0:
                capital += loss
                win_count += 1
                margin = 0
                position = 0
            elif loss < 0:
                capital += loss
                loss_count += 1
                margin = 0
                position = 0

        elif long or r_long:
            profit_loss = (
                margin * leverage * (entry_price - df.at[i, "close"]) / entry_price
            )
            if profit_loss > 0:
                capital += profit_loss
                win_count += 1
                margin = 0
                position = 0
            elif profit_loss < 0:
                capital += profit_loss
                loss_count += 1
                margin = 0
                position = 0

    if position == 0:  # 포지션이 없다면
        if long:
            position = 1
            margin = capital / 4
            capital -= margin * leverage * (0.1 / 100)
            entry_price = df.at[i, "close"]

        elif short:
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
