import yfinance as yf

# Download data for a stock
data = yf.download("AAPL", start="2022-01-01", end="2023-01-01")

# Save the data to a CSV file
data.to_csv("AAPL_data.csv")

# Print a preview of the data
print(data.head())
