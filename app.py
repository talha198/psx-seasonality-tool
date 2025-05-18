if st.sidebar.checkbox("Run Simple Line Chart Test"):
    try:
        test_df = fetch_stock_data(custom_ticker, start_date, end_date)
        st.subheader(f"✅ Line Chart Test: {custom_ticker}")
        plot_price_chart(test_df, custom_ticker)
    except Exception as e:
        st.error(f"Line chart test failed: {e}")
