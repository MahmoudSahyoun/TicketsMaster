from scrapingbee import ScrapingBeeClient

client = ScrapingBeeClient(api_key='1DFC2Q2MAR9ZGNW6JZLU2GMIJ07E4Y8F9TQWYPNO537UAU53IQ4OIEQS9YDFORL7L4FVIL9BJ9642X5J')

response = client.get("https://www.ticketsmaster.com", params={'block_resources': 'false'})


print('Response HTTP Status Code: ', response.status_code)
print('Response HTTP Response Body: ', response.content)
