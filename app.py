import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config and title
st.set_page_config(page_title="psxSeasonx", layout="wide")

# Inject custom CSS for black & blue theme
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #0b1117;
        color: #61dafb;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and sidebar
st.title("📊 psxSeasonx")

with st.sidebar:
    st.header("How to Use psxSeasonx")
    st.markdown(
        """
        1. Upload a CSV file with `Date` and `Price` columns.
        2. Date format: MM/DD/YYYY (e.g. 05/17/2025).
        3. See price trends and monthly return seasonality.
        4. Download sample CSV below if you want to test.
        """
    )
    st.markdown(
        "[📥 Download Sample CSV](https://raw.githubusercontent.com/yourusername/psx-seasonality-tool/main/test.csv)"
    )

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file here:", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)
        df = df.sort_values('Date')
        df.set_index('Date', inplace=True)
        df['Price'] = df['Price'].astype(float)
        df['Daily Return %'] = df['Price'].pct_change() * 100
        monthly_avg = df['Daily Return %'].resample('ME').mean()
        monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()

        st.subheader("📈 Closing Price Over Time")
        st.line_chart(df['Price'])

        st.subheader("📉 Average Monthly Return (%) - Seasonality")
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_df = pd.DataFrame({
            'Month': months,
            'Average Return %': monthly_avg_by_month.values
        }).set_index('Month')
        st.line_chart(monthly_df)

    except Exception as e:
        st.error(f"Error processing your file: {e}")

else:
    st.info("👆 Upload a CSV file to start analyzing PSX seasonality.")
