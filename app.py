import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from fpdf import FPDF

# Set page config
st.set_page_config(page_title="PSX SEASONX", page_icon="📈", layout="wide")

# Page title and description
st.title("PSX SEASONX")
st.markdown("""
#### Your Professional Seasonality Analysis Tool for the Pakistan Stock Exchange  
Upload multiple PSX stock CSV files and compare their monthly average return seasonality.
""")

uploaded_files = st.file_uploader(
    "Upload CSV files for different PSX stocks (each must have 'Date' and 'Price' columns):", 
    type=['csv'], 
    accept_multiple_files=True
)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Seasonality')
    processed_data = output.getvalue()
    return processed_data

def to_pdf(stock_name, monthly_avg_by_month):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 139)  # dark blue

    pdf.cell(0, 10, f"PSX SEASONX - Seasonality Report for {stock_name}", ln=True, align='C')

    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, "Month", border=1, align='C')
    pdf.cell(60, 10, "Average Return (%)", border=1, align='C')
    pdf.ln()

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for month_idx in range(1, 13):
        avg_return = monthly_avg_by_month.get(month_idx, 0)
        pdf.cell(40, 10, month_names[month_idx-1], border=1, align='C')
        pdf.cell(60, 10, f"{avg_return:.2f}", border=1, align='C')
        pdf.ln()

    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output

if uploaded_files:
    stock_data = {}
    for file in uploaded_files:
        df = pd.read_csv(file)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)
        df = df.sort_values('Date')
        df.set_index('Date', inplace=True)
        df['Price'] = df['Price'].astype(float)
        df['Daily Return %'] = df['Price'].pct_change() * 100
        monthly_avg = df['Daily Return %'].resample('ME').mean()
        monthly_avg_by_month = monthly_avg.groupby(monthly_avg.index.month).mean()
        stock_data[file.name] = monthly_avg_by_month

    # Single stock selection & plot
    stock_selected = st.selectbox("Select stock to view seasonality:", list(stock_data.keys()))
    monthly_avg_by_month = stock_data[stock_selected]

    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(
        x=monthly_avg_by_month.index - 1, 
        y=monthly_avg_by_month.values, 
        marker='o', 
        ax=ax,
        color='dodgerblue'
    )
    ax.set_title(f"Average Monthly Return (%) - Seasonality for {stock_selected}", color='white')
    ax.set_xlabel("Month", color='white')
    ax.set_ylabel("Average Return %", color='white')
    ax.set_xticks(range(0,12))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], color='white')
    ax.grid(True, color='gray')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white') 
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    fig.patch.set_facecolor('#0E1117')  # dark background
    ax.set_facecolor('#0E1117')  # dark background

    st.pyplot(fig)

    # Export buttons for selected stock
    col1, col2 = st.columns(2)

    with col1:
        excel_data = to_excel(monthly_avg_by_month.rename_axis('Month').reset_index())
        st.download_button(
            label="📥 Download Seasonality as Excel",
            data=excel_data,
            file_name=f"{stock_selected}_seasonality.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col2:
        pdf_data = to_pdf(stock_selected, monthly_avg_by_month)
        st.download_button(
            label="📥 Download Seasonality as PDF",
            data=pdf_data,
            file_name=f"{stock_selected}_seasonality.pdf",
            mime="application/pdf"
        )

    st.markdown("---")

    # Multi-stock side-by-side comparison chart
    st.subheader("Multi-Stock Seasonality Comparison")
    fig2, ax2 = plt.subplots(figsize=(12, 6))

    # Assign a color palette
    palette = sns.color_palette("tab10", n_colors=len(stock_data))

    for idx, (stock_name, monthly_avg) in enumerate(stock_data.items()):
        ax2.plot(
            monthly_avg.index - 1, 
            monthly_avg.values, 
            marker='o', 
            label=stock_name, 
            color=palette[idx]
        )

    ax2.set_title("Average Monthly Return (%) - Multi-Stock Comparison", color='white')
    ax2.set_xlabel("Month", color='white')
    ax2.set_ylabel("Average Return %", color='white')
    ax2.set_xticks(range(0,12))
    ax2.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], color='white')
    ax2.grid(True, color='gray')
    ax2.spines['bottom'].set_color('white')
    ax2.spines['top'].set_color('white') 
    ax2.spines['right'].set_color('white')
    ax2.spines['left'].set_color('white')
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')
    fig2.patch.set_facecolor('#0E1117')  # dark background
    ax2.set_facecolor('#0E1117')  # dark background
    ax2.legend(facecolor='#0E1117', edgecolor='white', labelcolor='white')

    st.pyplot(fig2)

else:
    st.info("Upload one or more CSV files to start analyzing seasonality.")

st.markdown("---")
st.subheader("Upcoming Features")
st.markdown("""
- Interactive charts with tooltips and zoom  
- Portfolio watchlist with aggregate seasonality view  
- Risk-adjusted seasonality metrics  
- Economic calendar & PSX market event overlays  
- AI-powered seasonal pattern detection and alerts  
""")
