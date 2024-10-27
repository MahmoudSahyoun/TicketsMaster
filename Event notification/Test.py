import requests

# Define your Ticketmaster API Key
api_key = '4MtKJcFof2Vz21n9v6n13tgQvpTmnlGm'

# Set the endpoint for event search
url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}'

# Define parameters for the API request
params = {
    'keyword': 'concert',
    'size': 1  # Just return 1 event to test
}

# Make the API request
response = requests.get(url, params=params)

# Check the response status
if response.status_code == 200:
    print("API request successful!")
    # Optionally print the returned data
    data = response.json()
    print("Event data:", data)
elif response.status_code == 401:
    print("Unauthorized: Invalid API Key or missing permissions.")
else:
    print(f"API request failed with status code {response.status_code}")

