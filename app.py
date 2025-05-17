import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="PSX Seasonality Tool", layout="wide")

# App title
st.title("📈 PSX Seasonality Tool")
st.write("Upload a CSV file with `Date` and `Price` columns to visualize PSX monthly return seasonality.")
st.markdown("""
- `Date` should be in MM/DD/YYYY or similar format.
- `Price` should be numerical (e.g. closing prices).
- If you want to try it out, use this [sample file](https://raw.githubusercontent.com/yourusername/psx-seasonality-tool/main/test.csv)
""")

# File uploader
uploaded_file = st.file_uploader("📤 Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # Load CSV
        df = pd.read_csv(uploaded_file)

        # Preprocess
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)
        df = df.sort_values('Date')
        df.set_index('Date', inplace=True)
        df['Price'] = df['Price'].astype(float)
        df['Daily Return %'] = df['Price'].pct_change() * 100
        monthly_avg = df['Daily Return %'].resample('ME').mean()
        monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()

        # Plotting
        fig, axs = plt.subplots(2, 1, figsize=(12, 10))

        axs[0].plot(df.index, df['Price'], color='blue', label='Closing Price')
        axs[0].set_title('Closing Price Over Time')
        axs[0].set_xlabel('Date')
        axs[0].set_ylabel('Price')
        axs[0].legend()
        axs[0].grid(True)

        sns.lineplot(x=monthly_avg_by_month.index - 1,
                     y=monthly_avg_by_month.values,
                     marker='o', ax=axs[1])
        axs[1].set_title('Average Monthly Return (%) - Seasonality')
        axs[1].set_xlabel('Month')
        axs[1].set_ylabel('Average Return %')
        axs[1].set_xticks(range(0,12))
        axs[1].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        axs[1].grid(True)

        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("👆 Please upload a CSV file to begin.")
