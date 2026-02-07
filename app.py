import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 의사결정 지원 시스템")

# 1. ★ 마마님의 비밀 장부 (평단가 데이터 명부) ★
my_portfolio = {
    "GRID": 156.05, "URA": 51.93, "PL": 23.3, "ALAB": 179.8525,
    "GOOGL": 341.9194, "RKLB": 78.5850, "QBTS": 28.68,
    "159400": 19540, "466920": 38282, "475380": 13026,
    "475370": 19330, "465540": 16968, "445380": 20232, "415480": 55794
}

# 2. 사이드바 설정
symbol = st.sidebar.text_input("종목 코드 입력", "GRID").upper()
default_price = my_portfolio.get(symbol, 0.0)
avg_price = st.sidebar.number_input(f"{symbol} 나의 평단가", value=float(default_price))

if symbol:
    # 한국 종목/미국 종목 구분 처리
    search_symbol = f"{symbol}.KS" if symbol.isdigit() and len(symbol) == 6 else symbol
    
    # 데이터 가져오기
    data = yf.download(search_symbol, period="1y")
    
    if not data.empty:
        # 주요 수치 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high = float(data['High'].max())
        low = float(data['Low'].min())
        curr = float(data['Close'].iloc[-1])
        diff = high - low
        loss_rate = ((curr / avg_price) - 1) * 100 if avg_price > 0 else 0

        # 상단 요약 지표 (괄호 및 구문 에러 완전 수정)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{curr:,.2f}")
        c2.metric("평단가", f"{avg_price:,.2f}")
        c3.metric("수익률", f"{loss_rate:.2f}%")
        c4.metric("최근 고점", f"{high:,.2f}")

        st.divider()

        # 3. 전략 지시서
        st.subheader("🚩 전황 분석 보고")
        f05 = high - (0.5 * diff)
        f0618 = high - (0.618 * diff)

        col1, col2 = st.columns(2)
        with col1:
            if curr <= f0618: st.error(f"📍 [강력 추매] 지지선({f0618:,.2f}) 도달!")
            elif curr <= f05: st.warning(f"📍 [분할 추매] 중기 지지선({f05:,.2f}) 부근!")
            else: st.info("📍 [관망] 전황이 아직 안정적입니다.")
        with col2:
            if avg_price > 0:
                if loss_rate > -10: st.success("✅ [보유] 진지가 견고합니다.")
                else: st.error("🆘 [위험] 손절 혹은 비중 축소 검토!")

        # 4. ★ 그래프 복구 (Plotly 차트) ★
        fig = go.Figure()
        
        # 캔들차트
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name="주가"
        ))
        
        # 이평선 추가
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=1.5)))

        # 피보나치 지지선 (0.5, 0.618)
        fig.add_hline(y=f05, line_dash="dash", line_color="red", annotation_text=f"0.5 ({f05:,.2f})")
        fig.add_hline(y=f0618, line_dash="dashdot", line_color="magenta", annotation_text=f"0.618 ({f0618:,.2f})")

        # 레이아웃 설정 (Rangeslider 제거로 깔끔하게)
        fig.update_layout(
            height=600, 
            template="plotly_dark", 
            xaxis_rangeslider_visible=False, 
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("데이터를 불러올 수 없습니다. 종목 코드(티커)를 확인해 주세요.")
