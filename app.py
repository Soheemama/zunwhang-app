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
        # 1. 지표 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        
        high_price = float(data['High'].max())
        low_price = float(data['Low'].min())
        current_price = float(data['Close'].iloc[-1])
        diff = high_price - low_price
        
        # 피보나치 5단계 전선
        minus_2 = high_price * 0.98
        fibo_0236 = high_price - (0.236 * diff)
        fibo_0382 = high_price - (0.382 * diff)
        fibo_05 = high_price - (0.5 * diff)
        fibo_0618 = high_price - (0.618 * diff)

        # 2. 상단 요약 정보
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재 주가", f"${current_price:.2f}")
        c2.metric("최근 고점", f"${high_price:.2f}")
        c3.metric("60일선", f"${data['MA60'].iloc[-1]:.2f}")
        c4.metric("120일선", f"${data['MA120'].iloc[-1]:.2f}")

        # 3. 차트 생성 (주가 7: 거래량 3 비율)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, row_heights=[0.7, 0.3])

        # 캔들차트 및 이평선 (1행)
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name="주가"
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=1.5)), row=1, col=1)

        # 거래량 복구 (2행)
        # 종가에 따라 색상 구분 (상승 빨강, 하락 파랑)
        colors = ['red' if c >= o else 'blue' for c, o in zip(data['Close'], data['Open'])]
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name="거래량", marker_color=colors, opacity=0.6), row=2, col=1)

        # 피보나치 5개 전선 표시 (수치 포함)
        lines = [
            (minus_2, "yellow", "dot", f"-2% (${minus_2:.2f})"),
            (fibo_0236, "green", "dash", f"0.236 (${fibo_0236:.2f})"),
            (fibo_0382, "cyan", "dash", f"0.382 (${fibo_0382:.2f})"),
            (fibo_05, "red", "dash", f"0.5 (${fibo_05:.2f})"),
            (fibo_0618, "magenta", "dashdot", f"0.618 (${fibo_0618:.2f})")
        ]

        for val, color, style, text in lines:
            fig.add_hline(y=val, line_dash=style, line_color=color, row=1, col=1,
                          annotation_text=text, annotation_position="top right")

        # 레이아웃 정리
        fig.update_layout(
            height=850,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            showlegend=True,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # 4. 전략 가이드
        st.subheader("📊 피보나치 전략 분석")
        st.write(f"현재가는 고점 대비 **{((current_price/high_price)-1)*100:.2f}%** 지점에 있습니다.")
        
    else:
        st.error("데이터를 찾을 수 없습니다.")
