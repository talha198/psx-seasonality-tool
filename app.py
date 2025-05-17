import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit page config
st.set_page_config(page_title="PSX SEASONX", layout="wide")

# Custom CSS for black & blue theme + styling
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #0b1117;
        color: #61dafb;
        font-family: 'Inter', sans-serif;
    }
    .css-18e3th9 {
        background-color: #0b1117;
    }
    .stButton>button {
        background-color: #1b263b;
        color: #61dafb;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3a5068;
        color: white;
    }
    .css-1d391kg {
        background-color: #0b1117;
    }
    h1, h2, h3, .css-1v3fvcr {
        color: #61dafb;
    }
    .stMarkdown p, .stMarkdown li {
        color: #a0c4ff;
    }
    hr {
        border: 1px solid #1b263b;
        margin: 1.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and tagline
st.title("📊 PSX SEASONX")
st.markdown("*Your Data-Driven Seasonality Intelligence for the Pakistan Stock Market*")

# Upcoming features section
st.markdown("---")
st.subheader("🚀 Upcoming Features & Enhancements")
st.markdown("""
- 📈 **Multi-Stock Analysis:** Compare seasonality across multiple PSX stocks simultaneously.  
- 🕒 **Custom Date Range Selection:** Analyze seasonality for specific periods or years.  
- 📊 **Interactive Charts:** Switch between line, bar, and heatmap visualizations with tooltips.  
- 📥 **Export & Share:** Download data and charts, or share interactive reports with your team.  
- 🔔 **Seasonality Alerts:** Get notified of optimal buy/sell windows based on historical data.  
- 📰 **Market News Integration:** Correlate seasonality trends with real-time Pakistan Stock Market news.  
- 🤖 **AI-Driven Insights:** Receive data-backed recommendations for better decision-making.  
""")

# Sidebar with instructions and sample CSV link
with st.sidebar:
    st.header("How to Use PSX SEASONX")
    st.markdown(
        """
        1. Upload a CSV file with columns `Date` and `Price`.  
        2. Date format should be MM/DD/YYYY (e.g., 05/17/2025).  
        3. View closing price trends and average monthly return seasonality.  
        4. Download sample CSV below to test the app.
        """
    )
    st.markdown(
        "[📥 Download Sample CSV](https://raw.githubusercontent.com/yourusername/psx-seasonality-tool/main/test.csv)"
    )

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file here:", type=["csv"])

if uploaded_file:
    try:
        # Load and process data
        df = pd.read_csv(uploaded_file)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)
        df = df.sort_values('Date')
        df.set_index('Date', inplace=True)
        df['Price'] = df['Price'].astype(float)
        df['Daily Return %'] = df['Price'].pct_change() * 100

        # Calculate monthly average returns
        monthly_avg = df['Daily Return %'].resample('ME').mean()
        monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()

        # Plot using matplotlib + seaborn with dark backgrounds
        fig, axs = plt.subplots(2, 1, figsize=(12, 10), constrained_layout=True)

        # Set figure facecolor (background) to dark
        fig.patch.set_facecolor('#0b1117')

        # Closing price plot
        axs[0].set_facecolor('#0b1117')  # dark background for plot area
        axs[0].plot(df.index, df['Price'], color='#61dafb', label='Closing Price')
        axs[0].set_title('Closing Price Over Time', color='#61dafb')
        axs[0].set_xlabel('Date', color='#a0c4ff')
        axs[0].set_ylabel('Price', color='#a0c4ff')
        axs[0].legend(facecolor='#1b263b', edgecolor='#61dafb')
        axs[0].grid(True, color='#3a5068')

        # Average monthly return seasonality plot
        axs[1].set_facecolor('#0b1117')
        sns.lineplot(
            x=monthly_avg_by_month.index - 1,
            y=monthly_avg_by_month.values,
            marker='o',
            color='#61dafb',
            ax=axs[1]
        )
        axs[1].set_title('Average Monthly Return (%) - Seasonality', color='#61dafb')
        axs[1].set_xlabel('Month', color='#a0c4ff')
        axs[1].set_ylabel('Average Return %', color='#a0c4ff')
        axs[1].set_xticks(range(0, 12))
        axs[1].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], color='#a0c4ff')
        axs[1].grid(True, color='#3a5068')

        # Style axis tick labels and spines color for all axes
        for ax in axs:
            ax.tick_params(axis='x', colors='#a0c4ff')
            ax.tick_params(axis='y', colors='#a0c4ff')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#3a5068')
            ax.spines['left'].set_color('#3a5068')

        # Show plots in Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error processing your file: {e}")

else:
    st.info("👆 Upload a CSV file to start analyzing PSX seasonality.")
