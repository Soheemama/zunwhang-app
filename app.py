import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="전황 분석 시스템", layout="wide")
st.title("🛡️ 주식 전황 및 거래량 분석 시스템")

# 종목 코드 입력
symbol = st.sidebar.text_input("종목 코드 입력 (예: GOOGL)", "GOOGL").upper()

if symbol:
    # 데이터 가져오기 (에러 방지를 위해 1년치로 고정)
    data = yf.download(symbol, period="1y")
    
    if not data.empty:
        # 주요 수치 계산
        high_price = float(data['High'].max())
        low_price = float(data['Low'].min())
        current_price = float(data['Close'].iloc[-1])
        
        # 지지선 계산
        minus_2 = high_price * 0.98
        fibo_05 = high_price - (0.5 * (high_price - low_price))
        fibo_0618 = high_price - (0.618 * (high_price - low_price))

        # 상단 요약 정보
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 주가", f"${current_price:.2f}")
        c2.metric("최근 1년 고점", f"${high_price:.2f}")
        c3.metric("하락률", f"{((current_price/high_price)-1)*100:.2f}%")

        # --- 그래프 그리기 시작 ---
        try:
            # 주가(80%)와 거래량(20%) 화면 분할
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                               vertical_spacing=0.05, row_heights=[0.7, 0.3])

            # 1. 캔들차트
            fig.add_trace(go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name="주가"
            ), row=1, col=1)

            # 2. 거래량 (에러를 방지하기 위해 단순화)
            fig.add_trace(go.Bar(
                x=data.index, y=data['Volume'], name="거래량", marker_color='gray'
            ), row=2, col=1)

            # 3. 피보나치 지지선 (가로선)
            fig.add_hline(y=minus_2, line_dash="dot", line_color="yellow", annotation_text="-2%", row=1, col=1)
            fig.add_hline(y=fibo_05, line_dash="dash", line_color="red", annotation_text="0.5", row=1, col=1)
            fig.add_hline(y=fibo_0618, line_dash="dashdot", line_color="magenta", annotation_text="0.618", row=1, col=1)

            # 레이아웃 설정
            fig.update_layout(
                height=600,
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            
            # 차트 출력
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"그래프를 그리는 중 오류가 발생했습니다: {e}")

        # 대응 가이드
        st.subheader("💡 전략적 대응 가이드")
        if current_price <= fibo_0618:
            st.error(f"🚩 강력 지지선(${fibo_0618:.2f}) 부근입니다.")
        elif current_price <= fibo_05:
            st.warning(f"⚠️ 중기 지지선(${fibo_05:.2f}) 부근입니다.")
        else:
            st.success("✅ 안정적인 전황 유지 중")
            
    else:
        st.error("데이터를 찾을 수 없습니다. 종목 코드를 확인해 주세요.")
