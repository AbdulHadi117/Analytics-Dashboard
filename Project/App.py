# ------------------ IMPORTS ------------------ #
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

# ------------------ PAGE TITLE ------------------ #
st.title("📈 Stock Market Dashboard")
st.markdown("Track stock prices, volume, and visualize trends using Plotly and Streamlit.")

# ------------------ SIDEBAR ------------------ #
st.sidebar.header("Configuration")

default_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

# Ticker dropdown
ticker = st.sidebar.selectbox("Select a Stock Ticker", default_tickers, index=0)

# Date range
start_date = st.sidebar.date_input("Start Date", datetime(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.now().date())

# ------------------ FETCH DATA BUTTON ------------------ #
if st.sidebar.button("Fetch Data"):
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        st.error("No data found. Please check the ticker or date range.")
    else:
        df.reset_index(inplace=True)
        df.columns = [' '.join(col) if isinstance(col, tuple) else col for col in df.columns]
        df.columns = [col.replace(f' {ticker}', '').strip() for col in df.columns]

        # Store data and metadata in session state
        st.session_state['df'] = df
        st.session_state['ticker'] = ticker
        st.session_state['start_date'] = start_date
        st.session_state['end_date'] = end_date

# ------------------ DISPLAY DATA IF AVAILABLE ------------------ #
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
    ticker = st.session_state['ticker']

    # ----------- KPI SECTION ----------- #
    st.subheader(f"📊 Latest Summary for {ticker}")
    latest_data = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Close Price", f"${latest_data['Close']:.2f}")
    col2.metric("Volume", f"{int(latest_data['Volume']):,}")
    col3.metric("High / Low", f"${latest_data['High']:.2f} / ${latest_data['Low']:.2f}")

    st.markdown("---")

    # ----------- PLOT SECTION ----------- #
    numeric_cols = [c for c in df.columns if c != 'Date' and pd.api.types.is_numeric_dtype(df[c])]
    selected_col = st.selectbox("Select a column to visualize", numeric_cols, index=0)
    fig = px.line(df, x="Date", y=selected_col, title=f"{selected_col} Trend for {ticker}")
    st.plotly_chart(fig, use_container_width=True)

    # ----------- RAW DATA VIEW ----------- #
    with st.expander("🔍 Show Raw Data"):
        st.dataframe(df, use_container_width=True)

    # ----------- PREDICTIONS SECTION ----------- #
    st.header("📈 Stock Price Prediction (Simple Linear Model)")
    forecast_days = st.slider('Days to Forecast', min_value=1, max_value=30, value=7)

    df_pred = df.copy()
    df_pred['Days'] = np.arange(len(df_pred))
    X = df_pred[['Days']]
    y = df_pred['Close']
    model = LinearRegression().fit(X, y)
    future_days = np.arange(len(df_pred), len(df_pred) + forecast_days).reshape(-1, 1)
    future_preds = model.predict(future_days)

    pred_df = pd.DataFrame({
        'Date': pd.date_range(start=df_pred['Date'].iloc[-1] + timedelta(days=1), periods=forecast_days),
        'Predicted_Close': future_preds
    })

    fig_pred = px.line(pred_df, x='Date', y='Predicted_Close', title='🔮 Predicted Future Prices')
    st.plotly_chart(fig_pred)
else:
    st.info("⬅️ Please select a ticker and click 'Fetch Data' to begin.")
