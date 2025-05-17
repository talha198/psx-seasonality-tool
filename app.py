import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(page_title="PSX SEASONX", page_icon="📈", layout="wide")

# Page title and description
st.title("PSX SEASONX")
st.markdown("""
#### Your Professional Seasonality Analysis Tool for the Pakistan Stock Exchange  
Upload multiple PSX stock CSV files and compare their monthly average return seasonality.
""")

# File uploader allowing multiple CSVs
uploaded_files = st.file_uploader(
    "Upload CSV files for different PSX stocks (each must have 'Date' and 'Price' columns):", 
    type=['csv'], 
    accept_multiple_files=True
)

if uploaded_files:
    stock_data = {}
    for file in uploaded_files:
        df = pd.read_csv(file)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)
        df = df.sort_values('Date')
        df.set_index('Date', inplace=True)
        df['Price'] = df['Price'].astype(float)
        df['Daily Return %'] = df['Price'].pct_change() * 100
        monthly_avg = df['Daily Return %'].resample('ME').mean()
        monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()
        stock_data[file.name] = monthly_avg_by_month

    # Stock selector dropdown
    stock_selected = st.selectbox("Select stock to view seasonality:", list(stock_data.keys()))

    # Plot seasonality for selected stock
    monthly_avg_by_month = stock_data[stock_selected]

    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(
        x=monthly_avg_by_month.index - 1, 
        y=monthly_avg_by_month.values, 
        marker='o', 
        ax=ax,
        color='dodgerblue'
    )
    ax.set_title(f"Average Monthly Return (%) - Seasonality for {stock_selected}", color='white')
    ax.set_xlabel("Month", color='white')
    ax.set_ylabel("Average Return %", color='white')
    ax.set_xticks(range(0,12))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], color='white')
    ax.grid(True, color='gray')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white') 
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    fig.patch.set_facecolor('#0E1117')  # dark background
    ax.set_facecolor('#0E1117')  # dark background

    st.pyplot(fig)

else:
    st.info("Upload one or more CSV files to start analyzing seasonality.")

# Footer or upcoming features header
st.markdown("---")
st.subheader("Upcoming Features")
st.markdown("""
- Multi-stock side-by-side comparison charts  
- Export seasonality reports (PDF/Excel)  
- Interactive charts with tooltips and zoom  
- Portfolio watchlist with aggregate seasonality view  
- Risk-adjusted seasonality metrics  
- Economic calendar & PSX market event overlays  
- AI-powered seasonal pattern detection and alerts  
""")
