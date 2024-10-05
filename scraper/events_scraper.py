from cmu_events_scraper import scrape_events_from_cmu_pages
from pittsburgh_events_scraper import scrape_events_from_pittsburgh_pages
import json

def main():
    all_events= []
    all_cmu_events = scrape_events_from_cmu_pages()
    print("Fetched {} events from cmu webpages.".format(len(all_cmu_events)))

    all_pittsburgh_events = scrape_events_from_pittsburgh_pages()
    print("Fetched {} events from pittsburgh webpages.".format(len(all_pittsburgh_events)))

    all_events.extend(all_cmu_events)
    all_events.extend(all_pittsburgh_events)

    with open("raw_data/dump-event_data.json", "w") as f:
        json.dump(all_events, f, indent=4)
        
    print("Saved {} events to path raw_data/dump-event_data.json.".format(len(all_events)))

if __name__ == '__main__':
    main()