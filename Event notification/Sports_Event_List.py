import requests
from datetime import datetime, timedelta, timezone
import pytz

class SportsEventList:
    # API credentials
    api_key = 'mo2Y8gSh2d6tJxh3R2MgjbFhRfFwNAZj'

    def __init__(self, calendar_notifier):
        self.calendar_notifier = calendar_notifier

    def search_sports_events(self, team_name, page=0, size=50):
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={self.api_key}&keyword={team_name}&classificationName=sports&page={page}&size={size}'
        response = requests.get(url)
        
        if response.status_code == 200:
            print("API request successful")
        else:
            print(f"API request failed with status code {response.status_code}")
            return []
        
        events = response.json().get('_embedded', {}).get('events', [])
        return events

    def check_and_notify_sports(self, team_name):
        page = 0
        size = 100  # Set the size to the number of events you want per page
        events_to_notify = []

        while True:
            events = self.search_sports_events(team_name, page=page, size=size)

            if not events:
                print(f"No more events found for {team_name}")
                break  # Stop the loop if no more events are returned
            
            print(f"Found {len(events)} events on page {page} for {team_name}.")
            
            for event in events:
                event_name = event.get('name')
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

                # Get event date and convert to datetime object
                event_date = event.get('dates', {}).get('start', {}).get('dateTime')
                event_datetime = datetime.fromisoformat(event_date[:-1]) if event_date else onsale_datetime

                # Define a far-future cutoff (e.g., 6 months from now)
                far_future_cutoff = datetime.utcnow() + timedelta(days=180)

                # Check if event is in the near or far future
                if event_datetime > datetime.utcnow() or event_datetime <= far_future_cutoff:
                    # Check for presale time
                    presale_info = event.get('sales', {}).get('presales', [{}])[0]
                    presale_time = presale_info.get('startDateTime', 'No presale')

                    # Print found times and location
                    print(f"Event Date: {event_datetime}")
                    print(f"Onsale Time: {onsale_time}")
                    print(f"Presale Time: {presale_time}")
                    print(f"Location: {location}")

                    # Store events to notify later
                    events_to_notify.append((event_name, onsale_time, presale_time, location, event_date))
                else:
                    print(f"Skipping event: {event_name} (Event Date: {event_datetime})")

            # Go to the next page
            page += 1

        # Handle notifications for all events after processing
        for event_name, onsale_time, presale_time, location, event_date in events_to_notify:
            self.calendar_notifier.add_event(event_name, onsale_time, presale_time, location, event_date)

# Example usage
if __name__ == '__main__':
    from calendarnotification import GoogleCalendarNotifier  # Ensure you import the correct class

    calendar_notifier = GoogleCalendarNotifier(credentials_file='C:/Users/Sohyon/OneDrive/Desktop/ticketsmaster/Event notification/credentials.json')
    sports_event_list = SportsEventList(calendar_notifier)

    # Example usage
    team_name = 'WWE'  # Replace with your preferred sports team or event keyword
    sports_event_list.check_and_notify_sports(team_name)
