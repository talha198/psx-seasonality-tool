import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
import io
from openpyxl import Workbook

# Set Streamlit page config
st.set_page_config(page_title="PSX SEASONX", layout="wide")

# Custom dark theme CSS
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: #c9d1d9;
        }
        .stApp {
            background-color: #0e1117;
        }
        .stMarkdown, .stTextInput, .stSelectbox, .stButton>button {
            color: #c9d1d9;
        }
        .stButton>button {
            background-color: #1f6feb;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
        }
        .stButton>button:hover {
            background-color: #388bfd;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📈 PSX SEASONX - Pakistan Stock Market Seasonality Tool")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV file (Date & Price columns required)", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Parse and clean
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)
    df = df.sort_values('Date')
    df.set_index('Date', inplace=True)
    df['Price'] = df['Price'].astype(float)
    df['Daily Return %'] = df['Price'].pct_change() * 100

    # Monthly average returns
    monthly_avg = df['Daily Return %'].resample('ME').mean()
    monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()

    # Plot settings
    plt.style.use('dark_background')
    sns.set_style("darkgrid")

    # Line chart of price
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(df.index, df['Price'], color='#58a6ff')
    ax1.set_title("Closing Price Over Time", color='white')
    ax1.set_xlabel("Date", color='white')
    ax1.set_ylabel("Price", color='white')
    ax1.tick_params(colors='white')

    # Line chart of seasonality
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    sns.lineplot(x=monthly_avg_by_month.index - 1,
                 y=monthly_avg_by_month.values,
                 marker='o', color='#1f6feb', ax=ax2)
    ax2.set_title("Average Monthly Return (%) - Seasonality", color='white')
    ax2.set_xlabel("Month", color='white')
    ax2.set_ylabel("Average Return %", color='white')
    ax2.set_xticks(range(0, 12))
    ax2.set_xticklabels(calendar.month_abbr[1:], color='white')
    ax2.tick_params(colors='white')
    ax2.grid(True, color='gray')

    # Display plots
    st.pyplot(fig1)
    st.pyplot(fig2)

    # Export options
    def to_excel(df):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Seasonality')
        writer.close()
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel(monthly_avg_by_month.rename_axis('Month').reset_index())
    st.download_button("📥 Download Excel Report", data=excel_data,
                       file_name="psx_seasonality_report.xlsx")

    st.markdown("---")
    st.subheader("🧪 Upcoming Features (Coming Soon):")
    st.markdown("""
    - 📊 Multi-stock seasonality comparisons  
    - 🌡️ Year-wise seasonality heatmaps  
    - 🧠 Signal generation based on seasonal trends  
    - 🖨️ PDF report generation  
    - 📅 Automatic PSX data integration  
    - 📱 Mobile-friendly view  
    - 🎯 Sector-wise seasonality insights  
    - 🧰 Custom filtering by date range or volatility  
    """)

else:
    st.info("Upload a CSV file to start. The file must have `Date` and `Price` columns.")

