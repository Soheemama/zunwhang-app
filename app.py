import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 의사결정 지원 시스템")

# 1. ★ 소희마마님의 비밀 장부 (평단가 데이터 완벽 이식) ★
# 미국 주식(티커)과 한국 주식(종목명/번호)을 모두 등록했습니다.
my_portfolio = {
    "GRID": 156.05, "URA": 51.93, "PL": 23.3, "ALAB": 179.8525,
    "GOOGL": 341.9194, "RKLB": 78.5850, "QBTS": 28.6800,
    "19,540": 19540, # KODEX 코스닥150 (추정)
    "466920": 38282, # SOL 조선 TOP3플러스
    "475380": 13026, # TIGER 코리아휴머노이드로봇산업
    "475370": 19330, # SOL AI 반도체소부장
    "465540": 16968, # SOL 전고체배터리&실리콘음극재
    "445380": 20232, # HANARO Fn K-반도체
    "415480": 55794  # TIGER 현대차그룹플러스
}

# 한국 종목명과 티커 매칭용 안내 (사이드바)
st.sidebar.info("💡 한국 종목은 '466920'(조선) 처럼 번호를 입력해 주세요.")

# 2. 사이드바 설정
symbol = st.sidebar.text_input("종목 코드 입력", "ALAB").upper()
default_price = my_portfolio.get(symbol, 0.0)
avg_price = st.sidebar.number_input(f"{symbol} 나의 평단가 ($/원)", value=float(default_price))

if symbol:
    # 한국 종목인지 확인 (숫자로만 된 경우 .KS 또는 .KQ 추가)
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

        # 상단 핵심 지표
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{curr:,.2f}")
        c2.metric("나의 평단가", f"{avg
