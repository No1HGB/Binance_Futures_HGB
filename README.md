# 바이낸스 선물 자동매매 봇 (BTCUSDT, ETHUSDT)

## 트레이딩 로직

### 역추세 진입

- 양봉 (숏은 반대)
- 종가 > 50일선 (숏은 반대)
- 거래량 >= 거래량 50일선 1.5배
- 고가 > 50일선 > 저가

### 추세 진입

- 양봉 (숏은 반대)
- 종가 > 50일선 (숏은 반대)
- 종가 > 진입 봉 전 7개 시가,종가 중 최대값 (숏은 반대)
- 거래량 >= 거래량 50일선 1.5배
- 30 <= RSI <= 70

### 포지션 일부 종료(1/3씩)

- RSI >= 70(롱)
- RSI <= 30 (숏)
- 거래량 >= 거래량 50일선 1.5배

### 풀손절 풀익절

- 전체 포지션 % 손절 익절
