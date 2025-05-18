import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- Debug/Test Section ---
st.sidebar.markdown("---")
if st.sidebar.checkbox("🧪 Run Simple Line Chart Test"):
    st.header("📉 Simple Line Chart Test")

    test_ticker = "OGDC.KA"
    test_start = pd.to_datetime("2020-01-01")
    test_end = pd.to_datetime("today")

    try:
        test_df = yf.download(test_ticker, start=test_start, end=test_end, progress=False, auto_adjust=True)
        if test_df.empty:
            st.warning(f"No data found for {test_ticker}")
        else:
            test_df = test_df[['Close']].rename(columns={"Close": "Price"})
            test_df['Date'] = test_df.index
            fig = px.line(test_df, x='Date', y='Price', title=f"{test_ticker} Price Line Chart")
            fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font=dict(color="#fafafa"))
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Failed to generate line chart: {e}")
