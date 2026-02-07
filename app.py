import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정 및 숫자 가독성 스타일
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.markdown("<style>[data-testid='stMetricValue'] { font-size: 1.5rem !important; }</style>", unsafe_allow_html=True)

st.title("🛡️ 한/미 통합 전황 및 의사결정 지원 시스템")

# 2. ★ 마마님의 비밀 지도 ★
# 현대차그룹(415480)을 포함한 모든 종목의 티커를 야후 최신 규격으로 정렬했습니다.
portfolio_map = {
    "현대차그룹플러스 (TIGER)": {"y": "415480.KS", "price": 55794.0, "cur": "₩"},
    "K-반도체 (HANARO)": {"y": "445380.KS", "price": 20232.0, "cur": "₩"},
    "AI반도체소부장 (SOL)": {"y": "475370.KS", "price": 19330.0, "cur": "₩"},
    "전고체배터리 (SOL)": {"y": "465540.KS", "price": 16968.0, "cur": "₩"},
    "코리아휴머노이드 (TIGER)": {"y": "475380.KS", "price": 13026.0, "cur": "₩"},
    "코스닥150 (KODEX)": {"y": "159400.KQ", "price": 19540.0, "cur": "₩"},
    "조선 TOP3 (SOL)": {"y": "466920.KS", "price": 38282.0, "cur": "₩"},
    "그리드 (GRID)": {"y": "GRID", "price": 156.05, "cur": "$"},
    "우라늄 (URA)": {"y": "URA", "price": 51.93, "cur": "$"},
    "팔란티어 (PL)": {"y": "PL", "price": 23.3, "cur": "$"},
    "아스테라 랩스 (ALAB)": {"y": "ALAB", "price": 179.8525, "cur": "$"},
    "구글 (GOOGL)": {"y": "GOOGL", "price": 341.9194, "cur": "$"},
    "로켓랩 (RKLB)": {"y": "RKLB", "price": 78.5850, "cur": "$"},
    "디웨이브 퀀텀 (QBTS)": {"y": "QBTS", "price": 28.68, "cur": "$"}
}

selected_name = st.sidebar.selectbox("감시 종목 선택", list(portfolio_map.keys()))
info = portfolio_map[selected_name]
currency = info['cur']
avg_price = st.sidebar.number_input(f"나의 평단가 ({currency})", value=float(info['price']))

# ★ 3중 강제 수색 시스템 ★
@st.cache_data(ttl=300)
def load_data_final(y_ticker):
    # 1. 정규 규격 시도
    df = yf.download(y_ticker, period="1y", interval="1d", progress=False)
    if not df.empty: return df, "야후 본대"
    
    # 2. 시장 규격 교차 시도 (.KS <-> .KQ)
    alt = y_ticker.replace(".KS", ".KQ") if ".KS" in y_ticker else y_ticker.replace(".KQ", ".KS")
    df = yf.download(alt, period="1y", interval="1d", progress=False)
    if not df.empty: return df, "시장 우회"
    
    # 3. 번호만으로 시도
    clean = y_ticker.split(".")[0]
    df = yf.download(clean, period="1y", interval="1d", progress=False)
    if not df.empty: return df, "번호 직송"
    
    return None, None

data, source = load_data_final(info['y'])

if data is not None and not data.empty:
    # 지표 계산
    data['MA60'] = data['Close'].rolling(window=60).mean()
    high, curr_p = float(data['High'].max()), float(data['Close'].iloc[-1])
    diff = high - float(data['Low'].min())
    loss_rate = ((curr_p / avg_price) - 1) * 100 if avg_price > 0 else 0

    # 4. 상단 요약 (최고가 복구)
    c1, c2, c3, c4 = st.columns(4)
    fmt = ",.0f" if currency == "₩" else ",.2f"
    c1.metric("현재가", f"{currency}{curr_p:{fmt}}")
    c2.metric("나의 평단가", f"{currency}{avg_price:{fmt}}")
    c3.metric("현재 수익률", f"{loss_rate:.2f}%")
    c4.metric("1년 최고가", f"{currency}{high:{fmt}}")

    st.divider()

    # 5. 전략 지시서 및 차트
    st.subheader(f"🚩 {selected_name} 전황 보고 (보급로: {source})")
    f05, f0618 = high - (0.5 * diff), high - (0.618 * diff)
    
    col1, col2 = st.columns(2)
    with col1:
        if curr_p <= f0618: st.error(f"📍 [추매] 강력 지지선({f0618:{fmt}}) 도달!")
        elif curr_p <= f05: st.warning(f"📍 [대기] 중기 지지선({f05:{fmt}}) 부근!")
        else: st.info(f"📍 [관망] 고점 대비 안정권 유지 중")
    
    with col2:
        status = "✅ [보유] 진지 견고" if loss_rate > -10 else "🆘 [위험] 비중 조절 검토"
        st.write(f"**현재 상태:** {status}")
        st.write(f"**참고(60일선):** {currency}{data['MA60'].iloc[-1]:{fmt}}")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)))
    
    for lvl, clr in [(0.236, "green"), (0.382, "cyan"), (0.5, "red"), (0.618, "magenta")]:
        val = high - (lvl * diff)
        fig.add_hline(y=val, line_dash="dash", line_color=clr, annotation_text=f"Fibo {lvl}")

    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"⚠️ {selected_name} 보급로 재탐색 중. 잠시 후 [새로고침(F5)] 해주세요.")
