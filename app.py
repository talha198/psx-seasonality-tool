import streamlit as st
import pandas as pd
import calendar
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import yfinance as yf
import base64
from io import BytesIO

st.set_page_config(page_title="📊 PSX SEASONX", layout="wide", page_icon="📈")

# --- Your existing CSS here (paste your style block if you want) ---
st.markdown("""
<style>
/* Add your existing CSS styles here */
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

def calculate_seasonality(df):
    # Calculate average daily returns by month over all years
    monthly_avg = df['Daily Return %'].groupby(df.index.month).mean()
    monthly_avg.index.name = 'Month'
    monthly_avg.name = 'Daily Return %'
    return monthly_avg

def get_first_price_of_month(df):
    # Get first price of each month for compound return calc
    first_prices = df['Price'].resample('MS').first()
    return first_prices

def analyze_favorable_times(df, monthly_avg):
    # Determine favorable months based on average return > 0 (buy), < 0 (sell)
    buy_months = monthly_avg[monthly_avg > 0].index.tolist()
    sell_months = monthly_avg[monthly_avg <= 0].index.tolist()

    # Get month names
    buy_month_names = [calendar.month_name[m] for m in buy_months]
    sell_month_names = [calendar.month_name[m] for m in sell_months]

    # Calculate simple return = sum of avg returns of buy months (assumes buying and selling monthly)
    simple_return_pct = monthly_avg.loc[buy_months].sum() if buy_months else 0
    simple_profit = 100000 * simple_return_pct / 100

    # Compound return calculation over entire period for buy months only
    first_prices = get_first_price_of_month(df)
    compound_profit = 100000
    compound_return_pct = 0
    if not first_prices.empty and buy_months:
        # Compound by multiplying returns of buy months for each year
        for year in first_prices.index.year.unique():
            # Filter first prices of buy months in this year
            year_month_prices = first_prices[first_prices.index.year == year].loc[
                first_prices.index.month.isin(buy_months)
            ]
            # Calculate compounded return
            for i in range(1, len(year_month_prices)):
                ret = (year_month_prices.iloc[i] - year_month_prices.iloc[i-1]) / year_month_prices.iloc[i-1]
                compound_profit *= (1 + ret)
        compound_return_pct = ((compound_profit - 100000) / 100000) * 100

    # Upcoming favorable buy months from today
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
    fig.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="#fafafa")
    )
    st.plotly_chart(fig, use_container_width=True)

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

def download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="seasonality_data.csv">📥 Download Seasonality Data as CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

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
