# 바이낸스 선물거래 (BTCUSDT, ETHUSDT, SOLUSDT)

## 트레이딩 로직

1. 돌파 매매(추세 매매, 쿠리마기 매매법(Kristjan Qullamaggie))
2. 역추세 매매(Regular RSI divergence 이용)

#### 돌파 매매(추세 매매)

<p align="left">
  <img src="/images/breakout_long.png" alt="돌파 롱" style="width: 60%;">
</p>

- 조정 구간(박스권 구간) 후 상승에 올라타는 방법
- 지수이평선 정배열(ema10 > ema20 > ema50)
- 박스권 상단 돌파 후 롱 진입
- 손절가는 진입 봉 시가

<p align="left">
  <img src="/images/breakout_short.png" alt="돌파 숏" style="width: 60%;">
</p>

- 조정 구간(박스권 구간) 후 하락
- 지수이평선 역배열(ema10 < ema20 < ema50)
- 박스권 하단 돌파 후 숏 진입
- 손절가는 진입 봉 시가

#### 역 추세 매매(RSI 다이버전스 이용)

- 가격의 큰 상승/하락 후 역추세를 노리는 방법

<p align="left">
  <img src="/images/rsi.png" alt="RSI 다이버전스" style="width: 50%;margin-right:10%;">
  <img src="/images/rsi_bull.png" alt="RSI 다이버전스 롱" style="width: 20%;">
</p>

- Regular만 사용
- 가격의 극값 변화와 RSI 극값 변화가 반대일 때 이용

###### 1번 확인 후 2번 확인

###### 심볼 하나 당 하나의 포지션

###### 시가 손절, 1/3씩 3번 익/손절
