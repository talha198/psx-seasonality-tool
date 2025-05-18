# --- Debug/Test Section ---
st.sidebar.markdown("---")
run_test = st.sidebar.checkbox("🧪 Run Simple Line Chart Test")

if run_test:
    st.header("🧪 PSX Chart Test")

    try:
        test_df = fetch_stock_data(custom_ticker.strip(), start_date, end_date)
        st.success(f"✅ Data fetched for {custom_ticker}")
        plot_price_chart(test_df, custom_ticker)
    except Exception as e:
        st.error(f"❌ Failed to generate line chart: {e}")
