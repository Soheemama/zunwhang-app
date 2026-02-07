import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 의사결정 지원 시스템")

# 1. ★ 소희마마님의 진짜 비밀 장부 (평단가 데이터 명부) ★
my_portfolio = {
    "GRID": 156.05, "URA": 51.93, "PL": 23.3, "ALAB": 179.8525,
    "GOOGL": 341.9194, "RKLB": 78.5850, "QBTS": 28.68,
    "159400": 19540, # KODEX 코스닥150 (추정)
    "466920": 38282, # SOL 조선 TOP3플러스
    "475380": 13026, # TIGER 코리아휴머노이드로봇산업
    "475370": 19330, # SOL AI 반도체소부장
    "465540": 16968, # SOL 전고체배터리&실리콘음극재
    "445380": 20232, # HANARO Fn K-반도체
    "415480": 55794  # TIGER 현대차그룹플러스
}

# 2. 사이드바 설정
symbol = st.sidebar.text_input("종목 코드 입력", "GRID").upper()
default_price = my_portfolio.get(symbol, 0.0)
avg_price = st.sidebar.number_input(f"{symbol} 나의 평단가", value=float(default_price))

if symbol:
    # 한국 종목 처리 로직
    search_symbol = f"{symbol}.KS" if symbol.isdigit() and len(symbol) == 6 else symbol
    data = yf.download(search_symbol, period="1y")
    
    if not data.empty:
        # 데이터 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high = float(data['High'].max())
        low = float(data['Low'].min())
        curr = float(data['Close'].iloc[-1])
        diff = high - low
        loss_rate = ((curr / avg_price) - 1) * 100 if avg_price > 0 else 0

        # 상단 지표 (image_2a983d.png에서 발생한 괄호 에러 수정 완료)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{curr:,.2f}")
        c2.metric("나의 평단가", f"{avg_price:,.2f}")
        c3.metric("현재 수익률", f"{loss_rate:.2f}%")
        c4.metric("최근 고점", f"{high:,.2f}")

        st.divider()

        # 3. 서바이벌 전략 지표
        st.subheader("🚩 전략 수립 보고")
        f05, f0618 = high - (0.5 * diff), high - (0.
