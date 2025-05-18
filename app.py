import streamlit as st
import pandas as pd
import warnings
from psx import PSX  # ✅ correct import

st.set_page_config(page_title="PSX Scraper Test", layout="wide")
st.title("🧪 PSX Data Reader Test")

ticker = st.text_input("Enter PSX Symbol (e.g., TRG, ENGRO):", value="TRG")
start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))

if st.button("Fetch PSX Data"):
    try:
        psx = PSX()  # ✅ instantiating PSX correctly
        data = psx.get_data(ticker)  # returns a list of dicts

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

        st.success(f"✅ Data fetched for {ticker}")
        st.dataframe(df)

        st.line_chart(df.set_index('date')['close'])

    except Exception as e:
        st.error(f"❌ Failed to fetch data: {e}")
        warnings.simplefilter(action='ignore', category=FutureWarning)
