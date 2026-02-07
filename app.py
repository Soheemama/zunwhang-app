import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. 페이지 설정 및 숫자 잘림 방지 스타일 적용
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ 한/미 통합 전황 및 의사결정 지원 시스템")

# 2. ★ 마마님의 비밀 장부 (번호 정밀 대조 완료) ★
# 마마님이 지적하신 445380(K-반도체)을 포함해 모든 번호를 다시 확인했습니다.
my_portfolio = {
    "GRID": {"name": "GRID ETF (그리드)", "price": 156.05, "cur": "$"},
    "URA": {"name": "URA ETF (우라늄)", "price": 51.93, "cur": "$"},
    "PL": {"name": "팔란티어 (PL)", "price": 23.3, "cur": "$"},
    "ALAB": {"name": "아스테라 랩스 (ALAB)", "price": 179.8525, "cur": "$"},
    "GOOGL": {"name": "구글 (GOOGL)", "price": 341.9194, "cur": "$"},
    "RKLB": {"name": "로켓랩 (RKLB)", "price": 78.5850, "cur": "$"},
    "QBTS": {"name": "디웨이브 퀀텀 (QBTS)", "price": 28.68, "cur": "$"},
    "445380.KS": {"name": "HANARO K-반도체 (445380)", "price": 20232.0, "cur": "₩"},
    "475370.KS": {"name": "SOL AI반도체소부장 (475370)", "price": 19330.0, "cur": "₩"},
    "465540.KS": {"name": "SOL 전고체배터리 (465540)", "price": 16968.0, "cur": "₩"},
    "475380.KS": {"name": "TIGER 코리아휴머노이드 (475380)", "price": 13026.0, "cur": "₩"},
    "415480.KS": {"name": "TIGER 현대차그룹플러스 (415480)", "price": 55794.0, "cur": "₩"},
    "159400.KS": {"name": "KODEX 코스닥150 (159400)", "price": 19540.0, "cur": "₩"},
    "466920.KS": {"name": "SOL 조선 TOP3플러스 (466920)", "price": 38282.0, "cur": "₩"}
}

# 3. 사이드바: 종목 선택 리스트 (중복 방지 강화)
stock_options = {info['name']: ticker for ticker, info in my_portfolio.items()}
selected_name = st.sidebar.selectbox("감시 종목 선택", list(stock_options.keys()))
symbol = stock_options[selected_name]

currency = my_portfolio[symbol]['cur']
default_price = my_portfolio[symbol]['price']
# 화면 표시용 번호 추출 (예: 445380.KS -> 445380)
display_symbol = symbol.split('.')[0]
avg_price = st.sidebar.number_input(f"[{display_symbol}] 나의 평단가 ({currency})", value=float(default_price))

if symbol:
    # 데이터 가져오기
    data = yf.download(symbol, period="1y")
    
    # 실패 시 코스닥 재시도
    if data.empty and ".KS" in symbol:
        alt_symbol = symbol.replace(".KS", ".KQ")
        data = yf.download(alt_symbol, period="1y")

    if not data.empty:
        # 주요 수치 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        high = float(data['High'].max())
        low_min = float(data['Low'].min())
        curr_p = float(data['Close'].iloc[-1])
        diff = high - low_min
        loss_rate = ((curr_p / avg_price) - 1) * 100 if avg_price > 0 else 0

        # 4. 상단 요약 지표
        c1, c2, c3, c4 = st.columns(4)
        fmt = ",.0f" if currency == "₩" else ",.2f"
        c1.metric("현재가", f"{currency}{curr_p:{fmt}}")
        c2.metric("나의 평단가", f"{currency}{avg_price:{fmt}}")
        c3.metric("현재 수익률", f"{loss_rate:.2f}%")
        c4.metric("1년 최고가", f"{currency}{high:{fmt}}")

        st.divider()

        # 5. 전략 지시서
        st.subheader(f"🚩 {selected_name} 전황 보고")
        f05 = high - (0.5 * diff)
        f0618 = high - (0.618 * diff)
        
        col1, col2 = st.columns(2)
        with col1:
            if curr_p <= f0618: st.error(f"📍 [추매] 강력 지지선({f0618:{fmt}}) 도달!")
            elif curr_p <= f05: st.warning(f"📍 [대기] 중기 지지선({f05:{fmt}}) 부근!")
            else: st.info(f"📍 [관망] 고점({high:{fmt}}) 대비 안정권")
        
        with col2:
            if avg_price > 0:
                status = "✅ [보유] 진지 견고" if loss_rate > -10 else "🆘 [위험] 비중 조절 검토"
                st.write(f"**현재 상태:** {status}")
                st.write(f"**참고(60일선):** {currency}{data['MA60'].iloc[-1]:{fmt}}")

        # 6. 차트 생성
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)))
        
        # 피보나치 방어선
        m2 = high * 0.98
        fig.add_hline(y=m2, line_dash="dot", line_color="yellow", annotation_text=f"-2% ({m2:{fmt}})")
        for lvl, clr in [(0.236, "green"), (0.382, "cyan"), (0.5, "red"), (0.618, "magenta")]:
            val = high - (lvl * diff)
            fig.add_hline(y=val, line_dash="dash", line_color=clr, annotation_text=f"Fibo {lvl} ({val:{fmt}})")

        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"데이터 로드 실패. '{symbol}' 코드를 확인해 주세요.")
