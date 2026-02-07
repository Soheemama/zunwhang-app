import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.title("🛡️ 주식 전황 및 의사결정 지원 시스템")

# 1. 설정 및 데이터 로드
symbol = st.sidebar.text_input("종목 코드 입력", "GOOGL").upper()
avg_price = st.sidebar.number_input("나의 평단가 ($)", value=341.0) # 마마님 평단가 입력

if symbol:
    data = yf.download(symbol, period="1y")
    
    if not data.empty:
        # 주요 지표 계산
        high = float(data['High'].max())
        low = float(data['Low'].min())
        curr = float(data['Close'].iloc[-1])
        diff = high - low
        loss_rate = ((curr / avg_price) - 1) * 100 # 수익률/손실률

        # 2. 상단 요약 지표
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"${curr:.2f}")
        c2.metric("나의 평단가", f"${avg_price:.2f}")
        c3.metric("현재 수익률", f"{loss_rate:.2f}%", delta_color="inverse")
        c4.metric("최근 고점", f"${high:.2f}")

        st.divider()

        # 3. ★ 핵심 전략 요약 (거래량 숫자 대신 배치) ★
        st.subheader("🚩 서바이벌 전략 지시서")
        
        # 지지선 계산
        f05 = high - (0.5 * diff)
        f0618 = high - (0.618 * diff)

        advice_col1, advice_col2 = st.columns(2)
        
        with advice_col1:
            if curr <= f0618:
                st.error(f"⚠️ [강력 매수/보유] 강력 지지선(${f0618:.2f}) 도달! 손절보다는 반등을 노려 비중 확대를 검토할 시점입니다.")
            elif curr <= f05:
                st.warning(f"🟡 [분할 매수] 중기 지지선(${f05:.2f}) 부근입니다. 하락이 멈추는 것을 확인하며 천천히 추가매수를 진행하세요.")
            else:
                st.info("⚪ [관망] 아직 주요 지지선 위에 있습니다. 성급한 추가매수보다는 주가 흐름을 더 지켜보세요.")

        with advice_col2:
            if loss_rate <= -15: # 예시: 손실 15% 이상일 때
                st.error("🆘 [위험 관리] 손실이 깊어지고 있습니다. 120일선 이탈 시 기계적인 손절 혹은 비중 축소를 고려하십시오.")
            else:
                st.success("✅ [보유 유지] 현재 전황은 감
