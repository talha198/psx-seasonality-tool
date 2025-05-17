import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
import io
from fpdf import FPDF

st.set_page_config(page_title="PSX SEASONX", layout="wide", page_icon="📈")

# ------------------ UI Style ------------------
def set_dark_theme():
    st.markdown("""
        <style>
        body, .main, .block-container {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stButton, .stSelectbox, .stSlider, .stFileUploader {
            background-color: #1e222b;
            color: #fafafa;
        }
        h1, h2, h3 {
            color: #29b6f6;
        }
        .css-1aumxhk {
            padding: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)

set_dark_theme()

# ------------------ Functions ------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)
    df = df.sort_values('Date')
    df.set_index('Date', inplace=True)
    df['Price'] = df['Price'].astype(float)
    df['Daily Return %'] = df['Price'].pct_change() * 100
    return df

def calculate_seasonality(df):
    monthly_avg = df['Daily Return %'].resample('ME').mean()
    monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()
    return monthly_avg_by_month

def plot_price_chart(df, stock_name):
    df_reset = df.reset_index()
    fig = px.line(df_reset, x='Date', y='Price', title=f'{stock_name} - Closing Price Over Time',
                  labels={'Price': 'Price', 'Date': 'Date'},
                  template='plotly_dark',
                  color_discrete_sequence=['#00FFFF'])  # Cyan color
    fig.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117',
                      font_color='white')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.15)')  # 15% opacity grid lines
    st.plotly_chart(fig, use_container_width=True)

def plot_seasonality_chart(monthly_avg_by_month, stock_name):
    # Prepare DataFrame for Plotly
    df_season = monthly_avg_by_month.rename_axis('Month').reset_index()
    df_season['Month Name'] = df_season['Month'].apply(lambda x: calendar.month_abbr[x])

    fig = px.line(df_season, x='Month Name', y='Daily Return %',
                  title=f'{stock_name} - Average Monthly Return (%)',
                  labels={'Daily Return %': 'Avg Return %', 'Month Name': 'Month'},
                  markers=True,
                  template='plotly_dark',
                  color_discrete_sequence=['#32CD32'])  # Lime green
    fig.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117',
                      font_color='white')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.15)')
    st.plotly_chart(fig, use_container_width=True)

def plot_seasonality_heatmap(df, stock_name):
    df['Year'] = df.index.year
    df['Month'] = df.index.month
    pivot = df.pivot_table(values='Daily Return %', index='Year', columns='Month', aggfunc='mean')

    # Prepare data for heatmap
    pivot = pivot[range(1, 13)]  # Ensure columns in order Jan-Dec
    pivot.columns = [calendar.month_abbr[m] for m in pivot.columns]

    fig = px.imshow(pivot,
                    color_continuous_scale='RdBu_r',
                    title=f"{stock_name} - Year-wise Monthly Return Heatmap (%)",
                    labels=dict(x="Month", y="Year", color="Return %"),
                    aspect="auto",
                    template='plotly_dark')

    fig.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117',
                      font_color='white')
    st.plotly_chart(fig, use_container_width=True)

def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Seasonality Report')
    writer.close()
    return output.getvalue()

# ------------------ App UI ------------------

st.title("📊 PSX SEASONX - Pakistan Stock Seasonality Intelligence Tool")

uploaded_file = st.file_uploader("Upload a CSV file (Date, Price)", type=["csv"])

if uploaded_file:
    stock_name = st.text_input("Enter Stock Name", value="PSX Stock")

    df = load_data(uploaded_file)
    monthly_avg_by_month = calculate_seasonality(df)

    tab1, tab2, tab3 = st.tabs(["📈 Charts", "🌡️ Heatmap", "📤 Export Report"])

    with tab1:
        plot_price_chart(df, stock_name)
        plot_seasonality_chart(monthly_avg_by_month, stock_name)

    with tab2:
        plot_seasonality_heatmap(df, stock_name)

    with tab3:
        st.subheader("📥 Download Seasonality Report")

        # Prepare Excel for download
        excel_data = to_excel(monthly_avg_by_month.rename_axis('Month').reset_index())
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"{stock_name}_seasonality.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ------------------ Upcoming Features ------------------
with st.expander("🚀 Upcoming Features"):
    st.markdown("""
    - 📍 Interactive tooltips and animations  
    - 📊 Multi-stock dynamic comparison  
    - 🔔 Buy/Sell signal generator  
    - 📅 Date range filters  
    - 🧠 Machine-learning-based pattern detection  
    - 📈 Seasonality correlation clusters  
    - 🧪 Backtesting tool for seasonal strategies  
    - 🔗 API integrations and PSX screener  
    """)
