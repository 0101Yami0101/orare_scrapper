import os
import json
import re


def extract_and_process_data(json_file='yt_data.json'):
    """
    Process the scrap data into a format easily writable to spreadsheet
    """
    # regex patterns for extracting email addresses and Telegram links
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    tg_pattern = r't.me/[\w_]+'

    # Load JSON data from the file
    with open(json_file, 'r') as file:
        data = json.load(file)

    result = []

    for item in data:
        channel_link = item.get('channel_link', '')
        channel_name = item.get('channel_name', '')  # Extract channel name
        email_matches = re.findall(email_pattern, item.get('channel_about', '') + ' ' + item.get('video_description', ''))
        tg_matches = re.findall(tg_pattern, item.get('channel_about', '') + ' ' + item.get('video_description', ''))

        #current item
        item_data = {
            "channel_name": channel_name,  
            "channel_link": channel_link,
            "email": list(set(email_matches)), 
            "tg": list(set(tg_matches))        
        }

        result.append(item_data)

    # Save the processed data to a new JSON file
    with open('processed_data.json', 'w') as file:
        json.dump(result, file, indent=4)

    return


