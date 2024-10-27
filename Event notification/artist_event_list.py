from __future__ import print_function
import os.path
from datetime import datetime
import requests
import pandas as pd

# Importing GoogleCalendarNotifier from the calendarnotification.py file
from calendarnotification import GoogleCalendarNotifier

class ArtistEventList:
    api_key = 'YN4claSsPUHH14UbvOzseEz8T6DN8jL5'
    
    def __init__(self, calendar_notifier):
        self.calendar_notifier = calendar_notifier
        self.events_data = []  # To store event information
    
    def search_artist_events(self, artist_name, page=0, size=50):
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={self.api_key}&keyword={artist_name}&classificationName=music&page={page}&size={size}'
        
        try:
            response = requests.get(url, timeout=10)  # Added timeout of 10 seconds
        except requests.exceptions.Timeout:
            print(f"Request for {artist_name} timed out.")
            return []

        if response.status_code == 200:
            print(f"API request successful for {artist_name}")
        else:
            print(f"API request failed with status code {response.status_code} for {artist_name}")
            return []
        
        events = response.json().get('_embedded', {}).get('events', [])
        return events

    def check_and_notify_artist(self, artist_name):
        page = 0
        size = 100

        while True:
            events = self.search_artist_events(artist_name, page=page, size=size)
            if not events:
                print(f"No more events found for {artist_name}")
                break
            
            for event in events:
                # Get the event ID
                event_id = event.get('id')
                event_name = event.get('name')
                sales_info = event.get('sales', {}).get('public', {})
                onsale_time = sales_info.get('startDateTime', 'No onsale')

                venue_info = event.get('_embedded', {}).get('venues', [{}])[0]
                venue_name = venue_info.get('name', 'Unknown Venue')
                city_name = venue_info.get('city', {}).get('name', 'Unknown City')
                state_name = venue_info.get('state', {}).get('name', 'Unknown State')
                country_name = venue_info.get('country', {}).get('name', 'Unknown Country')
                postal_code = venue_info.get('postalCode', 'Unknown Postal Code')
                address = venue_info.get('address', {}).get('line1', 'Unknown Address')
                location = f"{venue_name}, {city_name}, {state_name}, {country_name}"

                event_date = event.get('dates', {}).get('start', {}).get('dateTime', 'No event date')
                presale_info = event.get('sales', {}).get('presales', [{}])[0]
                presale_time = presale_info.get('startDateTime', 'No presale')

                # Collect all event details for Excel
                self.events_data.append({
                    'Artist': artist_name,
                    'Event Name': event_name,
                    'Event ID': event_id,
                    'Onsale Time': onsale_time,
                    'Presale Time': presale_time,
                    'Event Date': event_date,
                    'Venue Name': venue_name,
                    'City Name': city_name,
                    'State Name': state_name,
                    'Country Name': country_name,
                    'Postal Code': postal_code,
                    'Address': address,
                    'Location': location
                })

                # Add event to Google Calendar (optional)
                self.calendar_notifier.add_event(f"{event_name} (ID: {event_id})", onsale_time, presale_time, location, event_date)

            page += 1  # Move to the next page of events

    def save_to_excel(self, filename='artist_events.xlsx'):
        # Convert the events data to a pandas DataFrame and save to Excel
        df = pd.DataFrame(self.events_data)
        df.to_excel(filename, index=False)
        print(f"Events saved to {filename}")

# Top 50 Artists List
top_50_artists = [
    'Taylor Swift', 'Billie Eilish', 'The Weeknd', 'Kendrick Lamar', 'Ariana Grande', 'Post Malone', 'Eminem',
    'SZA', 'Dua Lipa', 'Zach Bryan', 'David Guetta', 'Beyoncé', 'Sabrina Carpenter', 'Gunna', 'Benson Boone', 
    'Hozier', 'Noah Kahan', 'Tate McRae', 'Tommy Richman', 'Bryson Tiller', 'Marshmello', 'Artemas', 'Teddy Swims',
    'Chappell Roan', 'Shaboozey', 'FloyyMenor', 'Kygo', 'Jack Harlow', 'Central Cee', 'Djo', 'd4vd', 'Tyla',
    'Rvssian', 'Mark Ambor', 'Myles Smith', 'ILLIT', 'Dasha', 'Lay Bankz', 'Michael Marcagi', 'Good Neighbours',
    'Tommy Richman', 'Bryson Tiller', 'Zach Bryan', 'David Guetta', 'Benson Boone', 'Sabrina Carpenter',
    'Beyoncé', 'SZA', 'Artemas', 'FloyyMenor'
]

# Initialize the notifier and the artist event list
if __name__ == "__main__":
    calendar_notifier = GoogleCalendarNotifier(credentials_file='C:\\Users\\Sohyon\\OneDrive\\Desktop\\ticketsmaster\\Event notification\\credentials.json')
    artist_event_list = ArtistEventList(calendar_notifier)

    # Loop through all top 50 artists and fetch events
    for artist in top_50_artists:
        print(f"Fetching events for {artist}")
        artist_event_list.check_and_notify_artist(artist)

    # Save all the events to an Excel file
    artist_event_list.save_to_excel('artist_events.xlsx')
