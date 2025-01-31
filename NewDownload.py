import yfinance as yf
import pandas as pd

# Define the currency pair and the time period
ticker = "EURUSD=X"  # Yahoo Finance ticker for EUR/USD
start_date = "2023-01-01"
end_date = "2023-12-31"

# Download the data
data = yf.download(ticker, start=start_date, end=end_date)

# Save the data to a CSV file
data.to_csv("EURUSD_data.csv")

# Print a preview of the data
print(data.head())