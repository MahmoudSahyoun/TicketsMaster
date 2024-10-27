import pandas as pd
from datetime import datetime

# Load the Excel file
file_path = r'C:\Users\Sohyon\OneDrive\Desktop\ticketsmaster\Event notification\artist_events.xlsx'

# Read the Excel file
df = pd.read_excel(file_path)

# Specify the date format if known (adjust '%Y-%m-%d %H:%M:%S' as per your data)
df['Presale Time'] = pd.to_datetime(df['Presale Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Set the date filter (after October 14th, 2024)
date_filter = pd.to_datetime('2024-10-14')

# Filter events with presale dates after October 14th, 2024
filtered_events = df[(df['Presale Time'] > date_filter) & (df['Presale Time'].notna())]

# Specify the correct directory for saving
filtered_output_file_path = r'C:\Users\Sohyon\OneDrive\Desktop\ticketsmaster\Event notification\filtered_events_after_october_14_2024.xlsx'

# Save the filtered data to a new Excel file
filtered_events.to_excel(filtered_output_file_path, index=False)

print("Filtered events saved to:", filtered_output_file_path)
