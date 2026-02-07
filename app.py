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
        # 1. 지표 계산 (이평선 & 피보나치)
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        
        high_price = float(data['High'].max())
        low_price = float(data['Low'].min())
        current_price = float(data['Close'].iloc[-1])
        
        minus_2 = high_price * 0.98
        fibo_05 = high_price - (0.5 * (high_price - low_price))
        fibo_0618 = high_price - (0.618 * (high_price - low_price))

        # 2. 상단 요약 정보
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 주가", f"${current_price:.2f}")
        c2.metric("60일 이평선", f"${data['MA60'].iloc[-1]:.2f}")
        c3.metric("120일 이평선", f"${data['MA120'].iloc[-1]:.2f}")

        # 3. 차트 생성
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_heights=[0.75, 0.25])

        # 캔들차트
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name="주가"
        ), row=1, col=1)

        # ★ 60일/120일 이평선 복구 ★
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=2)), row=1, col=1)

        # 거래량
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name="거래량", marker_color='gray', opacity=0.5), row=2, col=1)

        # ★ 피보나치 지지선 및 수치 표시 ★
        # 선만 긋는 게 아니라 수치(Text)를 차트 오른쪽에 표시합니다.
        fig.add_hline(y=minus_2, line_dash="dot", line_color="yellow", row=1, col=1,
                      annotation_text=f"-2% (${minus_2:.2f})", annotation_position="top right")
        fig.add_hline(y=fibo_05, line_dash="dash", line_color="red", row=1, col=1,
                      annotation_text=f"Fibo 0.5 (${fibo_05:.2f})", annotation_position="top right")
        fig.add_hline(y=fibo_0618, line_dash="dashdot", line_color="magenta", row=1, col=1,
                      annotation_text=f"Fibo 0.618 (${fibo_0618:.2f})", annotation_position="top right")

        # 레이아웃 정리
        fig.update_layout(
            height=700,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # 4. 하단 전략 요약
        st.subheader("📊 전황 지표 요약")
        st.write(f"현재가는 고점($ {high_price:.2f}) 대비 주요 지지선들 사이에 위치해 있습니다.")
        st.write(f"📍 **추가매수 검토가:** Fibo 0.5 (**${fibo_05:.2f}**) / Fibo 0.618 (**${fibo_0618:.2f}**)")

    else:
        st.error("데이터를 찾을 수 없습니다.")
