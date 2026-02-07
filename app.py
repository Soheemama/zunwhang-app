import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 의사결정 지원 시스템")

# 1. ★ 소희마마님의 진짜 비밀 장부 (평단가 데이터 명부) ★
my_portfolio = {
    "GRID": 156.05, "URA": 51.93, "PL": 23.3, "ALAB": 179.8525,
    "GOOGL": 341.9194, "RKLB": 78.5850, "QBTS": 28.68,
    "159400": 19540, "466920": 38282, "475380": 13026,
    "475370": 19330, "465540": 16968, "445380": 20232, "415480": 55794
}

# 2. 사이드바 설정
symbol = st.sidebar.text_input("종목 코드 입력", "GRID").upper()
default_price = my_portfolio.get(symbol, 0.0)
avg_price = st.sidebar.number_input(f"{symbol} 나의 평단가", value=float(default_price))

if symbol:
    search_symbol = f"{symbol}.KS" if symbol.isdigit() and len(symbol) == 6 else symbol
    data = yf.download(search_symbol, period="1y")
    
    if not data.empty:
        # 데이터 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high, low = float(data['High'].max()), float(data['Low'].min())
        curr = float(data['Close'].iloc[-1])
        diff = high - low
        loss_rate = ((curr / avg_price) - 1) * 100 if avg_price > 0 else 0

        # 상단 지표 (괄호 에러 수정 완료)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{curr:,.2f}")
        c2.metric("나의 평단가", f"{avg_price:,.2f}")
        c3.metric("현재 수익률", f"{loss_rate:.2f}%")
        c4.metric("최근 고점", f"{high:,.2f}")

        st.divider()

        # 3. 서바이벌 전략 지표 (피보나치 수식 보강)
        st.subheader("🚩 전략 수립 보고")
        f05 = high - (0.5 * diff)
        f0618 = high - (0.618 * diff)

        col1, col2 = st.columns(2)
        with col1:
            if curr <= f0618: st.error(f"📍 [추가매수] 강력 지지선({f0618:,.2f}) 도달!")
            elif curr <= f05: st.warning(f"📍 [분할매수] 중기 지지선({f05:,.2f}) 부근!")
            else: st.info("📍 [관망 유지] 아직 전황이 안정적입니다.")
        with col2:
            if avg_price > 0:
                if loss_rate > -10: st.success("✅ [보유 유지] 현재 진지는 견고합니다.")
                else: st.error("🆘 [위험 관리] 손절 혹은 비중 축소를 검토하세요.")

        # 4. 차트 (이평선 60/120일 & 피보나치)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=1.5)))
