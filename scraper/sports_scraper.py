from bs4 import BeautifulSoup
import requests

response = requests.get('https://www.mlb.com/pirates/team/front-office')

if response.status_code != 200:
    print("Error fetching data")

soup = BeautifulSoup(response.content, 'html.parser')
event_items = soup.find("div", class_="l-grid l-grid--two-column")
elements = []
for tag in event_items.find_all('div', class_ = 'l-grid'):
    elements.append(tag.find('table', class_ = 'p-table'))