from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

import time
from bs4 import BeautifulSoup
import requests
import re
import os
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil import parser

class CFG:
    cmu_events = {
        'URL': 'https://events.cmu.edu/all',
        'MAX_CLICKS': 100,
        'TIMEOUT': 2,
        'WEBDRIVER_TIMEOUT': 10
    }
    cmu_engage_events = {
        'URL': 'https://www.cmu.edu/engage/alumni/events/campus',
        'SUB_PAGES': ['spring-carnival', 'homecoming', 'reunions', 'alumni-awards'],
        'MONTHS_LIST': [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December",
            "Jan.", "Feb.", "Mar." , "Apr.", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."
        ]
    }
    cmu_alumni_events = {
        'URL': "https://community.cmu.edu/s/events",
        'TIMEOUT': 1
    }
    cmu_academic_calendar = {
        'URL': 'https://www.cmu.edu/hub/calendar/docs/2425-academic-calendar-list-view.xlsx'
    }

class ChromeDriver:
    def __init__(self, headless=True, no_sandbox=True):
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        if no_sandbox:
            chrome_options.add_argument('--no-sandbox')
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def get_driver(self):
        return self.driver

    def kill(self):
        if self.driver:
            self.driver.quit()

CURR_year = ' 2024'


def scrape_cmu_events(driver):
    '''
    This webpage has 1000+ recurring and annual events. For this page,
    the code repeatedly clicks on the `Show More` button till a fixed 
    number of clicks, and scrolls down till the end of page. Once the
    crawler completes execution, we use bs to extract the information
    tags.
    '''
    driver.get(CFG.cmu_events['URL'])
    time.sleep(CFG.cmu_events['TIMEOUT'])

    a = 0
    max_clicks = CFG.cmu_events['MAX_CLICKS']
    while a < max_clicks:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(CFG.cmu_events['TIMEOUT'])  
            
            show_more_button = WebDriverWait(driver, CFG.cmu_events['WEBDRIVER_TIMEOUT']).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.lw_cal_next'))
            )
            
            show_more_button.click()
            a+=1
            time.sleep(CFG.cmu_events['TIMEOUT'])
        
        except Exception as e:
            print("No more entries to load. Fetched events from {} pages from cmu events website.".format(a))
            break

    soup = BeautifulSoup(driver.page_source, 'html.parser')
        
    date_tags = soup.find_all('h3')
    extracted_event_list = []

    for date_tag in date_tags:
        date_text = ''.join(date_tag.find_all(text=True)).strip()
        event_list = date_tag.find_next('div', class_='lw_cal_event_list')
        if event_list:
            events = event_list.find_all('div', class_='lw_cal_event')
            for event in events:
                title_tag = event.find('div', class_='lw_events_title')
                title = title_tag.a.get_text(strip=True) if title_tag else None
                
                location_tag = event.find('div', class_='lw_events_location')
                location = location_tag.get_text(strip=True) if location_tag else None
                location = location if len(location)>0 else None
                time_tag = event.find('div', class_='lw_events_time')
                time_str = time_tag.get_text(strip=True) if time_tag else None

                description_tag = event.find('div', class_='lw_events_summary')
                description_str = description_tag.p.get_text(strip=True) if description_tag else None

                event_obj = {
                'date': date_text,
                'event_name': title,
                'time': time_str,
                }
                if location:
                    event_obj['location'] = location
                if description_str:
                    event_obj['description'] = description_str
                extracted_event_list.append(event_obj)

    return extracted_event_list



def extract_event_name_and_date(full_text):
    months = CFG.cmu_engage_events['MONTHS_LIST']
    for month in months:
        if month in full_text:
            match = re.search(f"({month}\\s?\\d.*)", full_text)
            if match:
                date_part = match.group(1)
                
                if "Weekend" in full_text:
                    full_text = full_text.replace("Weekend", "").strip()
                    date_part = "Weekend " + date_part.strip()
                
                if not date_part[len(month)].isspace():
                    date_part = date_part.replace(month, month + " ")
                
                event_name = full_text.split(month)[0].strip()
                return event_name, date_part.strip()
    return full_text, None


def scrape_cmu_engage_events():
    '''
    This webpage has 4 categories of sub-events. We call each
    of them iteratively and scrape events.
    '''
    events = []

    base_url = CFG.cmu_engage_events['URL']
    sub_strings = CFG.cmu_engage_events['SUB_PAGES']

    for event_tag in sub_strings:
        url = "{}/{}/index.html".format(base_url, event_tag)
        response = requests.get(url)

        if response.status_code != 200:
            print("Error fetching data")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        event_items = soup.find_all("div", class_="content")

        event = dict()
        event_name_str = ""
        event_desc_str = ""
        event_date_str = None

        for event_item in event_items:
            h1_tag = event_item.find('h1')
            p1_tag = event_item.find('p')
            date_append = None

            if h1_tag: 
                try:
                    event_string = h1_tag.text.strip()
                    event_name, date_append = extract_event_name_and_date(event_string)
                    event_name_str += "{}".format(event_name)
                    if date_append: event_date_str = date_append

                except Exception as e:
                    print("Encountered err while extracting information from cmu engage events. Err: {}.".format(e))

            if p1_tag:
                description = p1_tag.text.strip()
                event_desc_str += "{}".format(description)

        event['event_name'] = event_name_str
        event['description'] = event_desc_str

        if event_date_str:
            event['date'] = event_date_str

        sidebar = soup.find_all("div", class_ = 'blue invert')
        if sidebar:
            for sub_bar in sidebar:
                list_items = sub_bar.find_all('li')
                
                if len(list_items) >= 2:
                    date_time = list_items[0].get_text(strip=True)
                    location = list_items[1].get_text(strip=True)
                    
                    if "at" in date_time:
                        date, time = date_time.split("at", 1)
                    else:
                        date = date_time
                        time = None
                    
                    event['date'] = date.strip()
                    event['time'] = time.strip() if time else None
                    event['location'] = location.strip()
        
        events.append(event)

    return events


def scrape_cmu_alumni_events(driver):
    '''
    In this page structure, the events from the current
    page vanish once the `Next` button is pressed. We 
    have implemented a crawler that recursively crawls
    and scrapes event contents from each page.
    '''
    url = CFG.cmu_alumni_events['URL']
    driver.get(url)

    time.sleep(CFG.cmu_alumni_events['TIMEOUT'])
    events = []
    a = 0
    while True:
        try:
            current_events = driver.find_elements(By.CLASS_NAME, "slds-size_12-of-12")

            for event in current_events:
                event_html = event.get_attribute('innerHTML')
                soup = BeautifulSoup(event_html, 'html.parser')
                title_element = soup.find('a', class_='slds-text-heading_medium')
                title = title_element.text.strip() if title_element else None
                if not title:
                    continue
                else:
                    try:
                        date_element = WebDriverWait(event, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'lightning-formatted-date-time'))
                        )
                        date = date_element.text.strip() if date_element else None
                    except NoSuchElementException:
                        date = None

                    description_div = soup.find('div', class_='slds-text-body_regular description')
                    location = None
                    
                    if description_div:
                        parts = description_div.text.split('|')
                        if len(parts) > 1:
                            location = parts[1].strip()

                    event_data = {
                        "event_name": title,
                        "date": date,
                        "location": location
                    }
                    events.append(event_data)

            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'slds-button_neutral') and contains(text(), 'Next')]"))
            )

            show_more_button.click()
            a+=1

        except Exception:
            print("No more entries to load. Fetched alumni events from {} pages.".format(a))
            break
    return events

def process_day(day_str):
    day_map = {
    'M': 'Monday',
    'Tu': 'Tuesday',
    'W': 'Wednesday',
    'Th': 'Thursday',
    'F': 'Friday',
    'Sa': 'Saturday',
    'Su': 'Sunday',
    'S': 'Sunday'
    }
    try:
        if '-' in day_str:
            start_day, end_day = day_str.split('-')
            start_full = day_map.get(start_day.strip(), start_day)
            end_full = day_map.get(end_day.strip(), end_day)
            return f"{start_full} to {end_full}"
        else:
            days = day_str.split()
            full_days = [day_map.get(day.strip(), day) for day in days]
            return ' '.join(full_days)
    except: pass

def format_dates(row):
    global CURR_year
    try:
        if pd.notna(row['Date_from']):
            date_obj = parser.parse(str(row['Date_from']))
            formatted_date = date_obj.strftime("%d %B") + CURR_year

            if pd.notna(row['Date_to']):
                end_date = parser.parse(str(row['Date_to']))
                formatted_date += " to {}".format(end_date.strftime("%d %B") + CURR_year)

            return formatted_date
    except:
        CURR_year = " 2025"
        return None

def scrape_academic_calendar():
    response = requests.get(CFG.cmu_academic_calendar['URL'])
    file_path = 'temp.xlsx'

    with open(file_path, 'wb') as f:
        f.write(response.content)

    df = pd.read_excel(file_path, header=4, names=['Date_from', 'temp', 'Date_to', 'Day', 'event_name'])
    if os.path.exists(file_path):
        os.remove(file_path)
    df.drop('temp', axis=1, inplace=True)

    df_filtered = df[df['event_name'].notna()]
    
    df_filtered['date'] = df_filtered.apply(format_dates, axis=1)
    df_filtered['Day'] = df_filtered['Day'].apply(process_day)

    df_filtered = df_filtered[df_filtered['date'].notna()]
    df_filtered['date'] = df_filtered['Day'] + " " + df_filtered['date']

    return df_filtered[['event_name', 'date']].to_dict(orient='records')

def scrape_events_from_cmu_pages():
    chrome_driver = ChromeDriver(headless=True)
    driver = chrome_driver.get_driver()

    exhaustive_list_events = []

    cmu_events = scrape_cmu_events(driver)
    cmu_engage_events = scrape_cmu_engage_events()
    cmu_alumni_events = scrape_cmu_alumni_events(driver)
    cmu_academic_events = scrape_academic_calendar()

    exhaustive_list_events.extend(cmu_events)
    exhaustive_list_events.extend(cmu_engage_events)
    exhaustive_list_events.extend(cmu_alumni_events)
    exhaustive_list_events.extend(cmu_academic_events)

    chrome_driver.kill()

    return exhaustive_list_events


