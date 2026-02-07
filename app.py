import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. 페이지 설정 및 숫자 잘림 방지 스타일 적용
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.markdown("""
    <style>
    /* 숫자 크기를 최적화하여 큰 금액도 잘리지 않게 합니다 */
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ 한/미 통합 전황 및 의사결정 지원 시스템")

# 2. ★ 마마님의 비밀 장부 ★
my_portfolio = {
    "GRID": {"name": "GRID ETF (그리드)", "price": 156.05, "cur": "$"},
    "URA": {"name": "URA ETF (우라늄)", "price": 51.93, "cur": "$"},
    "PL": {"name": "팔란티어 (PL)", "price": 23.3, "cur": "$"},
    "ALAB": {"name": "아스테라 랩스 (ALAB)", "price": 179.8525, "cur": "$"},
    "GOOGL": {"name": "구글 (GOOGL)", "price": 341.9194, "cur": "$"},
    "RKLB": {"name": "로켓랩 (RKLB)", "price": 78.5850, "cur": "$"},
    "QBTS": {"name": "디웨이브 퀀텀 (QBTS)", "price": 28.68, "cur": "$"},
    "445380": {"name": "HANARO K-반도체", "price": 20232.0, "cur": "₩"},
    "475370": {"name": "SOL AI반도체소부장", "price": 19330.0, "cur": "₩"},
    "465540": {"name": "SOL 전고체배터리", "price": 16968.0, "cur": "₩"},
    "475380": {"name": "TIGER 코리아휴머노이드", "price": 13026.0, "cur": "₩"},
    "415480": {"name": "TIGER 현대차그룹플러스", "price": 55794.0, "cur": "₩"},
    "159400": {"name": "KODEX 코스닥150", "price": 19540.0, "cur": "₩"},
    "466920": {"name": "SOL 조선 TOP3플러스", "price": 38282.0, "cur": "₩"}
}

# 3. 사이드바: 종목 선택 리스트
stock_names = [info['name'] for info in my_portfolio.values()]
selected_name = st.sidebar.selectbox("감시 종목 선택", stock_names)

symbol = next((s for s, info in my_portfolio.items() if info['name'] == selected_name), "")
currency = my_portfolio[symbol]['cur']
default_price = my_portfolio[symbol]['price']
avg_price = st.sidebar.number_input(f"[{symbol}] 나의 평단가 ({currency})", value=float(default_price))

if symbol:
    search_symbol = f"{symbol}.KS" if symbol.isdigit() and len(symbol) == 6 else symbol
    data = yf.download(search_symbol, period="1y")
    
    if data.empty and symbol.isdigit():
        data = yf.download(f"{symbol}.KQ", period="1y")

    if not data.empty:
        # 데이터 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        high = float(data['High'].max())
        curr_p = float(data['Close'].iloc[-1])
        diff = high - float(data['Low'].min())
        loss_rate = ((curr_p / avg_price) - 1) * 100 if avg_price > 0 else 0

        # 4. 상단 요약 (최고가 복구!)
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
            else: st.info(f"📍 [관망] 고점({high:{fmt}}) 대비 안정적 전황")
        
        with col2:
            if avg_price > 0:
                status = "✅ [보유] 진지 견고" if loss_rate > -10 else "🆘 [위험] 비중 조절 검토"
                st.write(f"**현재 상태:** {status}")
                st.write(f"**참고(60일선):** {currency}{data['MA60'].iloc[-1]:{fmt}}")

        # 6. 차트 생성
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)))
        
        m2 = high * 0.98
        fig.add_hline(y=m2, line_dash="dot", line_color="yellow", annotation_text=f"-2% ({m2:{fmt}})")
        for lvl, clr in [(0.236, "green"), (0.382, "cyan"), (0.5, "red"), (0.618, "magenta")]:
            val = high - (lvl * diff)
            fig.add_hline(y=val, line_dash="dash", line_color=clr, annotation_text=f"Fibo {lvl} ({val:{fmt}})")

        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"데이터 로드 실패.")
