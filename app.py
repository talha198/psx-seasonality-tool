import yfinance as yf
df = yf.download("TRG.PK", start="2015-01-01", end="2025-05-18")
print(df.head())
