import requests
from bs4 import BeautifulSoup
import ssl
import certifi
import csv

def scrape_pittsburgh_info():
    url = "https://pittsburghpa.gov/pittsburgh/pgh-about"
    
    response = requests.get(url, verify=False)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        main_content = soup.find('div', id='article')
        if main_content:
            sections = main_content.find_all('div', class_='collapsing-content')

            data = []

            for section in sections:
                try:
                    title = section.find('a').text.strip()
                    
                    content = section.find('div', class_='well').text.strip()
                    
                    data.append([title, content])
                except: print(section)

            print("Written records to csv file.")

        else:
            print("Main content not found on the page.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
    return data


def scrape_mayers_info():
    url = "https://pittsburghpa.gov/mayor"
    
    response = requests.get(url, verify=False)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

    mayors = mayors = [
    "denny-mayor", "darraugh-mayor", "snowden-mayor",
    "murray-mayor", "lowrie-mayor","pettigrew-mayor",
    "mcclintock-mayor", "little-mayor", "irwin-mayor",
    "thomson-mayor", "hay-mayor", "howard-mayor",
    "kerr-mayor", "adams-mayor", "herron-mayor",
    "barker-mayor", "jguthrie-mayor", "riddle-mayor",
    "volz-mayor","bingham-mayor", "weaver-mayor",
    "wilson-mayor", "sawyer-mayor", "lowry-mayor",
    "mccarthy-mayor", "blackmore-mayor", "bush-mayor",
    "liddell-mayor", "lyon-mayor", "fulton-mayor",
    "mccallin-mayor", "gourley-mayor", "mckenna-mayor",
    "ford-mayor", "diehl-mayor", "brown-mayor", "obrown-mayor",
    "hays-mayor", "gguthrie-mayor", "magee-mayor",
    "armstrong-mayor", "babcock-mayor", "kline-mayor",
    "jherron-mayor", "mcnair-mayor", "scully-mayor",
    "lawrence-mayor", "gallagher-mayor", "barr-mayor",
    "flaherty-mayor", "caliguiri-mayor", "masloff-mayor",
    "murphy-mayor", "oconnor-mayor", "ravenstahl-mayor",
    "mayor-peduto", "mayor-profile"
    ]

    data = []
    for mayor in mayors:
        try:
            response = requests.get(f'{url}/{mayor}', verify = False)
            if response.status_code == 200:
                soupObj = BeautifulSoup(response.text, 'html.parser')
                main_content = soupObj.find('div', class_='col-sm-9')
                name = main_content.find('span', class_ = 'person')
                data.append([name.text, main_content.text])
        except:pass

    return data
if __name__ == "__main__":
    data = scrape_pittsburgh_info()
    data.extend(scrape_mayers_info())

    with open('raw_data/pittsburgh_info.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['section', 'text'])
        writer.writerows(data)