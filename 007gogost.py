import streamlit as st
import yfinance as yf
import numpy as np
from datetime import date 


hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




st.title("📈 株式リターン分析")

# ===== サイドバーで入力 =====
st.sidebar.header("設定")
ticker = st.sidebar.text_input("ティッカーシンボル", value="8593.T")
start_date = st.sidebar.date_input("開始日", value=date(2023, 1, 1)) 
end_date = st.sidebar.date_input("終了日", value=date(2026, 2, 4)) 
risk_free_rate = st.sidebar.number_input("無リスク金利（年率 %）", value=0.1, step=0.1) / 100

if st.sidebar.button("分析実行"):
    with st.spinner("データ取得中..."):
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            auto_adjust=True
        )

    if data.empty:
        st.error("データが取得できませんでした。ティッカーシンボルを確認してください。")
    else:
        close = data["Close"]
        returns = close.pct_change().dropna()

        expected_return = returns.mean().item()
        variance = returns.var().item()
        std_dev = returns.std().item()

        annual_return = expected_return * 252
        annual_vol = std_dev * np.sqrt(252)
        sharpe_ratio = (annual_return - risk_free_rate) / annual_vol

        cumulative_return = ((1 + returns).prod() - 1).item()
        days = (close.index[-1] - close.index[0]).days
        years = days / 365.25
        cagr = (1 + cumulative_return) ** (1 / years) - 1

        # ===== 日次統計 =====
        st.subheader("📊 日次統計")
        col1, col2, col3 = st.columns(3)
        col1.metric("期待リターン（日次）", f"{expected_return*100:.4f}%")
        col2.metric("標準偏差（日次）", f"{std_dev*100:.4f}%")
        col3.metric("分散", f"{variance:.6f}")

        # ===== 年率統計 =====
        st.subheader("📅 年率統計")
        col4, col5, col6 = st.columns(3)
        col4.metric("期待リターン（年率）", f"{annual_return*100:.2f}%")
        col5.metric("年率ボラティリティ", f"{annual_vol*100:.2f}%")
        col6.metric("sharpe_ratio", f"{sharpe_ratio:.4f}")

        # ===== 複利ベース =====
        st.subheader("💹 複利ベース")
        col7, col8, col9 = st.columns(3)
        col7.metric("累積リターン", f"{cumulative_return*100:.2f}%")
        col8.metric("投資期間", f"{years:.2f} 年")
        col9.metric("CAGR（年率複利）", f"{cagr*100:.2f}%")

        # ===== 株価チャート =====
        st.subheader("📈 株価推移")
        st.line_chart(close)

        # ===== 日次リターンチャート =====
        st.subheader("📉 日次リターン推移")
        st.line_chart(returns)

