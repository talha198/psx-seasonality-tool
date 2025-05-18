import streamlit as st
import pandas as pd
import calendar
import plotly.graph_objects as go
import plotly.express as px
import io

st.set_page_config(page_title="📊 PSX SEASONX", layout="wide", page_icon="📈")

# ------------------ CSS UI Design ------------------
st.markdown("""
<style>
/* Global background */
body, .main, .block-container {
    background-color: #0e1117;
    color: #fafafa;
    font-family: 'Segoe UI', sans-serif;
}

/* Hide default menu and footer */
#MainMenu, footer, header {visibility: hidden;}

/* Header */
h1 {
    text-align: center;
    color: #29b6f6;
    margin-bottom: 0;
}
.title-container {
    background: linear-gradient(to right, #1e88e5, #1565c0);
    padding: 1.2rem;
    border-radius: 12px;
    box-shadow: 0 0 10px rgba(41,182,246,0.3);
    margin-bottom: 2rem;
}

/* File uploader button */
[data-testid="stFileUploader"] > label {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #1E88E5;
    color: white;
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 16px;
    border: 1px solid #1565C0;
    transition: background-color 0.3s ease, transform 0.2s ease;
    margin: auto;
    width: fit-content;
}

[data-testid="stFileUploader"] > label:hover {
    background-color: #1565C0;
    transform: scale(1.05);
}

[data-testid="stFileUploader"] span {
    display: none;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    margin-bottom: 1rem;
}
.stTabs [data-baseweb="tab"] {
    background-color: #1e1e1e;
    color: white;
    padding: 0.75rem 1.25rem;
    border-radius: 8px 8px 0 0;
    margin: 0 0.2rem;
    font-weight: bold;
    border-bottom: 2px solid transparent;
    transition: background-color 0.3s ease, transform 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #2e2e2e;
    transform: scale(1.05);
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #29b6f6;
}

/* Input box */
input {
    background-color: #1e1e1e !important;
    color: white !important;
}

/* Download button */
button[kind="primary"] {
    background-color: #1E88E5;
    color: white;
    border-radius: 8px;
    font-weight: bold;
    padding: 0.6rem 1rem;
    transition: background-color 0.3s ease, transform 0.2s ease;
}
button[kind="primary"]:hover {
    background-color: #1565C0;
    transform: scale(1.05);
}

/* Card styling for charts */
.card {
    background-color: #1a1c23;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    box-shadow: 0 6px 20px rgba(41,182,246,0.4);
    transform: scale(1.02);
}

/* Sidebar title */
.sidebar .sidebar-content h2 {
    color: #29b6f6;
}
</style>
""", unsafe_allow_html=True)


# ------------------ Header ------------------
st.markdown("""
<div class='title-container'>
    <h1>📊 PSX SEASONX</h1>
    <p style='text-align:center; margin-top:-10px;'>Pakistan Stock Seasonality Intelligence Tool</p>
</div>
""", unsafe_allow_html=True)


# ------------------ Sidebar ------------------
st.sidebar.title("🔧 Settings & Filters")
stock_name = st.sidebar.text_input("Stock Name", value="PSX Stock")
st.sidebar.markdown("---")
st.sidebar.write("⚙️ *Filters coming soon...*")


# ------------------ File Upload ------------------
uploaded_file = st.file_uploader("Upload CSV file with Date, Price", type=["csv"])

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
    
def analyze_favorable_times(monthly_avg_by_month):
    # Get months with positive returns (favorable to buy)
    favorable_buy_months = monthly_avg_by_month[monthly_avg_by_month > 0].sort_values(ascending=False).index.tolist()
    # Get months with negative returns (suggest sell)
    favorable_sell_months = monthly_avg_by_month[monthly_avg_by_month <= 0].sort_values().index.tolist()

    # For demo, take top 3 buy months and bottom 3 sell months
    buy_months = favorable_buy_months[:3]
    sell_months = favorable_sell_months[:3]

    # Calculate demo return by summing average returns for buy months
    demo_return_pct = monthly_avg_by_month[buy_months].sum()

    # Investment amount
    invested_amount = 100000  # 100k PKR
    final_amount = invested_amount * (1 + demo_return_pct / 100)
    profit = final_amount - invested_amount

    # Convert month numbers to names
    buy_month_names = [calendar.month_name[m] for m in buy_months]
    sell_month_names = [calendar.month_name[m] for m in sell_months]

    return buy_month_names, sell_month_names, demo_return_pct, profit, final_amount



def plot_price_chart_plotly(df, stock_name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Price'], mode='lines', line=dict(color='cyan'), name='Closing Price'))
    fig.update_layout(
        title=f'{stock_name} - Closing Price Over Time',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        hovermode='x unified',
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_seasonality_chart_plotly(monthly_avg_by_month, stock_name):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=monthly_avg_by_month.values,
        mode='lines+markers',
        line=dict(color='lime', width=2),
        marker=dict(size=8),
        name='Avg Monthly Return %'
    ))
    fig.update_layout(
        title=f'{stock_name} - Avg Monthly Return (%)',
        xaxis_title='Month',
        yaxis_title='Avg Return %',
        template='plotly_dark',
        hovermode='x unified',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.15)',
            tickmode='array',
            tickvals=months,
            ticktext=months
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.15)'
        ),
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="white"
        ),
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_seasonality_heatmap(df, stock_name):
    df['Year'] = df.index.year
    df['Month'] = df.index.month
    pivot = df.pivot_table(values='Daily Return %', index='Year', columns='Month', aggfunc='mean')

    pivot = pivot[range(1, 13)]  # Ensure Jan-Dec order
    pivot.columns = [calendar.month_abbr[m] for m in pivot.columns]

    fig = px.imshow(pivot,
                    color_continuous_scale='RdBu_r',
                    title=f"{stock_name} - Year-wise Monthly Return Heatmap (%)",
                    labels=dict(x="Month", y="Year", color="Return %"),
                    aspect="auto",
                    template='plotly_dark')

    fig.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.reset_index(inplace=True)
    df.to_excel(writer, index=False, sheet_name='Seasonality Report')
    writer.close()
    return output.getvalue()


# ------------------ App Logic ------------------
if uploaded_file:
    df = load_data(uploaded_file)
    monthly_avg_by_month = calculate_seasonality(df)

    tab1, tab2, tab3 = st.tabs(["📈 Charts", "🌡️ Heatmap", "📤 Export Report"])

  with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    plot_price_chart_plotly(df, stock_name)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    plot_seasonality_chart_plotly(monthly_avg_by_month, stock_name)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Add this block for favorable times & demo return ---
    buy_months, sell_months, demo_return_pct, profit, final_amount = analyze_favorable_times(monthly_avg_by_month)

    st.markdown("---")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🔍 Favorable Time Analysis & Demo Return")
    st.write(f"**Favorable months to BUY:** {', '.join(buy_months)}")
    st.write(f"**Favorable months to SELL:** {', '.join(sell_months)}")
    st.write(f"💰 If you invested 100,000 PKR in these favorable months, estimated return would be: **{demo_return_pct:.2f}%**")
    st.write(f"📈 This means your investment might grow to approximately: **{final_amount:,.0f} PKR** (profit of {profit:,.0f} PKR)")
    st.markdown("</div>", unsafe_allow_html=True)


    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        plot_seasonality_heatmap(df, stock_name)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("Download the seasonality report as an Excel file:")
        excel_data = to_excel(df)
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"{stock_name}_seasonality_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Please upload a CSV file with at least 'Date' and 'Price' columns to begin.")
