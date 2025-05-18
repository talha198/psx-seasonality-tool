import streamlit as st
import pandas as pd
import calendar
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import yfinance as yf

st.set_page_config(page_title="📊 PSX SEASONX", layout="wide", page_icon="📈")

# --- Your existing CSS here, unchanged ---

# Paste all your existing CSS here (same as your current style block) ...

# ------------------ Header ------------------
st.markdown("""
<div class='title-container'>
    <h1>📊 PSX SEASONX</h1>
    <p style='text-align:center; margin-top:-10px;'>Pakistan Stock Seasonality Intelligence Tool</p>
</div>
""", unsafe_allow_html=True)

# ------------------ Sidebar ------------------
st.sidebar.title("🔧 Settings & Filters")
stock_ticker = st.sidebar.text_input("Enter Stock Ticker", value="TRG.PK")  # example PSX ticker with .PK suffix
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

# Your existing functions: calculate_seasonality, get_first_price_of_month, analyze_favorable_times,
# plot_price_chart, plot_seasonality_chart, download_link remain unchanged but imported here.

# Paste your functions calculate_seasonality, get_first_price_of_month, analyze_favorable_times,
# plot_price_chart, plot_seasonality_chart, download_link here without change from your original code

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
                    # Simple Return
                    simple_class = "return-positive" if results['simple_return_pct'] >= 0 else "return-negative"
                    st.markdown(f"<span class='{simple_class}'>Demo Return (Simple Sum): {results['simple_return_pct']:.2f}%</span>", unsafe_allow_html=True)
                    st.markdown(f"Profit on 100,000 PKR: {results['simple_profit']:.2f} PKR")

                    # Compound Return
                    compound_class = "return-positive" if results['compound_return_pct'] >= 0 else "return-negative"
                    st.markdown(f"<span class='{compound_class}'>Compound Return (Simulated): {results['compound_return_pct']:.2f}%</span>", unsafe_allow_html=True)
                    st.markdown(f"Profit on 100,000 PKR: {results['compound_profit']:.2f} PKR")

                st.markdown("---")

                # Show Charts inside cards
                with st.container():
                    st.markdown("### Price Chart")
                    plot_price_chart(df, stock_ticker)

                with st.container():
                    st.markdown("### Seasonality Chart")
                    plot_seasonality_chart(monthly_avg, stock_ticker)

                # Download button for seasonality data
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
