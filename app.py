import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="PSX SEASONX", layout="wide", page_icon="📈")

# --- APP TITLE & HEADER ---
st.markdown("""
    <h1 style='color:#00aaff; text-align:center; font-family:Arial Black, sans-serif;'>PSX SEASONX</h1>
    <h3 style='color:#3399ff; text-align:center; font-family:Arial, sans-serif;'>Pakistan Stock Exchange Seasonality Intelligence Tool</h3>
    <hr style="border:1px solid #00aaff;">
    """, unsafe_allow_html=True)

# --- UPLOAD FILES ---
uploaded_files = st.file_uploader(
    "Upload one or more PSX CSV files (Date, Price columns expected)", 
    type=['csv'], accept_multiple_files=True)

if uploaded_files:
    # Dictionary to store dataframes for each stock
    stock_dfs = {}
    for file in uploaded_files:
        df = pd.read_csv(file)
        # Basic preprocessing
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)
        df = df.sort_values('Date')
        df.set_index('Date', inplace=True)
        df['Price'] = df['Price'].astype(float)
        stock_name = file.name.replace('.csv','')
        stock_dfs[stock_name] = df

    # Stock selector for individual analysis
    selected_stock = st.selectbox("Select Stock to Analyze", options=list(stock_dfs.keys()))

    df = stock_dfs[selected_stock]

    # Calculate daily returns in %
    df['Daily Return %'] = df['Price'].pct_change() * 100

    # Monthly average return for seasonality line chart
    monthly_avg = df['Daily Return %'].resample('ME').mean()
    monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()

    # ----------------- PLOTTING --------------------

    fig, axs = plt.subplots(3, 1, figsize=(14, 16), gridspec_kw={'height_ratios': [2, 2, 3]})

    # Closing Price Over Time
    axs[0].plot(df.index, df['Price'], color='#00aaff')
    axs[0].set_title(f'{selected_stock} - Closing Price Over Time', color='white')
    axs[0].set_xlabel('Date', color='white')
    axs[0].set_ylabel('Price', color='white')
    axs[0].tick_params(axis='x', colors='white')
    axs[0].tick_params(axis='y', colors='white')
    axs[0].grid(True, color='gray', linestyle='--', alpha=0.5)
    axs[0].set_facecolor('#121212')

    # Average Monthly Return Seasonality
    sns.lineplot(x=monthly_avg_by_month.index - 1, y=monthly_avg_by_month.values,
                 marker='o', color='#3399ff', ax=axs[1])
    axs[1].set_title(f'{selected_stock} - Average Monthly Return (%) - Seasonality', color='white')
    axs[1].set_xlabel('Month', color='white')
    axs[1].set_ylabel('Average Return %', color='white')
    axs[1].set_xticks(range(0, 12))
    axs[1].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], color='white')
    axs[1].tick_params(axis='y', colors='white')
    axs[1].grid(True, color='gray', linestyle='--', alpha=0.5)
    axs[1].set_facecolor('#121212')

    # ----- NEW: Seasonality Heatmap: Year-wise Monthly Returns ----

    # Calculate monthly returns by year-month
    df['Year'] = df.index.year
    df['Month'] = df.index.month

    monthly_returns = df.groupby(['Year', 'Month'])['Daily Return %'].mean().unstack()

    # Order months correctly (1-12)
    monthly_returns = monthly_returns.reindex(columns=range(1,13))

    # Plot heatmap
    sns.heatmap(monthly_returns, cmap='RdYlGn', center=0, annot=True, fmt=".2f",
                cbar_kws={'label': 'Average Monthly Return (%)'},
                linewidths=0.5, linecolor='gray', ax=axs[2])

    axs[2].set_title(f'{selected_stock} - Year-wise Monthly Return Heatmap', color='white')
    axs[2].set_xlabel('Month', color='white')
    axs[2].set_ylabel('Year', color='white')
    axs[2].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45, ha='right', color='white')
    axs[2].tick_params(axis='y', colors='white')
    axs[2].tick_params(axis='x', colors='white')
    axs[2].set_facecolor('#121212')

    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")
    st.markdown(
        "<h3 style='color:#00aaff;'>Upcoming Features</h3>", unsafe_allow_html=True)
    st.write("""
    - Portfolio-Level Seasonality Aggregation  
    - Risk-Adjusted Seasonality Metrics  
    - Economic Event Overlay  
    - Seasonality Alerts and Notifications  
    - Custom Date Range Analysis  
    - Interactive Charts  
    """)

else:
    st.info("Please upload one or more CSV files with Date and Price columns.")

# Set dark theme background for app
page_bg = """
<style>
    .reportview-container {
        background-color: #0e1117;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #121212;
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)
