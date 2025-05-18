import datetime
from psx import stocks

# Define the date range
start_date = datetime.date(2020, 1, 1)
end_date = datetime.date.today()

# Fetch data for a single ticker
data = stocks("OGDC", start=start_date, end=end_date)

# Display the first few rows
print(data.head())
