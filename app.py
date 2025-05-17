import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
import io
from fpdf import FPDF
plt.style.use('dark_background')


st.set_page_config(page_title="PSX SEASONX", layout="wide", page_icon="📈")

# ------------------ UI Style ------------------
def set_dark_theme():
    st.markdown("""
        <style>
        body, .main, .block-container {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stPlotlyChart, .stButton, .stSelectbox, .stSlider, .stFileUploader {
            background-color: #1e222b;
            color: #fafafa;
        }
        h1, h2, h3 {
            color: #29b6f6;
        }
        .css-1aumxhk {
            padding: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)

set_dark_theme()

# ------------------ Functions ------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)
    df = df.sort_values('Date')
    df.set_index('Date', inplace=True)
    df['Price'] = df['Price'].astype(float)
    df['Daily Return %'] = df['Price'].pct_change() * 100
    return df

def calculate_seasonality(df):
    monthly_avg = df['Daily Return %'].resample('ME').mean()
    monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()
    return monthly_avg_by_month

def plot_price_chart(df, stock_name):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df.index, df['Price'], color='cyan', label='Closing Price')
    ax.set_title(f'{stock_name} - Closing Price Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.grid(True,color='gray', alpha=0.15)
    ax.legend()
    st.pyplot(fig)

def plot_seasonality_chart(monthly_avg_by_month, stock_name):
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.lineplot(x=monthly_avg_by_month.index - 1, y=monthly_avg_by_month.values, marker='o', ax=ax, color='lime')
    ax.set_title(f'{stock_name} - Avg Monthly Return (%)')
    ax.set_xlabel('Month')
    ax.set_ylabel('Avg Return %')
    ax.set_xticks(range(0, 12))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.grid(True)
    st.pyplot(fig)

def plot_seasonality_heatmap(df, stock_name):
    df['Year'] = df.index.year
    df['Month'] = df.index.month
    pivot = df.pivot_table(values='Daily Return %', index='Year', columns='Month', aggfunc='mean')
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(pivot, cmap='coolwarm', annot=True, fmt=".1f", ax=ax, cbar=True)
    ax.set_title(f"{stock_name} - Year-wise Monthly Return Heatmap (%)")
    ax.set_xlabel('Month')
    ax.set_ylabel('Year')
    ax.set_xticklabels([calendar.month_abbr[i] for i in range(1, 13)])
    st.pyplot(fig)

def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Seasonality Report')
    writer.close()
    return output.getvalue()

# ------------------ App UI ------------------

st.title("📊 PSX SEASONX - Pakistan Stock Seasonality Intelligence Tool")

uploaded_file = st.file_uploader("Upload a CSV file (Date, Price)", type=["csv"])

if uploaded_file:
    stock_name = st.text_input("Enter Stock Name", value="PSX Stock")

    df = load_data(uploaded_file)
    monthly_avg_by_month = calculate_seasonality(df)

    tab1, tab2, tab3 = st.tabs(["📈 Charts", "🌡️ Heatmap", "📤 Export Report"])

    with tab1:
        plot_price_chart(df, stock_name)
        plot_seasonality_chart(monthly_avg_by_month, stock_name)

    with tab2:
        plot_seasonality_heatmap(df, stock_name)

    with tab3:
        st.subheader("📥 Download Seasonality Report")

        # Prepare Excel for download
        excel_data = to_excel(monthly_avg_by_month.rename_axis('Month').reset_index())
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"{stock_name}_seasonality.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ------------------ Upcoming Features ------------------
with st.expander("🚀 Upcoming Features"):
    st.markdown("""
    - 📍 Interactive tooltips and animations  
    - 📊 Multi-stock dynamic comparison  
    - 🔔 Buy/Sell signal generator  
    - 📅 Date range filters  
    - 🧠 Machine-learning-based pattern detection  
    - 📈 Seasonality correlation clusters  
    - 🧪 Backtesting tool for seasonal strategies  
    - 🔗 API integrations and PSX screener  
    """)
