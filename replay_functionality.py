import pandas as pd
import time

# Load the data
data = pd.read_csv("AAPL_data.csv")

# Get speed control input from the user
speed = float(input("Enter the speed (seconds) between bars: "))

# Start the timer
start_time = time.time()

print(data.head())
for index, row in data.iterrows():
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    print(f"Elapsed Time: {elapsed_time:.2f} seconds")
    
    # Print the row data
    print(row)
    
    # Pause for the specified speed
    time.sleep(speed)