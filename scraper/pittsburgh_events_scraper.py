import requests
import re
from bs4 import BeautifulSoup

class CFG:
    PITTSBURGH_EVENTS_URL=  'https://pittsburgh.events/'
    PITTSBURGH_CITY_PAGE_URL = "https://www.pghcitypaper.com/pittsburgh/EventSearch?page={}&v=d"
    DOWNTOWN_EVENTS_URL = 'https://downtownpittsburgh.com/events/'

def fetch_events_from_pittsburgh_events():
    '''
    Used pagination based approach to fetch events from the website,
    since the website retrieves content on a page level. The event 
    specific details are filtered from HTML src using regex matching.
    '''
    base_url = CFG.PITTSBURGH_EVENTS_URL
    events = []
    page_num = 1

    while True:
        url = "{}?pagenum={}".format(base_url, page_num)
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text()

        pattern = r'(\w{3})\s+(\d{2})\s+(\d{4})\s+(\d{1,2}:\d{2}\s+[AP]M)\s+(\w{3})\s+([^\n]+)\s+([^\n]+)\s+(\d{5}),\s+([^,]+),\s+([^,]+),\s+([^\n]+)\s+Prices from \$(\d+)'
        
        matches = re.findall(pattern, text_content)

        if not matches:
            print("No more events found on Pittsburgh Events. Fetched events from {} pages.".format(page_num))
            break

        for match in matches:
            month, day, year, time, weekday, event_name, venue, zipcode, city, state, country, price = match
            event = {
                'event_name': event_name.strip(),
                'date': f"{month} {day}, {year}",
                'time': time,
                'location': f"{city}, {state} {zipcode}",
            }
            locationStr = ""
            if venue and len(venue.strip())>0:
                locationStr += venue

            if city and state and zipcode:
                locationStr += " {}, {} {}".format(city, state, zipcode)

            if len(locationStr)>0:
                event['location'] = locationStr

            if price:
                event['price'] = f"${price}"

            events.append(event)
        page_num += 1

    return events


def fetch_events_from_pgh_city_paper():
    '''
    Since the page contents are loaded using inherent pagination, 
    used a page_num based retrieval approach to scrape continously
    till end of pages. The details are then extracted out of the 
    event specific tags in HTML structure.
    '''
    base_url = CFG.PITTSBURGH_CITY_PAGE_URL
    events = []
    page_num = 1

    while True:
        url = base_url.format(page_num)
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        event_items = soup.find_all("div", class_="fdn-pres-content uk-flex-1 uk-padding-xsmall-right fdn-event-search-text-block")

        if not event_items:
            print("No more events found on Pittsburgh City Paper. Fetched events from {} pages".format(page_num))
            break

        for item in event_items:
            event_name_tag = item.find("p", class_="fdn-teaser-headline")
            event_name = event_name_tag.get_text(strip=True) if event_name_tag else None

            location_tag = item.find("p", class_="fdn-event-teaser-location")
            location = location_tag.get_text(strip=True) if location_tag else None

            date_time = None

            description_tag = item.find("div", class_="fdn-teaser-description")
            description = description_tag.get_text(strip=True) if description_tag else "No description available"

            if 'Ongoing' in description:
                date_time = 'Ongoing' 

            price_tag = item.find("span", class_="uk-margin-xsmall-top")
            price = price_tag.get_text(strip=True) if price_tag else None
            event = {
                'event_name': event_name,
                'location': location,
                'description': description,
            }
            if date_time:
                event['date'] = date_time
            if price:
                event['price'] = price
            events.append(event)

        page_num += 1

    return events

def fetch_events_from_downtown_pittsburgh():
    '''
    Since the webpage is static and displays all the
    events concurrently, we have simply scraped the
    contents once using BeautifulSoup. 
    '''
    url = CFG.DOWNTOWN_EVENTS_URL
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching Downtown Pittsburgh events.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    events = []

    event_items = soup.find_all('div', class_='eventitem')

    for item in event_items:
        event_name = item.find('h1').get_text(strip=True)
        event_date_time = item.find('div', class_='eventdate').get_text(strip=True)

        date, time = event_date_time.split('|') if '|' in event_date_time else (event_date_time, '')
        
        event_date = date.strip() 
        event_time = time.strip() 

        description = item.find('div', class_='copyContent').get_text(strip=True, separator=' ')
        description = description.replace(event_date_time, '').strip()
        
        event = {
            'event_name': event_name,
            'description': description,
        }
        if event_date:
            event['date'] = event_date
        if event_time:
            event['time'] = event_time

        events.append(event)
    return events

def scrape_events_from_pittsburgh_pages():
    all_events = []

    pittsburgh_events = fetch_events_from_pittsburgh_events()
    all_events.extend(pittsburgh_events)

    downtown_events = fetch_events_from_downtown_pittsburgh()
    all_events.extend(downtown_events)
    
    newspaper_events = fetch_events_from_pgh_city_paper()
    all_events.extend(newspaper_events)

    return all_events

