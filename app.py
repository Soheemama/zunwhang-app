import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="전황 투자 비서", layout="wide")
st.title("🛡️ 전황(戰況) 투자 의사결정 시스템")

# 종목 입력
symbol = st.sidebar.text_input("종목 코드 입력 (예: NVDA, GOOGL)", "GOOGL").upper()
period = st.sidebar.selectbox("기간", ["6mo", "1y", "2y"])

if symbol:
    data = yf.download(symbol, period=period)
    
    # 이평선 계산
    data['MA60'] = data['Close'].rolling(window=60).mean()
    data['MA120'] = data['Close'].rolling(window=120).mean()
    
    # 피보나치 계산 (최근 고점 기준)
    high_price = float(data['High'].max())
    low_price = float(data['Low'].min())
    diff = high_price - low_price
    
    current_price = float(data['Close'].iloc[-1])
    support_2pct = high_price * 0.98
    fibo_50 = high_price - (0.5 * diff)
    fibo_618 = high_price - (0.618 * diff)

    # 전황 판정
    is_bull = data['MA60'].iloc[-1] > data['MA120'].iloc[-1]
    status = "🔥 공격 가능 (정배열)" if is_bull else "❄️ 수비 전념 (역배열)"

    # 대시보드 출력
    col1, col2, col3 = st.columns(3)
    col1.metric("현재가", f"${current_price:.2f}")
    col2.metric("전황 판정", status)
    col3.metric("고점 대비 -2%", f"${support_2pct:.2f}")

    st.subheader("🛡️ 3-4-1 전략 지지선")
    st.write(f"1차(비중3): **${support_2pct:.2f}** | 2차(비중4): **${fibo_50:.2f}** | 3차(비중1): **${fibo_618:.2f}**")

    # 차트 그리기
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='red')))
    st.plotly_chart(fig, use_container_width=True)
