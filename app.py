import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. 페이지 설정 및 숫자 잘림 방지를 위한 스타일 적용
st.set_page_config(page_title="소희마마 전용 전황 분석", layout="wide")
st.markdown("""
    <style>
    /* 숫자 크기를 최적화하여 원화 단위가 잘리지 않게 합니다 */
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
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
    "159400": {"name": "KODEX 코스닥150", "
