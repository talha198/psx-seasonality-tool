import streamlit as st
import pandas as pd
import calendar
import plotly.graph_objects as go
import plotly.express as px
import io
from datetime import datetime

st.set_page_config(page_title="📊 PSX SEASONX", layout="wide", page_icon="📈")

# ------------------ CSS UI Design ------------------
st.markdown("""
<style>
/* Global background */
body, .main, .block-container {
    background-color: #0e1117;
    color: #fafafa;
    font-family: 'Segoe UI', sans-serif;
}

/* Hide default menu and footer */
#MainMenu, footer, header {visibility: hidden;}

/* Header */
h1 {
    text-align: center;
    color: #29b6f6;
    margin-bottom: 0;
}
.title-container {
    background: linear-gradient(to right, #1e88e5, #1565c0);
    padding: 1.2rem;
    border-radius: 12px;
    box-shadow: 0 0 10px rgba(41,182,246,0.3);
    margin-bottom: 2rem;
}

/* File uploader button */
[data-testid="stFileUploader"] > label {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #1E88E5;
    color: white;
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 16px;
    border: 1px solid #1565C0;
    transition: background-color 0.3s ease, transform 0.2s ease;
    margin: auto;
    width: fit-content;
}
[data-testid="stFileUploader"] > label:hover {
    background-color: #1565C0;
    transform: scale(1.05);
}
[data-testid="stFileUploader"] span {
    display: none;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    margin-bottom: 1rem;
}
.stTabs [data-baseweb="tab"] {
    background-color: #1e1e1e;
    color: white;
    padding: 0.75rem 1.25rem;
    border-radius: 8px 8px 0 0;
    margin: 0 0.2rem;
    font-weight: bold;
    border-bottom: 2px solid transparent;
    transition: background-color 0.3s ease, transform 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #2e2e2e;
    transform: scale(1.05);
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #29b6f6;
}

/* Input box */
input {
    background-color: #1e1e1e !important;
    color: white !important;
}

/* Download button */
button[kind="primary"] {
    background-color: #1E88E5;
    color: white;
    border-radius: 8px;
    font-weight: bold;
    padding: 0.6rem 1rem;
    transition: background-color 0.3s ease, transform 0.2s ease;
}
button[kind="primary"]:hover {
    background-color: #1565C0;
    transform: scale(1.05);
}

/* Card styling for charts */
.card {
    background-color: #1a1c23;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    box-shadow: 0 6px 20px rgba(41,182,246,0.4);
    transform: scale(1.02);
}

/* Sidebar title */
.sidebar .sidebar-content h2 {
    color: #29b6f6;
}

/* Colored return text */
.return-positive {
    color: #4CAF50;
    font-weight: bold;
}
.return-negative {
    color: #F44336;
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
stock_name = st.sidebar.text_input("Stock Name", value="PSX Stock")
st.sidebar.markdown("---")
st.sidebar.write("⚙️ *Filters coming soon...*")


# ------------------ File Upload ------------------
uploaded_file = st.file_uploader("Upload CSV file with Date, Price", type=["csv"])


# ------------------ Functions ------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').set_index('Date')
    df['Price'] = df['Price'].astype(float)
    df['Daily Return %'] = df['Price'].pct_change() * 100
    return df


def calculate_seasonality(df):
    # Average daily return by month-end date, then average by month number across years
    monthly_avg = df['Daily Return %'].resample('ME').mean()
    monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()
    return monthly_avg_by_month


def get_first_price_of_month(df, year, month):
    """Helper: Find first available price on or after the 1st of given month."""
    dt = pd.Timestamp(year=year, month=month, day=1)
    prices = df.loc[df.index >= dt]['Price']
    if not prices.empty:
        return prices.iloc[0]
    return None


def analyze_favorable_times(df, monthly_avg_by_month):
    # Separate favorable buy and sell months by positive/negative avg return
    favorable_buy_months = monthly_avg_by_month[monthly_avg_by_month > 0].sort_values(ascending=False).index.tolist()
    favorable_sell_months = monthly_avg_by_month[monthly_avg_by_month <= 0].sort_values().index.tolist()

    # Top 3 buy and sell months (or fewer if less than 3)
    buy_months = favorable_buy_months[:3]
    sell_months = favorable_sell_months[:3]

    # Demo return if invested 100,000 PKR in buy months' average returns
    demo_return_pct = monthly_avg_by_month.loc[buy_months].sum() if buy_months else 0
    invested_amount = 100_000
    final_amount = invested_amount * (1 + demo_return_pct / 100)
    profit = final_amount - invested_amount

    # Calculate compound return by simulating buy-sell cycles per year
    years = sorted(df.index.year.unique())
    total_return_factor = 1

    for year in years:
        for buy_month in favorable_buy_months:
            buy_price = get_first_price_of_month(df, year, buy_month)
            if buy_price is None:
                continue

            # Find nearest sell month after buy month within the year or next year
            sell_price = None
            for offset in range(1, 13):
                candidate_month = ((buy_month - 1 + offset) % 12) + 1
                candidate_year = year + ((buy_month - 1 + offset) // 12)
                if candidate_month in favorable_sell_months:
                    sell_price = get_first_price_of_month(df, candidate_year, candidate_month)
                    if sell_price is not None:
                        break

            # If no sell price found, hold till year end
            if sell_price is None:
                sell_prices = df.loc[df.index.year == year]['Price']
                if not sell_prices.empty:
                    sell_price = sell_prices.iloc[-1]
                else:
                    continue

            cycle_return = sell_price / buy_price
            total_return_factor *= cycle_return

    compound_final_amount = invested_amount * total_return_factor
    compound_profit = compound_final_amount - invested_amount
    compound_return_pct = (total_return_factor - 1) * 100

    # Current month and upcoming favorable buy months
    current_month = datetime.today().month
    upcoming_buy_months = [m for m in favorable_buy_months if m >= current_month]
    upcoming_buy_names = [calendar.month_name[m] for m in upcoming_buy_months]

    # Convert numeric months to names
    buy_month_names = [calendar.month_name[m] for m in buy_months]
    sell_month_names = [calendar.month_name[m] for m in sell_months]

    return {
        "buy_month_names": buy_month_names,
        "sell_month_names": sell_month_names,
        "simple_return_pct": demo_return_pct,
        "simple_profit": profit,
        "simple_final_amount": final_amount,
        "compound_return_pct": compound_return_pct,
        "compound_profit": compound_profit,
        "compound_final_amount": compound_final_amount,
        "upcoming_buy_names": upcoming_buy_names,
    }


def plot_price_chart(df, stock_name):
    fig = px.line(df.reset_index(), x='Date', y='Price', title=f"Price Chart: {stock_name}")
    st.plotly_chart(fig, use_container_width=True)


def plot_seasonality_chart(monthly_avg_by_month, stock_name):
    months = list(calendar.month_abbr)[1:]  # Jan to Dec abbreviations
    data = monthly_avg_by_month.reindex(range(1, 13)).fillna(0).values

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
        title=f"Seasonality Chart: {stock_name}",
        xaxis_title="Month",
        yaxis_title="Average Monthly Return (%)",
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="#fafafa"),
        yaxis=dict(ticksuffix="%")
    )
    st.plotly_chart(fig, use_container_width=True)


def download_link(df, filename="seasonality_report.csv"):
    csv = df.to_csv().encode()
    st.download_button(
        label="Download Seasonality Data as CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )


# ------------------ Main ------------------
if uploaded_file is not None:
    with st.spinner("Processing data..."):
        df = load_data(uploaded_file)
        monthly_avg = calculate_seasonality(df)
        results = analyze_favorable_times(df, monthly_avg)

    # Display Summary
    st.subheader(f"📈 Seasonality Summary for {stock_name}")

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
        plot_price_chart(df, stock_name)

    with st.container():
        st.markdown("### Seasonality Chart")
        plot_seasonality_chart(monthly_avg, stock_name)

    # Download button for seasonality data
    monthly_df = monthly_avg.rename_axis('Month').reset_index()
    monthly_df['Month_Name'] = monthly_df['Month'].apply(lambda x: calendar.month_name[x])
    monthly_df = monthly_df[['Month', 'Month_Name', 'Daily Return %']]
    monthly_df.rename(columns={'Daily Return %': 'Avg Monthly Return (%)'}, inplace=True)

    download_link(monthly_df)

else:
    st.info("Please upload a CSV file with columns: Date, Price to proceed.")


# ------------------ Footer ------------------
st.markdown("""
<div style='text-align:center; margin-top:3rem; color:#666; font-size:12px;'>
    © 2025 PSX SEASONX | Developed by YourName
</div>
""", unsafe_allow_html=True)
