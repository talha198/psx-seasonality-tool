import streamlit as st
import pandas as pd
import calendar
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import yfinance as yf
import random

st.set_page_config(page_title="📊 PSX SEASONX", layout="wide", page_icon="📈")

# --- CSS for styling (add your existing CSS here or adjust as needed) ---
st.markdown("""
<style>
.title-container {
    text-align: center;
    margin-bottom: 1rem;
}
.return-positive {
    color: green;
    font-weight: bold;
}
.return-negative {
    color: red;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ------------------ Header ------------------
st.markdown("""
<div class='title-container'>
    <h1>📊 PSX SEASONX</h1>
    <p style='text-align:center; margin-top:-10px;'>Pakistan Stock Seasonality Intelligence Tool</p>
</div>
""", unsafe_allow_html=True)

# ------------------ Sidebar ------------------
st.sidebar.title("🔧 Settings & Filters")

# Your watchlist for ticker suggestions
watchlist = [
    "TRG.PK", "HBL.PK", "OGDC.PK", "UBL.PK", "MARI.PK", "SNGP.PK", "PSO.PK", "KEL.PK", "FSL.PK"
]

# Text input for ticker
stock_ticker = st.sidebar.text_input("Enter Stock Ticker", value="TRG.PK")

# Show random suggestion if user typed at least 1 char
if len(stock_ticker.strip()) >= 1:
    suggestion = random.choice(watchlist)
    st.sidebar.markdown(f"**Suggestion:** {suggestion}")
    if st.sidebar.button(f"Use Suggested Ticker: {suggestion}"):
        # When user clicks button, update stock_ticker via session state and rerun
        st.session_state['stock_ticker'] = suggestion
        st.experimental_rerun()

# Keep stock_ticker from session state if available (for button click to persist)
if 'stock_ticker' in st.session_state:
    stock_ticker = st.session_state['stock_ticker']

start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2015-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))
st.sidebar.markdown("---")
st.sidebar.write("⚙️ *Filters coming soon...*")

# ------------------ Functions ------------------

@st.cache_data(show_spinner=False)
def fetch_stock_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    df.reset_index(inplace=True)
    df = df[['Date', 'Close']]
    df.rename(columns={'Close': 'Price'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df['Daily Return %'] = df['Price'].pct_change() * 100
    return df

def calculate_seasonality(df):
    # Calculate average monthly returns
    df['Month'] = df.index.month
    monthly_avg = df.groupby('Month')['Daily Return %'].mean()
    return monthly_avg

def analyze_favorable_times(df, monthly_avg):
    buy_months = monthly_avg[monthly_avg > 0].index.tolist()
    sell_months = monthly_avg[monthly_avg <= 0].index.tolist()

    buy_month_names = [calendar.month_name[m] for m in buy_months]
    sell_month_names = [calendar.month_name[m] for m in sell_months]

    # Simple return: sum of monthly returns of buy months
    simple_return_pct = monthly_avg[buy_months].sum()
    simple_profit = 100000 * simple_return_pct / 100

    # Compound return simulation
    compound_return = 1.0
    for m in buy_months:
        compound_return *= (1 + monthly_avg[m] / 100)
    compound_return_pct = (compound_return - 1) * 100
    compound_profit = 100000 * compound_return_pct / 100

    # Upcoming favorable buy months (from current month)
    current_month = datetime.now().month
    upcoming_buy_months = [m for m in buy_months if m >= current_month]
    upcoming_buy_names = [calendar.month_name[m] for m in upcoming_buy_months]

    return {
        'buy_months': buy_months,
        'sell_months': sell_months,
        'buy_month_names': buy_month_names,
        'sell_month_names': sell_month_names,
        'simple_return_pct': simple_return_pct,
        'simple_profit': simple_profit,
        'compound_return_pct': compound_return_pct,
        'compound_profit': compound_profit,
        'upcoming_buy_names': upcoming_buy_names
    }

def plot_price_chart(df, ticker):
    fig = px.line(df, y='Price', title=f"Price Chart for {ticker.upper()}")
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

def plot_seasonality_chart(monthly_avg, ticker):
    months = [calendar.month_name[m] for m in monthly_avg.index]
    returns = monthly_avg.values
    fig = go.Figure(data=[
        go.Bar(x=months, y=returns, marker_color=['green' if x > 0 else 'red' for x in returns])
    ])
    fig.update_layout(title=f"Seasonality (Avg Monthly Returns %) for {ticker.upper()}",
                      xaxis_title="Month", yaxis_title="Avg Monthly Return (%)",
                      margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

def download_link(df):
    csv = df.to_csv(index=False)
    st.download_button(label="Download Seasonality Data as CSV", data=csv, file_name="seasonality_data.csv", mime='text/csv')

# ------------------ Main ------------------

if stock_ticker:
    with st.spinner(f"Fetching data for {stock_ticker} ..."):
        try:
            df = fetch_stock_data(stock_ticker, start_date, end_date)
            if df.empty:
                st.error("No data found for this ticker or date range. Please check the ticker symbol or date.")
            else:
                monthly_avg = calculate_seasonality(df)
                results = analyze_favorable_times(df, monthly_avg)

                # Display Summary
                st.subheader(f"📈 Seasonality Summary for {stock_ticker.upper()}")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Favorable Buy Months:** {', '.join(results['buy_month_names']) if results['buy_month_names'] else 'None'}")
                    st.markdown(f"**Favorable Sell Months:** {', '.join(results['sell_month_names']) if results['sell_month_names'] else 'None'}")
                    st.markdown(f"**Upcoming Favorable Buy Months:** {', '.join(results['upcoming_buy_names']) if results['upcoming_buy_names'] else 'None'}")

                with col2:
                    simple_class = "return-positive" if results['simple_return_pct'] >= 0 else "return-negative"
                    st.markdown(f"<span class='{simple_class}'>Demo Return (Simple Sum): {results['simple_return_pct']:.2f}%</span>", unsafe_allow_html=True)
                    st.markdown(f"Profit on 100,000 PKR: {results['simple_profit']:.2f} PKR")

                    compound_class = "return-positive" if results['compound_return_pct'] >= 0 else "return-negative"
                    st.markdown(f"<span class='{compound_class}'>Compound Return (Simulated): {results['compound_return_pct']:.2f}%</span>", unsafe_allow_html=True)
                    st.markdown(f"Profit on 100,000 PKR: {results['compound_profit']:.2f} PKR")

                st.markdown("---")

                # Show Charts
                with st.container():
                    st.markdown("### Price Chart")
                    plot_price_chart(df, stock_ticker)

                with st.container():
                    st.markdown("### Seasonality Chart")
                    plot_seasonality_chart(monthly_avg, stock_ticker)

                # Prepare seasonality data for download
                monthly_df = monthly_avg.rename_axis('Month').reset_index()
                monthly_df['Month_Name'] = monthly_df['Month'].apply(lambda x: calendar.month_name[x])
                monthly_df = monthly_df[['Month', 'Month_Name', 'Daily Return %']]
                monthly_df.rename(columns={'Daily Return %': 'Avg Monthly Return (%)'}, inplace=True)

                download_link(monthly_df)

        except Exception as e:
            st.error(f"Error fetching data: {e}")

else:
    st.info("Enter a stock ticker symbol (e.g. TRG.PK) in the sidebar to get started.")

# ------------------ Footer ------------------
st.markdown("""
<div style='text-align:center; margin-top:3rem; color:#666; font-size:12px;'>
    © 2025 PSX SEASONX | Developed by YourName
</div>
""", unsafe_allow_html=True)
