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
        
        minus_2 = high_price * 0.98
        fibo_05 = high_price - (0.5 * (high_price - low_price))
        fibo_0618 = high_price - (0.618 * (high_price - low_price))

        # 상단 지표
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 주가", f"${current_price:.2f}")
        c2.metric("최근 1년 고점", f"${high_price:.2f}")
        c3.metric("하락률", f"{((current_price/high_price)-1)*100:.2f}%")

        # 차트 레이아웃 설정 (주가와 거래량을 8:2 비율로 나눔)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, row_heights=[0.8, 0.2])

        # 1. 캔들차트 (주가)
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name="주가"
        ), row=1, col=1)

        # 2. 이동평균선
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=1.5)), row=1, col=1)

        # 3. 거래량 (막대 차트)
        colors = ['red' if row['Open'] < row['Close'] else 'blue' for _, row in data.iterrows()]
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name="거래량", marker_color=colors, opacity=0.7), row=2, col=1)

        # 4. 피보나치 지지선 (가로선)
        fig.add_hline(y=minus_2, line_dash="dot", line_color="yellow", annotation_text="-2%", row=1, col=1)
        fig.add_hline(y=fibo_05, line_dash="dash", line_color="red", annotation_text="Fibo 0.5", row=1, col=1)
        fig.add_hline(y=fibo_0618, line_dash="dashdot", line_color="magenta", annotation_text="Fibo 0.618", row=1, col=1)

        # 레이아웃 정리
        fig.update_layout(
            height=800,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            yaxis_title="가격 ($)",
            yaxis2_title="거래량",
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # 추가매수 가이드
        st.subheader("💡 전략적 대응 가이드")
        if current_price <= fibo_0618:
            st.error(f"🚩 최후 방어선(${fibo_0618:.2f}) 부근! 거래량 동반 반등 확인 시 강력 매수")
        elif current_price <= fibo_05:
            st.warning(f"⚠️ 중기 지지선(${fibo_05:.2f}) 도달! 분할 추가매수 구간")
        else:
            st.success("✅ 전황 안정세 유지. 지지선까지 관망")
    else:
        st.error("종목 정보를 가져오지 못했습니다.")
