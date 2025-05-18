import streamlit as st
import pandas as pd
import calendar
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import yfinance as yf
import base64

st.set_page_config(page_title="📊 PSX SEASONX", layout="wide", page_icon="📈")

# --- CSS ---
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #fafafa;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.title-container h1 {
    font-weight: 700;
    font-size: 3rem;
    color: lime;
    text-shadow: 0 0 5px lime;
}
.return-positive {
    color: #32CD32;
    font-weight: 600;
}
.return-negative {
    color: #FF6347;
    font-weight: 600;
}
.card {
    background-color: #1c1f26;
    padding: 20px;
    margin-bottom: 30px;
    border-radius: 15px;
    box-shadow: 0 0 10px lime;
}
hr {
    border: 1px solid lime;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class='title-container'>
    <h1>📊 PSX SEASONX</h1>
    <p style='text-align:center; margin-top:-10px;'>Pakistan Stock Seasonality Intelligence Tool</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🔧 Settings & Filters")

tickers_input = st.sidebar.text_area("Enter up to 5 PSX Tickers (one per line)", value="TRG\nOGDC\nPSO\nHBL\nLUCK")
tickers = [ticker.strip().upper().replace(".PK", "").replace(".KA", "") + ".KA" for ticker in tickers_input.splitlines()[:5]]

start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2015-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

# --- Functions ---

@st.cache_data(show_spinner=False)
def fetch_stock_data(ticker, start, end):
    if start >= end:
        raise ValueError("Start date must be before end date.")
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
    monthly_avg.name = 'Daily Return %'
    return monthly_avg

def get_first_price_of_month(df):
    return df['Price'].resample('MS').first()

def analyze_favorable_times(df, monthly_avg):
    buy_months = monthly_avg[monthly_avg > 0].index.tolist()
    sell_months = monthly_avg[monthly_avg <= 0].index.tolist()
    buy_month_names = [calendar.month_name[m] for m in buy_months]
    sell_month_names = [calendar.month_name[m] for m in sell_months]

    simple_return_pct = monthly_avg.loc[buy_months].sum() if buy_months else 0
    simple_profit = 100000 * simple_return_pct / 100

    first_prices = get_first_price_of_month(df)
    compound_profit = 100000

    if not first_prices.empty and buy_months:
        for year in first_prices.index.year.unique():
            year_month_prices = first_prices[(first_prices.index.year == year) & (first_prices.index.month.isin(buy_months))]
            if len(year_month_prices) < 2:
                continue
            for i in range(1, len(year_month_prices)):
                ret = (year_month_prices.iloc[i] - year_month_prices.iloc[i-1]) / year_month_prices.iloc[i-1]
                compound_profit *= (1 + ret)

    compound_return_pct = ((compound_profit - 100000) / 100000) * 100

    today_month = datetime.today().month
    upcoming_buy_months = [m for m in buy_months if m >= today_month]
    upcoming_buy_names = [calendar.month_name[m] for m in upcoming_buy_months]

    return {
        'buy_months': buy_months,
        'sell_months': sell_months,
        'buy_month_names': buy_month_names,
        'sell_month_names': sell_month_names,
        'simple_return_pct': simple_return_pct,
        'simple_profit': simple_profit,
        'compound_return_pct': compound_return_pct,
        'compound_profit': compound_profit - 100000,
        'upcoming_buy_names': upcoming_buy_names,
    }

def plot_price_chart(df, ticker):
    fig = px.line(df.reset_index(), x='Date', y='Price', title=f"Price Chart: {ticker}")
    fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font=dict(color="#fafafa"))
    st.plotly_chart(fig, use_container_width=True)

def plot_seasonality_chart(monthly_avg, ticker):
    months = list(calendar.month_abbr)[1:]
    data = monthly_avg.reindex(range(1, 13)).fillna(0).values
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=data, mode='lines+markers',
        line=dict(color='lime', width=2), marker=dict(size=8),
        name='Avg Monthly Return %'
    ))
    fig.update_layout(
        title=f"Seasonality Chart: {ticker}",
        xaxis_title="Month", yaxis_title="Average Monthly Return (%)",
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font=dict(color="#fafafa"), yaxis=dict(ticksuffix="%")
    )
    st.plotly_chart(fig, use_container_width=True)

def download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="seasonality_data.csv">📥 Download Seasonality Data as CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

def display_seasonality_for_ticker(ticker, start, end):
    df = fetch_stock_data(ticker, start, end)
    monthly_avg = calculate_seasonality(df)
    results = analyze_favorable_times(df, monthly_avg)

    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"## 📊 {ticker.replace('.KA', '')} — Seasonality Summary", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**✅ Favorable Buy Months:** {', '.join(results['buy_month_names']) or 'None'}")
        st.markdown(f"**❌ Unfavorable Sell Months:** {', '.join(results['sell_month_names']) or 'None'}")
        st.markdown(f"**🕒 Upcoming Buy Months:** {', '.join(results['upcoming_buy_names']) or 'None'}")

    with col2:
        simple_class = "return-positive" if results['simple_return_pct'] >= 0 else "return-negative"
        st.markdown(f"<span class='{simple_class}'>Simple Return: {results['simple_return_pct']:.2f}%</span>", unsafe_allow_html=True)
        st.markdown(f"📈 Profit on 100,000 PKR: {results['simple_profit']:.2f} PKR")

        compound_class = "return-positive" if results['compound_return_pct'] >= 0 else "return-negative"
        st.markdown(f"<span class='{compound_class}'>Compound Return: {results['compound_return_pct']:.2f}%</span>", unsafe_allow_html=True)
        st.markdown(f"💼 Profit on 100,000 PKR: {results['compound_profit']:.2f} PKR")

    st.markdown("### 📈 Price Chart")
    plot_price_chart(df, ticker)

    st.markdown("### 📊 Seasonality Chart")
    plot_seasonality_chart(monthly_avg, ticker)

    st.markdown("### 🔮 Forward-Looking Forecast (Next 6 Months)")
    today_month = datetime.today().month
    next_6_months = [(today_month + i - 1) % 12 + 1 for i in range(6)]
    forecast_returns = monthly_avg.reindex(next_6_months).fillna(0).values
    forecast_month_names = [calendar.month_name[m] for m in next_6_months]

    forecast_df = pd.DataFrame({
        'Month': forecast_month_names,
        'Avg Monthly Return (%)': forecast_returns
    })

    st.table(forecast_df.style.applymap(
        lambda v: 'color: #32CD32;' if v >= 0 else 'color: #FF6347;', subset=['Avg Monthly Return (%)']
    ))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=forecast_month_names, y=forecast_returns,
        marker_color=['lime' if x >= 0 else 'tomato' for x in forecast_returns]
    ))
    fig.update_layout(
        title=f"Forward-Looking Seasonality: {ticker}",
        xaxis_title="Month", yaxis_title="Avg Monthly Return (%)",
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font=dict(color="#fafafa"), yaxis=dict(ticksuffix="%")
    )
    st.plotly_chart(fig, use_container_width=True)

    monthly_df = monthly_avg.rename_axis('Month').reset_index()
    monthly_df['Month_Name'] = monthly_df['Month'].apply(lambda x: calendar.month_name[x])
    monthly_df = monthly_df[['Month', 'Month_Name', 'Daily Return %']]
    monthly_df.rename(columns={'Daily Return %': 'Avg Monthly Return (%)'}, inplace=True)
    download_link(monthly_df)

    st.markdown("</div>", unsafe_allow_html=True)

# --- Main Execution ---
for ticker in tickers:
    try:
        display_seasonality_for_ticker(ticker, start_date, end_date)
        st.markdown("<hr>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Error for {ticker}: {e}")
