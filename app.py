import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="완성형 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 거래량 분석 시스템")

symbol = st.sidebar.text_input("종목 코드 입력 (예: GOOGL)", "GOOGL").upper()

if symbol:
    # 1년치 데이터 가져오기
    data = yf.download(symbol, period="1y")
    
    if not data.empty:
        # 데이터 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high_price = float(data['High'].max())
        low_price = float(data['Low'].min())
        current_price = float(data['Close'].iloc[-1])
        
        # 지지선 수치
        minus_2 = high_price * 0.98
        fibo_05 = high_price - (0.5 * (high_price - low_price))
        fibo_0618 = high_price - (0.618 * (high_price - low_price))

        # 상단 지표
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 주가", f"${current_price:.2f}")
        c2.metric("최근 1년 고점", f"${high_price:.2f}")
        c3.metric("하락률", f"{((current_price/high_price)-1)*100:.2f}%")

        # 차트 레이아웃 (주가 80%, 거래량 20%)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_heights=[0.8, 0.2])

        # 1. 캔들차트 (주가)
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name="주가"
        ), row=1, col=1)

        # 2. 이동평균선
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=1.5)), row=1, col=1)

        # 3. 거래량 (에러 수정 포인트: 색상 계산 방식 변경)
        # 종가 > 시가 면 빨강, 아니면 파랑
        data['Bar_Color'] = ['red' if c >= o else 'blue' for c, o in zip(data['Close'], data['Open'])]
        
        fig.add_trace(go.Bar(
            x=data.index, y=data['Volume'], 
            name="거래량", 
            marker_color=data['Bar_Color'], 
            opacity=0.7
        ), row=2, col=1)

        # 4. 피보나치 지지선 (가로선)
        fig.add_hline(y=minus_2, line_dash="dot", line_color="yellow", annotation_text="-2%", row=1, col=1)
        fig.add_hline(y=fibo_05, line_dash="dash", line_color="red", annotation_text="Fibo 0.5", row=1, col=1)
        fig.add_hline(y=fibo_0618, line_dash="dashdot", line_color="magenta", annotation_text="Fibo 0.618", row=1, col=1)

        # 레이아웃 정리
        fig.update_layout(
            height=800,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            showlegend=True,
            margin=
