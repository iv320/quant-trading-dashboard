
# STEP 0: Import required libraries

import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf



# STEP 1: Page configuration (layout & title)

st.set_page_config(layout="wide")
st.title("Real-Time Quant Trading Dashboard")



# STEP 2: Sidebar – User Inputs

st.sidebar.header("User Inputs")

# Stock ticker input
ticker = st.sidebar.text_input("Enter Stock Ticker", "AAPL")

# Date inputs
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")



# STEP 3: Download stock market data

data = None  # Initialize variable

# Download data only if all inputs are present
if ticker and start_date and end_date:
    data = yf.download(
        ticker,
        start=start_date,
        end=end_date
    )



# STEP 4: Clean yfinance data (MultiIndex fix)

# Sometimes yfinance returns MultiIndex columns
if data is not None and not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)



# STEP 5: Display Raw Stock Market Data

if data is not None and not data.empty:
    st.subheader("Raw Stock Market Data")
    st.dataframe(data)
else:
    st.warning("No data available. Please select a valid past date range.")
    st.stop()   # Stop execution if no data



# STEP 6: Closing Price Trend

st.subheader("Closing Price Trend")
st.line_chart(data["Close"])



# STEP 7: Calculate Moving Averages

st.subheader("Moving Averages")

# 20-day Moving Average
data["MA20"] = data["Close"].rolling(window=20).mean()

# 50-day Moving Average
data["MA50"] = data["Close"].rolling(window=50).mean()

# Plot Close price + Moving Averages
st.line_chart(data[["Close", "MA20", "MA50"]])



# STEP 8: Generate Trading Signals

st.subheader("Trading Signals")

# Initialize signal column
data["Signal"] = 0

# Buy signal → MA20 crosses above MA50
data.loc[data["MA20"] > data["MA50"], "Signal"] = 1

# Sell signal → MA20 crosses below MA50
data.loc[data["MA20"] < data["MA50"], "Signal"] = -1

# Display signal table
st.dataframe(data[["Close", "MA20", "MA50", "Signal"]])


# STEP 9: Calculate Daily Returns

st.subheader("Daily Returns")

data["Daily_Return"] = data["Close"].pct_change()

# Visualize Daily Returns
st.line_chart(data["Daily_Return"])


# STEP 10: Calculate Strategy Returns

st.subheader("Strategy Returns")

data["Strategy_Return"] = data["Daily_Return"] * data["Signal"].shift(1)

# Visualize Strategy Returns
st.line_chart(data["Strategy_Return"])


# STEP 11: Calculate Cumulative Returns

st.subheader("Cumulative Returns")

# Buy & Hold cumulative return
data["Market_Cumulative_Return"] = (1 + data["Daily_Return"]).cumprod()

# Strategy cumulative return
data["Strategy_Cumulative_Return"] = (1 + data["Strategy_Return"]).cumprod()

# Visualize Cumulative Returns
st.line_chart(
    data[["Market_Cumulative_Return", "Strategy_Cumulative_Return"]]
)


# STEP 12: Profit & Loss (P&L)

st.subheader("Profit & Loss (P&L)")

# Assume initial capital
initial_capital = 100000  # ₹1,00,000

# Daily P&L
data["Daily_P&L"] = initial_capital * data["Strategy_Return"]

# Cumulative P&L
data["Cumulative_P&L"] = data["Daily_P&L"].cumsum()

# Display P&L chart
st.line_chart(data["Cumulative_P&L"])

# Display final profit/loss
final_pnl = data["Cumulative_P&L"].iloc[-1]
final_capital = initial_capital + final_pnl

st.metric("Final P&L (₹)", round(final_pnl, 2))
st.metric("Final Portfolio Value (₹)", round(final_capital, 2))


# STEP 13: Sharpe Ratio (Risk-Adjusted Return)

st.subheader("Risk Metrics")

sharpe_ratio = (
    data["Strategy_Return"].mean() /
    data["Strategy_Return"].std()
) * np.sqrt(252)

# Calculate drawdown
rolling_max = data["Strategy_Cumulative_Return"].cummax()
drawdown = data["Strategy_Cumulative_Return"] / rolling_max - 1
max_drawdown = drawdown.min()

# Display Risk Metrics
st.metric("Sharpe Ratio", round(sharpe_ratio, 2))
st.metric("Maximum Drawdown", round(max_drawdown, 2))

