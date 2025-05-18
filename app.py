import streamlit as st
import pandas as pd
import calendar
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="📊 Seasonality Demo", layout="wide", page_icon="📈")

# List of 5 popular US stocks (you can replace with any tickers)
stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

@st.cache_data(show_spinner=False)
def fetch_stock_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No data found for ticker '{ticker}' or date range.")
    df.reset_index(inplace=True)
    df = df[['Date', 'Close']]
    df.rename(columns={'Close': 'Price'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df['Daily Return %'] = df['Price'].pct_change() * 100
    return df

def calculate_seasonality(df):
    monthly_avg = df['Daily Return %'].groupby(df.index.month).mean()
    monthly_avg.index.name = 'Month'
    monthly_avg.name = 'Avg Monthly Return (%)'
    return monthly_avg

def plot_seasonality_chart(monthly_avg, ticker):
    months = list(calendar.month_abbr)[1:]
    data = monthly_avg.reindex(range(1, 13)).fillna(0).values

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=data,
        mode='lines+markers',
        line=dict(color='lime', width=2),
        marker=dict(size=8),
        name='Avg Monthly Return %'
    ))
    fig.update_layout(
        title=f"Seasonality Chart: {ticker}",
        xaxis_title="Month",
        yaxis_title="Average Monthly Return (%)",
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="#fafafa"),
        yaxis=dict(ticksuffix="%")
    )
    st.plotly_chart(fig, use_container_width=True)

st.title("📊 Seasonality Charts for 5 Sample Stocks")

start_date = st.date_input("Start Date", value=pd.to_datetime("2015-01-01"))
end_date = st.date_input("End Date", value=pd.to_datetime("today"))

for ticker in stocks:
    st.header(ticker)
    try:
        df = fetch_stock_data(ticker, start_date, end_date)
        monthly_avg = calculate_seasonality(df)
        plot_seasonality_chart(monthly_avg, ticker)
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
