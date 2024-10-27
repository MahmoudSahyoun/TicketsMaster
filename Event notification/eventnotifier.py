# artist_event_list.py

import requests
from datetime import datetime
import time
from add_to_calendar import AddToCalendar  # Import the AddToCalendar class

class ArtistEventList:
    def __init__(self, api_key, calendar_handler):
        self.api_key = api_key
        self.calendar_handler = calendar_handler

    def search_artist_events(self, artist_name, page=0, size=50):
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={self.api_key}&keyword={artist_name}&classificationName=music&page={page}&size={size}'
        response = requests.get(url)
        
        if response.status_code == 200:
            print("API request successful")
        else:
            print(f"API request failed with status code {response.status_code}")
            return []
        
        events = response.json().get('_embedded', {}).get('events', [])
        return events

    def check_and_notify_artist(self, artist_name):
        page = 0
        size = 50  # Set the size to the number of events you want per page
        events_to_notify = []

        while True:
            events = self.search_artist_events(artist_name, page=page, size=size)

            if not events:
                print(f"No more events found for {artist_name}")
                break  # Stop the loop if no more events are returned
            
            print(f"Found {len(events)} events on page {page} for {artist_name}.")
            
            for event in events:
                event_name = event['name']
                sales_info = event.get('sales', {}).get('public', {})

                # Check if 'startDateTime' exists
                onsale_time = sales_info.get('startDateTime')
                
                if not onsale_time:
                    print(f"Skipping event: {event_name}, no onsale time available.")
                    continue

                # Ensure that 'venues' and the required fields exist in the response
                venue_info = event.get('_embedded', {}).get('venues', [{}])[0]
                venue_name = venue_info.get('name', 'Unknown Venue')
                city_name = venue_info.get('city', {}).get('name', 'Unknown City')
                location = f"{venue_name}, {city_name}"
                
                # Convert onsale_time to datetime object
                onsale_datetime = datetime.fromisoformat(onsale_time[:-1])
                
                # Filter for future onsale times
                current_time = datetime.now()
                if current_time >= onsale_datetime:
                    print(f"Skipping past event: {event_name} (Onsale Time: {onsale_time})")
                    continue
                
                presale_time = event.get('sales', {}).get('presales', [{}])[0].get('startDateTime', 'No presale')

                # Print found times and location
                print(f"Onsale Time: {onsale_time}")
                print(f"Presale Time: {presale_time}")
                print(f"Location: {location}")

                # Store events to notify later
                events_to_notify.append((event_name, onsale_time, presale_time, location))

            # Go to the next page
            page += 1

        # Handle notifications for all events after processing
        for event_name, onsale_time, presale_time, location in events_to_notify:
            onsale_datetime = datetime.fromisoformat(onsale_time[:-1])
            current_time = datetime.now()
            time_until_onsale = (onsale_datetime - current_time).total_seconds()

            print(f"Time until onsale for {event_name}: {time_until_onsale} seconds")
            if time_until_onsale > 0:
                time.sleep(time_until_onsale)
            # Send event data to AddToCalendar
            self.calendar_handler.add_event(event_name, onsale_time, presale_time, location)
