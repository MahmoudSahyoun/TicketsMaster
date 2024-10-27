from artist_event_list import ArtistEventList
from add_to_calendar import AddToCalendar

# Example usage
api_key = 'mo2Y8gSh2d6tJxh3R2MgjbFhRfFwNAZj'
calendar_handler = AddToCalendar()
event_list = ArtistEventList(api_key, calendar_handler)
artist_name = 'The Weekend'
event_list.check_and_notify_artist(artist_name)
