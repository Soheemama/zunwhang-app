import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="완성형 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 거래량 분석 시스템")

symbol = st.sidebar.text_input("종목 코드 입력 (예: GOOGL)", "GOOGL").upper()

if symbol:
    data = yf.download(symbol, period="1y")
    
    if not data.empty:
        # 데이터 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high_price = float(data['High'].max())
        low_price = float(data['Low'].min())
        current_price = float(data['Close'].iloc[-1])
        
        # 지지선 수치 계산
        minus_2 = high_price * 0.98
        fibo_05 = high_price - (0.5 * (high_price - low_price))
        fibo_0618 = high_price - (0.618 * (high_price - low_price))

        # 상단 지표 출력
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 주가", f"${current_price:.2f}")
        c2.metric("최근 1년 고점", f"${high_price:.2f}")
        c3.metric("하락률", f"{((current_price/high_price)-1)*100:.2f}%")

        # 차트 레이아웃 설정
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_heights=[0.8, 0.2])

        # 1. 주가 캔들차트
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name="주가"
        ), row=1, col=1)

        # 2. 이동평균선
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=1.5)), row=1, col=1)

        # 3. 거래량 (에러 안전 장
