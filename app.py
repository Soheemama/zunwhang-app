import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. 페이지 설정 및 숫자 잘림 방지를 위한 스타일 적용
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.markdown("""
    <style>
    /* 숫자 크기를 살짝 줄여서 잘림 현상을 방지합니다 */
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ 한/미 통합 전황 및 의사결정 지원 시스템")

# 2. ★ 마마님의 비밀 장부 (평단가 데이터 명부) ★
my_portfolio = {
    "GRID": {"name": "GRID ETF (그리드)", "price": 156.05, "cur": "$"},
    "URA": {"name": "URA ETF (우라늄)", "price": 51.93, "cur": "$"},
    "PL": {"name": "팔란티어 (PL)", "price": 23.3, "cur": "$"},
    "ALAB": {"name": "아스테라 랩스 (ALAB)", "price": 179.8525, "cur": "$"},
    "GOOGL": {"name": "구글 (GOOGL)", "price": 341.9194, "cur": "$"},
    "RKLB": {"name": "로켓랩 (RKLB)", "price": 78.5850, "cur": "$"},
    "QBTS": {"name": "디웨이브 퀀텀 (QBTS)", "price": 28.68, "cur": "$"},
    "445380": {"name": "HANARO K-반도체", "price": 20232, "cur": "₩"},
    "475370": {"name": "SOL AI반도체소부장", "price": 19330, "cur": "₩"},
    "465540": {"name": "SOL 전고체배터리", "price": 16968, "cur": "₩"},
    "475380": {"name": "TIGER 코리아휴머노이드", "price": 13026, "cur": "₩"},
    "415480": {"name": "TIGER 현대차그룹플러스", "price": 55794, "cur": "₩"},
    "159400": {"name": "KODEX 코스닥150", "price": 19540, "cur": "₩"},
    "466920": {"name": "SOL 조선 TOP3플러스", "price": 38282, "cur": "₩"}
}

# 3. 사이드바: 종목 선택 리스트
stock_names = [info['name'] for info in my_portfolio.values()]
selected_name = st.sidebar.selectbox("감시 종목 선택", stock_names)

# 선택한 종목의 정보 추출 (image_2bf83c 에러 지점 수정 완료)
symbol = ""
for s, info in my_portfolio.items():
    if info['name'] == selected_name:
        symbol = s
        currency = info['cur']
        break

default_price = my_portfolio[symbol]['price']
avg_price = st.sidebar.number_input(f"[{symbol}] 나의 평단가 ({currency})", value=float(default_price))

if symbol:
    # 한국 주식은 종목 코드 뒤에 .KS를 붙여야 데이터가 나옵니다
    search_symbol = f"{symbol}.KS" if symbol.isdigit() and len(symbol) == 6 else symbol
    data = yf.download(search_symbol, period="1y")
    
    # 코스피(.KS)에서 실패하면 코스닥(.KQ)으로 재시도
    if data.empty and symbol.isdigit():
        data = yf.download(f"{symbol}.KQ", period="1y")

    if not data.empty:
        # 데이터 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high, low = float(data['High'].max()), float(data['Low'].min())
        curr_p = float(data['Close'].iloc[-1])
        diff = high - low
        loss_rate = ((curr_p / avg_price) - 1) * 100 if avg_price > 0 else 0

        # 4. 상단 요약 (숫자 잘림 방지 포맷 적용)
        c1, c2, c3, c4 = st.columns(4)
        fmt = ",.0f" if currency == "₩" else ",.2f"
        c1.metric("현재가", f"{currency}{curr_p:{fmt}}")
        c2.metric("나의 평단가", f"{currency}{avg_price:{fmt}}")
        c3.metric("수익률", f"{loss_rate:.2f}%")
        c4.metric("60일선", f"{currency}{data['MA60'].iloc[-1]:{fmt}}")

        st.divider()

        # 5. 전략 지시서 및 차트 (에러 지점들 전수 수정)
        st.subheader(f"🚩 {selected_name} 전황 보고")
        f05, f0618 = high - (0.5 * diff), high - (0.618 * diff)
        
        col1, col2 = st.columns(2)
        with col1:
            if curr_p <= f0618: st.error(f"📍 [추매] 지지선({f0618:{fmt}}) 도달!")
            elif curr_p <= f05: st.warning(f"📍 [대기] 중기 지지선({f05:{fmt}}) 부근!")
            else: st.info("📍 [관망] 전황 안정적")
        
        with col2:
            if avg_price > 0:
                if loss_rate > -10: st.success("✅ [보유] 진지 견
