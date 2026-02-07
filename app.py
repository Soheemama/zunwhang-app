import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. 페이지 설정 및 숫자 잘림 방지 스타일 적용
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.markdown("""
    <style>
    /* 한국 주식의 큰 숫자가 잘리지 않도록 폰트 크기를 최적화합니다 */
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ 한/미 통합 전황 및 의사결정 지원 시스템")

# 2. ★ 마마님의 비밀 지도 (이름만 고르면 번호는 자동 연결) ★
# 야후 서버가 가장 잘 알아듣는 .KS 규격으로 전수 교체했습니다.
portfolio_map = {
    "그리드 (GRID)": {"ticker": "GRID", "price": 156.05, "cur": "$"},
    "우라늄 (URA)": {"ticker": "URA", "price": 51.93, "cur": "$"},
    "팔란티어 (PL)": {"ticker": "PL", "price": 23.3, "cur": "$"},
    "아스테라 랩스 (ALAB)": {"ticker": "ALAB", "price": 179.8525, "cur": "$"},
    "구글 (GOOGL)": {"ticker": "GOOGL", "price": 341.9194, "cur": "$"},
    "로켓랩 (RKLB)": {"ticker": "RKLB", "price": 78.5850, "cur": "$"},
    "디웨이브 퀀텀 (QBTS)": {"ticker": "QBTS", "price": 28.68, "cur": "$"},
    "K-반도체 (HANARO)": {"ticker": "445380.KS", "price": 20232.0, "cur": "₩"},
    "AI반도체소부장 (SOL)": {"ticker": "475370.KS", "price": 19330.0, "cur": "₩"},
    "전고체배터리 (SOL)": {"ticker": "465540.KS", "price": 16968.0, "cur": "₩"},
    "코리아휴머노이드 (TIGER)": {"ticker": "475380.KS", "price": 13026.0, "cur": "₩"},
    "현대차그룹플러스 (TIGER)": {"ticker": "415480.KS", "price": 55794.0, "cur": "₩"},
    "코스닥150 (KODEX)": {"ticker": "159400.KS", "price": 19540.0, "cur": "₩"},
    "조선 TOP3 (SOL)": {"ticker": "466920.KS", "price": 38282.0, "cur": "₩"}
}

# 3. 사이드바: 종목 이름 선택
selected_name = st.sidebar.selectbox("감시 종목 선택", list(portfolio_map.keys()))
info = portfolio_map[selected_name]
symbol = info['ticker']
currency = info['cur']

# 평단가 자동 세팅
avg_price = st.sidebar.number_input(f"나의 평단가 ({currency})", value=float(info['price']))

if symbol:
    # 데이터 강제 소환
    data = yf.download(symbol, period="1y")
    
    # .KS 실패 시 .KQ(코스닥)로 자동 전환하여 2차 수색
    if data.empty and ".KS" in symbol:
        alt_symbol = symbol.replace(".KS", ".KQ")
        data = yf.download(alt_symbol, period="1y")

    if not data.empty:
        # 지표 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        high = float(data['High'].max())
        curr_p = float(data['Close'].iloc[-1])
        diff = high - float(data['Low'].min())
        loss_rate = ((curr_p / avg_price) - 1) * 100 if avg_price > 0 else 0

        # 4. 상단 지표
        c1, c2, c3, c4 = st.columns(4)
        fmt = ",.0f" if currency == "₩" else ",.2f"
        c1.metric("현재가", f"{currency}{curr_p:{fmt}}")
        c2.metric("나의 평단가", f"{currency}{avg_price:{fmt}}")
        c3.metric("현재 수익률", f"{loss_rate:.2f}%")
        c4.metric("1년 최고가", f"{currency}{high:{fmt}}")

        st.divider()

        # 5. 전략 지시서
        st.subheader(f"🚩 {selected_name} 전황 보고")
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

        # 6. 차트 생성
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)))
        
        # 피보나치 방어선 복구
        m2 = high * 0.98
        fig.add_hline(y=m2, line_dash="dot", line_color="yellow", annotation_text=f"-2% ({m2:{fmt}})")
        for lvl, clr in [(0.236, "green"), (0.382, "cyan"), (0.5, "red"), (0.618, "magenta")]:
            val = high - (lvl * diff)
            fig.add_hline(y=val, line_dash="dash", line_color=clr, annotation_text=f"Fibo {lvl} ({val:{fmt}})")

        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"데이터 로드 실패. '{selected_name}'의 서버 연결을 재시도 중입니다.")
