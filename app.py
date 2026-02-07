import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.title("🛡️ 한/미 통합 전황 및 의사결정 지원 시스템")

# 1. ★ 마마님의 비밀 장부 (통화 구분 추가) ★
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

# 2. 사이드바: 종목 선택 리스트
stock_names = [info['name'] for info in my_portfolio.values()]
selected_name = st.sidebar.selectbox("감시 종목 선택", stock_names)

# 선택한 종목의 정보 추출
symbol = ""
for s, info in my_portfolio.items():
    if info['name'] == selected_name:
        symbol = s
        currency = info['cur']
        break

default_price = my_portfolio.get(symbol, {}).get("price", 0.0)
avg_price = st.sidebar.number_input(f"[{symbol}] 나의 평단가 ({currency})", value=float(default_price))

if symbol:
    # ★ 한국 종목 티커 자동 완성 (유가증권 .KS / 코스닥 .KQ 등 구분) ★
    # 한국 종목(숫자 6자리)인 경우 야후파이낸스 규격에 맞춰 변환
    if symbol.isdigit() and len(symbol) == 6:
        # 대부분의 마마님 보유 ETF는 코스피/코스닥에 상장되어 있습니다.
        search_symbol = f"{symbol}.KS" 
    else:
        search_symbol = symbol

    data = yf.download(search_symbol, period="1y")
    
    # 만약 .KS로 안 나오면 .KQ로 한 번 더 시도 (안정성 강화)
    if data.empty and symbol.isdigit():
        search_symbol = f"{symbol}.KQ"
        data = yf.download(search_symbol, period="1y")

    if not data.empty:
        # 주요 수치 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high, low = float(data['High'].max()), float(data['Low'].min())
        curr_price = float(data['Close'].iloc[-1])
        diff = high - low
        loss_rate = ((curr_price / avg_price) - 1) * 100 if avg_price > 0 else 0

        # 상단 요약 (통화별 기호 적용)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{currency} {curr_price:,.0f}" if currency == "₩" else f"{currency} {curr_price:,.2f}")
        c2.metric("나의 평단가", f"{currency} {avg_price:,.0f}" if currency == "₩" else f"{currency} {avg_price:,.2f}")
        c3.metric("수익률", f"{loss_rate:.2f}%")
        c4.metric("60일선", f"{curr_price:,.0f}" if currency == "₩" else f"{curr_price:,.2f}")

        st.divider()

        # 3. 전략 지시서
        st.subheader(f"🚩 {selected_name} 전황 분석")
        f05, f0618 = high - (0.5 * diff), high - (0.618 * diff)
        col1, col2 = st.columns(2)
        with col1:
            if curr_price <= f0618: st.error(f"📍 [강력 추매] 지지선({f0618:,.0f}) 도달!")
            elif curr_price <= f05: st.warning(f"📍 [분할 추매] 중기 지지선({f05:,.0f}) 부근!")
            else: st.info("📍 [관망 유지] 아직 전황이 견고합니다.")
        with col2:
            if avg_price > 0:
                if loss_rate > -10: st.success("✅ [보유] 현재 진지를 사수하세요.")
                else: st.error("🆘 [위험] 비중 축소 및 후방 배치를 검토하세요.")

        # 4. 차트 (5중 피보나치 + 이평선)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=1.5)))

        # 피보나치 전선 표시
        m2 = high * 0.98
        fig.add_hline(y=m2, line_dash="dot", line_color="yellow", annotation_text=f"-2% ({m2:,.0f})")
        for lvl, clr in [(0.236, "green"), (0.382, "cyan"), (0.5, "red"), (0.618, "magenta")]:
            val = high - (lvl * diff)
            fig.add_hline(y=val, line_dash="dash", line_color=clr, annotation_text=f"Fibo {lvl} ({val:,.0f})")

        fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"데이터를 불러오지 못했습니다. [{symbol}] 코드를 확인해 주세요.")
