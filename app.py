import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 의사결정 지원 시스템")

# 1. 사이드바 설정
symbol = st.sidebar.text_input("종목 코드 입력", "GOOGL").upper()
avg_price = st.sidebar.number_input("나의 평단가 ($)", value=341.0)

if symbol:
    data = yf.download(symbol, period="1y")
    
    if not data.empty:
        # 데이터 및 이평선 계산
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        high = float(data['High'].max())
        low = float(data['Low'].min())
        curr = float(data['Close'].iloc[-1])
        diff = high - low
        loss_rate = ((curr / avg_price) - 1) * 100

        # 상단 핵심 지표
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"${curr:.2f}")
        c2.metric("나의 평단가", f"${avg_price:.2f}")
        c3.metric("60일 이평선", f"${data['MA60'].iloc[-1]:.2f}")
        c4.metric("120일 이평선", f"${data['MA120'].iloc[-1]:.2f}")

        st.divider()

        # 2. ★ 서바이벌 전략 지표 (메시지 에러 수정 완료) ★
        st.subheader("🚩 서바이벌 전략 지표")
        f05 = high - (0.5 * diff)
        f0618 = high - (0.618 * diff)

        col1, col2 = st.columns(2)
        with col1:
            if curr <= f0618:
                st.error(f"📍 [추가매수 검토] 강력 지지선(${f0618:.2f}) 도달! 비중 확대 구간입니다.")
            elif curr <= f05:
                st.warning(f"📍 [분할 매수 준비] 중기 지지선(${f05:.2f}) 부근입니다.")
            else:
                st.info("📍 [관망 유지] 아직 지지선 위입니다. 성급한 추격매수는 금물입니다.")
        
        with col2:
            # 로그 폭사 현상을 막기 위해 조건문을 명확히 한 줄로 정리
            if loss_rate > -10:
                st.success(f"✅ [보유 유지] 현재 수익률 {loss_rate:.2f}%로 전황은 감내 가능합니다.")
            else:
                st.error(f"🆘 [위험 관리] 현재 수익률 {loss_rate:.2f}%입니다. 손절을 신중히 검토하십시오.")

        st.divider()

        # 3. ★ 차트 지표 (이평선 + 피보나치 5종) ★
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="주가"))
        
        # 이평선 추가
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name="60일선", line=dict(color='royalblue', width=1.5)))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA120'], name="120일선", line=dict(color='orange', width=1.5)))

        # 피보나치 전선 및 가격 표시
        m2 = high * 0.98
        fig.add_hline(y=m2, line_dash="dot", line_color="yellow", annotation_text=f"-2% (${m2:.2f})")
        
        f_levels = [(0.236, "green"), (0.382, "cyan"), (0.5, "red"), (0.618, "magenta")]
        for lvl, clr in f_levels:
            val = high - (lvl * diff)
            fig.add_hline(y=val, line_dash="dash", line_color=clr, annotation_text=f"Fibo {lvl} (${val:.2f})")

        fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("데이터 로드 실패")
