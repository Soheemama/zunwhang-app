import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 의사결정 지원 시스템")

# 1. ★ 마마님의 비밀 장부 (한글 이름과 티커 매칭) ★
# 리스트에서 보여줄 순서대로 정리했습니다.
my_portfolio = {
    "GRID": {"name": "GRID ETF (그리드)", "price": 156.05},
    "URA": {"name": "URA ETF (우라늄)", "price": 51.93},
    "PL": {"name": "팔란티어 (PL)", "price": 23.3},
    "ALAB": {"name": "아스테라 랩스 (ALAB)", "price": 179.8525},
    "GOOGL": {"name": "구글 (GOOGL)", "price": 341.9194},
    "RKLB": {"name": "로켓랩 (RKLB)", "price": 78.5850},
    "QBTS": {"name": "디웨이브 퀀텀 (QBTS)", "price": 28.68},
    "445380": {"name": "HANARO K-반도체", "price": 20232},
    "475370": {"name": "SOL AI반도체소부장", "price": 19330},
    "465540": {"name": "SOL 전고체배터리", "price": 16968},
    "475380": {"name": "TIGER 휴머노이드", "price": 13026},
    "415480": {"name": "TIGER 현대차그룹+", "price": 55794},
    "159400": {"name": "KODEX 코스닥150", "price": 19540},
    "466920": {"name": "SOL 조선 TOP3", "price": 38282}
}

# 2. ★ 사이드바: 종목 선택 리스트 (Selectbox) ★
# 명단에서 이름을 추출하여 선택 메뉴를 만듭니다.
stock_names = [info['name'] for info in my_portfolio.values()]
selected_name = st.sidebar.selectbox("감시 종목 선택", stock_names)

# 선택한 이름에 해당하는 티커(Symbol) 찾기
symbol = ""
for ticker, info in my_portfolio.items():
    if info['name'] == selected_name:
        symbol = ticker
        break

# 평단가 자동 세팅
default_price = my_portfolio.get(symbol, {}).get("price", 0.0)
avg_price = st.sidebar.number_input(f"[{symbol}] 나의 평단가", value=float(default_price))

if symbol:
    # 한국 종목 처리
    search_symbol = f"{symbol}.KS" if symbol.isdigit() and len(symbol) == 6 else symbol
    data = yf.download(search_symbol, period="1y")
    
    if not data.empty:
        # 주요 수치 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high, low = float(data['High'].max()), float(data['Low'].min())
        curr = float(data['Close'].iloc[-1])
        diff = high - low
        loss_rate = ((curr / avg_price) - 1) * 100 if avg_price > 0 else 0

        # 상단 요약
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{curr:,.2f}")
        c2.metric("평단가", f"{avg_price:,.2f}")
        c3.metric("수익률", f"{loss_rate:.2f}%")
        c4.metric("최근 고점", f"{high:,.2f}")

        st.divider()

        # 3. 전략 지시서
        st.subheader(f"🚩 {selected_name} 전황 보고")
        f05, f0618 = high - (0.5 * diff), high - (0.618 * diff)
        col1, col2 = st.columns(2)
        with col1:
            if curr <= f0618: st.error(f"📍 [강력 추매] 지지선({f0618:,.2f}) 도달!")
            elif curr <= f05: st.warning(f"📍 [분할 추매] 중기 지지선({f05:,.2f}) 부근!")
            else: st.info("📍 [관망] 전황이 안정적입니다.")
        with col2:
            if avg_price > 0:
                if loss_rate > -10: st.success("✅ [보유] 진지가 견고합니다.")
                else: st.error("🆘 [위험] 손절 혹은 비중 축소 검토!")

        # 4. 그래프 (5중 피보나치 + 이평선)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=1.5)))

        # 피보나치 5선
        m2 = high * 0.98
        fig.add_hline(y=m2, line_dash="dot", line_color="yellow", annotation_text=f"-2% ({m2:,.2f})")
        for lvl, clr in [(0.236, "green"), (0.382, "cyan"), (0.5, "red"), (0.618, "magenta")]:
            val = high - (lvl * diff)
            fig.add_hline(y=val, line_dash="dash", line_color=clr, annotation_text=f"Fibo {lvl} ({val:,.2f})")

        fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
