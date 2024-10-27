import requests
import csv

class PriceTracker:
    def __init__(self, api_key, event_id, output_file):
        self.api_key = api_key
        self.event_id = event_id
        self.output_file = output_file
        self.base_url = "https://app.ticketmaster.com/discovery/v2/"

    def fetch_event_data(self):
        url = f"{self.base_url}events/{self.event_id}.json"
        params = {
            'apikey': self.api_key
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            print("API request successful!")
            return response.json()
        else:
            print(f"API request failed with status code {response.status_code}")
            return None

    def extract_section_prices(self, event_data):
        if not event_data:
            print("No event data to extract.")
            return []

        sections_data = []

        # Check if priceRanges information exists
        if "priceRanges" in event_data:
            # Loop over price ranges
            for price_range in event_data['priceRanges']:
                # Extract pricing and section name (if section name exists)
                section_info = {
                    'event_name': event_data['name'],
                    'event_date': event_data['dates']['start']['dateTime'],
                    'venue_name': event_data['_embedded']['venues'][0]['name'],
                    'section_name': price_range.get('type', 'General Admission'),  # Use section name if available
                    'min_price': price_range.get('min'),
                    'max_price': price_range.get('max'),
                    'currency': price_range.get('currency')
                }
                sections_data.append(section_info)

        return sections_data

    def save_to_csv(self, sections_data):
        with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['event_name', 'event_date', 'venue_name', 'section_name', 'min_price', 'max_price', 'currency'])
            writer.writeheader()

            for section in sections_data:
                writer.writerow(section)

        print(f"Data saved to {self.output_file}")

    def track_event(self):
        event_data = self.fetch_event_data()
        if event_data:
            print(event_data)  # Print the JSON response for debugging
            sections_data = self.extract_section_prices(event_data)
            if sections_data:
                self.save_to_csv(sections_data)
            else:
                print("No sections data found.")
        else:
            print("Failed to retrieve event data.")


# Example usage:
if __name__ == "__main__":
    api_key = "4MtKJcFof2Vz21n9v6n13tgQvpTmnlGm"
    event_id = "1778vOG621lcxQD"  # Example event ID
    output_file = "event_prices_with_sections.csv"

    price_tracker = PriceTracker(api_key, event_id, output_file)
    price_tracker.track_event()
