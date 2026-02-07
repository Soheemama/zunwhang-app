import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="완성형 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 거래량 분석 시스템")

symbol = st.sidebar.text_input("종목 코드 입력", "GOOGL").upper()

if symbol:
    data = yf.download(symbol, period="1y")
    
    if not data.empty:
        # 1. 지표 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high = float(data['High'].max())
        low = float(data['Low'].min())
        curr = float(data['Close'].iloc[-1])
        diff = high - low

        # 상단 수치 보고
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"${curr:.2f}")
        c2.metric("60일선", f"${data['MA60'].iloc[-1]:.2f}")
        c3.metric("120일선", f"${data['MA120'].iloc[-1]:.2f}")
        c4.metric("하락률", f"{((curr/high)-1)*100:.1f}%")

        # 2. 차트 구성 (간격 조정으로 숫자 겹침 해결)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.1, row_heights=[0.7, 0.3])

        # 주가 캔들 및 이평선
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=2)), row=1, col=1)

        # 거래량 막대 (숫자 대신 막대로 깔끔하게 표시)
        colors = ['red' if c >= o else 'blue' for c, o in zip(data['Close'], data['Open'])]
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name="거래량", marker_color=colors, showlegend=False), row=2, col=1)

        # 피보나치 5중 전선
        f_levels = [0.02, 0.236, 0.382, 0.5, 0.618]
        f_colors = ["yellow", "green", "cyan", "red", "magenta"]
        for lvl, clr in zip(f_levels, f_colors):
            val = high * (1 - lvl) if lvl == 0.02 else high - (lvl * diff)
            fig.add_hline(y=val, line_dash="dash", line_color=clr, row=1, col=1,
                          annotation_text=f"{lvl} (${val:.2f})", annotation_position="top right")

        fig.update_layout(height=900, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("데이터 로드 실패")
