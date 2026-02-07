import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.markdown("<style>[data-testid='stMetricValue'] { font-size: 1.5rem !important; }</style>", unsafe_allow_html=True)

st.title("🛡️ 한/미 통합 전황 및 의사결정 지원 시스템")

# 2. ★ 마마님의 비밀 지도 ★
portfolio_map = {
    "현대차그룹플러스 (TIGER)": {"n": "415480", "y": "415480.KS", "price": 55794.0, "cur": "₩"},
    "K-반도체 (HANARO)": {"n": "445380", "y": "445380.KS", "price": 20232.0, "cur": "₩"},
    "코스닥150 (KODEX)": {"n": "159400", "y": "159400.KQ", "price": 19540.0, "cur": "₩"},
    "AI반도체소부장 (SOL)": {"n": "475370", "y": "475370.KS", "price": 19330.0, "cur": "₩"},
    "전고체배터리 (SOL)": {"n": "465540", "y": "465540.KS", "price": 16968.0, "cur": "₩"},
    "코리아휴머노이드 (TIGER)": {"n": "475380", "y": "475380.KS", "price": 13026.0, "cur": "₩"},
    "조선 TOP3 (SOL)": {"n": "466920", "y": "466920.KS", "price": 38282.0, "cur": "₩"},
    "그리드 (GRID)": {"n": None, "y": "GRID", "price": 156.05, "cur": "$"},
    "우라늄 (URA)": {"n": None, "y": "URA", "price": 51.93, "cur": "$"},
    "팔란티어 (PL)": {"n": None, "y": "PL", "price": 23.3, "cur": "$"},
    "아스테라 랩스 (ALAB)": {"n": None, "y": "ALAB", "price": 179.8525, "cur": "$"},
    "구글 (GOOGL)": {"n": None, "y": "GOOGL", "price": 341.9194, "cur": "$"},
    "로켓랩 (RKLB)": {"n": None, "y": "RKLB", "price": 78.5850, "cur": "$"},
    "디웨이브 퀀텀 (QBTS)": {"n": None, "y": "QBTS", "price": 28.68, "cur": "$"}
}

selected_name = st.sidebar.selectbox("감시 종목 선택", list(portfolio_map.keys()))
info = portfolio_map[selected_name]
currency = info['cur']
avg_price = st.sidebar.number_input(f"나의 평단가 ({currency})", value=float(info['price']))

# ★ 데이터 보급로 ★
@st.cache_data(ttl=60)
def load_data_robust(item):
    if item['cur'] == "₩":
        try:
            url = f"https://fchart.naver.com/sise.nhn?symbol={item['n']}&timeframe=day&count=400&requestType=0"
            r = requests.get(url, timeout=5)
            data = []
            for line in r.text.strip().split('\n'):
                if '<item data=' in line:
                    v = line.split('"')[1].split('|')
                    data.append([v[0], float(v[1]), float(v[2]), float(v[3]), float(v[4])])
            df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close'])
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            if not df.empty: return df, "네이버"
        except: pass
    
    df = yf.download(item['y'], period="2y", interval="1d", progress=False)
    return (df, "야후") if not df.empty else (None, None)

data, source = load_data_robust(info)

if data is not None and not data.empty:
    # 지표 계산 (60일선 및 120일선)
    data['MA60'] = data['Close'].rolling(window=60).mean()
    data['MA120'] = data['Close'].rolling(window=120).mean()
    
    high, curr_p = float(data['High'].max()), float(data['Close'].iloc[-1])
    diff = high - float(data['Low'].min())
    loss_rate = ((curr_p / avg_price) - 1) * 100 if avg_price > 0 else 0

    # 4. 상단 요약
    c1, c2, c3, c4 = st.columns(4)
    fmt = ",.0f" if currency == "₩" else ",.2f
