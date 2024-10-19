import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

def rename_key(event, old_key, new_key):
    if old_key in event:
        event[new_key] = event.pop(old_key)
    return event

def rename_and_clean_downtown_data(events):
    renamed_events = []
    for event in events:
        renamed_event = rename_key(event, "name", "event_name")
        renamed_events.append(renamed_event)
    return renamed_events

def combine_jsons(cmu_data, downtown_data):
    return cmu_data + downtown_data

def remove_links(text):
    return re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

def parse_date(date_str):
    formats = ['%A, %B %d, %Y', '%A, %B %d', '%B %d, %Y', '%b %d, %Y', '%B %d']  
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date, fmt 
        except (ValueError, TypeError):
            continue
    return None, None

def format_date_range(start_date, end_date, start_fmt, end_fmt):
    if start_date == end_date:
        if '%Y' in start_fmt:
            return start_date.strftime('%B %d, %Y')
        elif '%A' in start_fmt:
            return start_date.strftime('%A, %B %d')
        else:
            return start_date.strftime('%B %d')
    else:
        if '%Y' in start_fmt and '%Y' in end_fmt:
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        elif '%A' in start_fmt:
            return f"{start_date.strftime('%A, %B %d')} - {end_date.strftime('%A, %B %d')}"
        else:
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d')}"

def clean_event(event):
    cleaned_event = {}
    for key, value in event.items():
        if isinstance(value, str):
            cleaned_event[key] = remove_links(value)
        else:
            cleaned_event[key] = value
    return cleaned_event

def combine_events(events):
    grouped_events = defaultdict(list)
    for event in events:
        if 'date' in event:
            group_key = (event['event_name'], event.get('location'), event.get('time'), event.get('price'))
            grouped_events[group_key].append(event)
        else:
            grouped_events[None].append(event)
    combined_events = []
    for group_key, event_list in grouped_events.items():
        if group_key is None:
            combined_events.extend(event_list)
            continue
        valid_events = [event for event in event_list if parse_date(event['date'])[0] is not None]
        invalid_events = [event for event in event_list if parse_date(event['date'])[0] is None]
        valid_events.sort(key=lambda x: parse_date(x['date'])[0])
        i = 0
        while i < len(valid_events):
            temp_event = valid_events[i]
            start_date, start_fmt = parse_date(temp_event['date'])
            prev_date = start_date
            prev_fmt = start_fmt
            j = i + 1
            while j < len(valid_events):
                curr_event = valid_events[j]
                curr_date, curr_fmt = parse_date(curr_event['date'])
                if curr_date == prev_date + timedelta(days=1):
                    prev_date = curr_date
                    prev_fmt = curr_fmt
                    j += 1
                else:
                    break
            event_output = {
                "event_name": temp_event['event_name'],
                "date": format_date_range(start_date, prev_date, start_fmt, prev_fmt),
            }
            if 'description' in temp_event:
                event_output['description'] = temp_event['description']
            if 'time' in temp_event:
                event_output['time'] = temp_event['time']
            if 'location' in temp_event:
                event_output['location'] = temp_event['location']
            if 'price' in temp_event:
                event_output['price'] = temp_event.get('price', None)
            combined_events.append(event_output)
            i = j
        combined_events.extend(invalid_events)
    return combined_events

def remove_duplicate_event(events, event_name_to_remove):
    filtered_events = []
    event_found = False
    for event in events:
        if event.get("event_name") == event_name_to_remove:
            if not event_found:
                filtered_events.append(event)
                event_found = True
        else:
            filtered_events.append(event)
    return filtered_events

def process_event_data(cmu_file_path, downtown_file_path):
    with open(cmu_file_path, 'r') as file:
        cmu_event_data = json.load(file)
    with open(downtown_file_path, 'r') as file:
        downtown_event_data = json.load(file)
    print(f"Number of events before processing CMU data: {len(cmu_event_data)}")
    cleaned_cmu_data = [clean_event(event) for event in cmu_event_data]
    print(f"Number of events before processing Downtown data: {len(downtown_event_data)}")
    cleaned_downtown_data = rename_and_clean_downtown_data(downtown_event_data)
    combined_event_data = combine_jsons(cleaned_cmu_data, cleaned_downtown_data)
    print(f"Number of events after combining: {len(combined_event_data)}")
    combined_event_data = remove_duplicate_event(combined_event_data, "CMU Pantry Hours")
    combined_event_data = combine_events(combined_event_data)
    print(f"Number of events after processing: {len(combined_event_data)}")
    with open('combined_events.json', 'w') as output_file:
        json.dump(combined_event_data, output_file, indent=4)

process_event_data('./data/raw_data/dump-event_data.json', './data/raw_data/DowntownEvents.json')