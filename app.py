import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("📈 Quant Trading Dashboard")

ticker = st.text_input("Enter Stock Ticker", "AAPL")
period = st.selectbox("Select Time Period", ["6mo", "1y", "2y"])

data = yf.download(ticker, period=period)

data["Returns"] = data["Close"].pct_change()
data["Strategy"] = np.where(data["Returns"] > 0, 1, -1)
data["Strategy_Returns"] = data["Returns"] * data["Strategy"]

pnl = data["Strategy_Returns"].sum()
sharpe = (data["Strategy_Returns"].mean() / data["Strategy_Returns"].std()) * np.sqrt(252)
drawdown = (data["Strategy_Returns"].cumsum().cummax() - data["Strategy_Returns"].cumsum()).max()

st.subheader("Price Chart")
st.line_chart(data["Close"])

st.subheader("Strategy Returns")
st.line_chart(data["Strategy_Returns"].cumsum())

st.subheader("Performance Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total P&L", round(pnl, 4))
col2.metric("Sharpe Ratio", round(sharpe, 2))
col3.metric("Max Drawdown", round(drawdown, 4))
