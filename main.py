import json
import os
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

#all sport rss feeds
menFeeds = {
    'baseball': 'https://www.ttusports.com/sports/bsb/2024-25/schedule?print=rss',
    'basketball': 'https://www.ttusports.com/sports/mbkb/2024-25/schedule?print=rss',
    'cross country': 'https://www.ttusports.com/sports/mxc/2024-25/schedule?print=rss',
    'football': 'https://www.ttusports.com/sports/fball/2024-25/schedule?print=rss',
    'golf': 'https://www.ttusports.com/sports/mgolf/2024-25/schedule?print=rss',
    'tennis': 'https://www.ttusports.com/sports/mten/2024-25/schedule?print=rss',
}
#women sport rss feeds
womanFeeds = {
    'basketball': 'https://www.ttusports.com/sports/wbkb/2024-25/schedule?print=rss',
    'cross country': 'https://www.ttusports.com/sports/wxc/2024-25/schedule?print=rss',
    'golf': 'https://www.ttusports.com/sports/wgolf/2024-25/schedule?print=rss',
    'soccer': 'https://www.ttusports.com/sports/wsoc/2024-25/schedule?print=rss',
    'softball': 'https://www.ttusports.com/sports/sball/2024-25/schedule?print=rss',
    'volleyball': 'https://www.ttusports.com/sports/wvball/2024-25/schedule?print=rss',
    'track and field': 'https://www.ttusports.com/sports/wtrack/2024-25/schedule?print=rss',
    'beach volleyball': 'https://www.ttusports.com/sports/beachvball/2024-25/schedule?print=rss',
    
}

def fetch_rss_feed(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
    }
    response = requests.get(url, headers=headers)
    print(response.headers)  # Debug: print response headers
    response.raise_for_status()  # Ensure HTTP status is OK
    try:
        root = ET.fromstring(response.content)  # Parse XML
        print("XML Parsed Successfully!")  # Debug
        return root
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

# Parse RSS feed items
def parse_rss_feed(root):
    # Define namespaces
    namespaces = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "ps": "http://www.prestosports.com/rss/schedule"
    }

    # Extract items
    items = []
    for item in root.findall(".//item"):
        data = {
            "title": item.find("title").text if item.find("title") is not None else None,
            "link": item.find("link").text if item.find("link") is not None else None,
            "description": item.find("description").text if item.find("description") is not None else None,
            "category": item.find("category").text if item.find("category") is not None else None,
            "pubDate": item.find("pubDate").text if item.find("pubDate") is not None else None,
            "dc_date": item.find("dc:date", namespaces).text if item.find("dc:date", namespaces) is not None else None,
            "score": item.find("ps:score", namespaces).text if item.find("ps:score", namespaces) is not None else None,
            "opponent": item.find("ps:opponent", namespaces).text if item.find("ps:opponent", namespaces) is not None else None,
        }
        items.append(data)
    return items

# Categorize items into men and women
def categorize_items(items):
    categorized_data = {"men": [], "women": []}
    for item in items:
        if "men" in (item["category"] or "").lower():
            categorized_data["men"].append(item)
        elif "women" in (item["category"] or "").lower():
            categorized_data["women"].append(item)
    return categorized_data



# Save or update the JSON file
def save_to_json_file(categorized_data, file_path):
    # # Check if the file already exists
    # if os.path.exists(file_path):
    #     with open(file_path, "r") as f:
    #         existing_data = json.load(f)
    # else:
    #     existing_data = {"men": [], "women": []}

    # Save back to the file
    with open(file_path, "w") as f:
        json.dump(categorized_data, f, indent=4)

# Main function
if __name__ == "__main__":
    json_file_path = "sports_data.json"  # Path to the JSON file
    categorized_data = {"men": {}, "women": {}}  # Initialize structure

    # # Fetch and parse the feed
    # root = fetch_rss_feed(rss_feed_url)
    # items = parse_rss_feed(root)
    for sport, url in menFeeds.items():
        print(f"Fetching {sport} feed...")
        try:
            root = fetch_rss_feed(url)
            items = parse_rss_feed(root)
            categorized_data["men"][sport] = items
        except Exception as e:
            print(f"Error fetching {sport} feed: {e}")
    
    for sport, url in womanFeeds.items():
        print(f"Fetching {sport} feed...")
        try:
            root = fetch_rss_feed(url)
            items = parse_rss_feed(root)
            categorized_data["women"][sport] = items
        except Exception as e:
            print(f"Error fetching {sport} feed: {e}")
        
         
    

    # Save to JSON file
    save_to_json_file(categorized_data, json_file_path)

    print(f"Data saved to {json_file_path}")