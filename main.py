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

menLinks = {
    'baseball': 'https://www.ttusports.com/sports/bsb/2024-25/schedule',
    'basketball': 'https://www.ttusports.com/sports/mbkb/2024-25/schedule',
    'cross country': 'https://www.ttusports.com/sports/mxc/2024-25/schedule',
    'football': 'https://www.ttusports.com/sports/fball/2024-25/schedule',
    'golf': 'https://www.ttusports.com/sports/mgolf/2024-25/schedule',
    'tennis': 'https://www.ttusports.com/sports/mten/2024-25/schedule',
}

womanLinks = {
    'basketball': 'https://www.ttusports.com/sports/wbkb/2024-25/schedule',
    'cross country': 'https://www.ttusports.com/sports/wxc/2024-25/schedule',
    'golf': 'https://www.ttusports.com/sports/wgolf/2024-25/schedule',
    'soccer': 'https://www.ttusports.com/sports/wsoc/2024-25/schedule',
    'softball': 'https://www.ttusports.com/sports/sball/2024-25/schedule',
    'volleyball': 'https://www.ttusports.com/sports/wvball/2024-25/schedule',
    'track and field': 'https://www.ttusports.com/sports/wtrack/2024-25/schedule',
    'beach volleyball': 'https://www.ttusports.com/sports/beachvball/2024-25/schedule',
}

def fetch_rss_feed(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
    }
    response = requests.get(url, headers=headers)
    # print(response.headers)  # Debug: print response headers
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

#Get websites html to parse
def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
    }
    response = requests.get(url, headers=headers)
    # print(response.text)  # Debug: print response headers
    response.raise_for_status()  # Ensure HTTP status is OK
    return response.text

#Parse html to get image sources
def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    team_logos = soup.find_all("div", class_="team-logo")

    # Extract image sources
    image_sources = []
    for logo in team_logos:
        img_tag = logo.find("img")  # Find the <img> tag inside the div
        if img_tag:
            # Try to get 'data-src' first, fallback to 'src' if needed
            image_source = img_tag.get("data-src") or img_tag.get("src")
            if image_source:
                image_sources.append(image_source)

    return image_sources


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
    image_sources = {"men": {}, "women": {}}  # Initialize structure
    
    for sport, url in menLinks.items():
        print(f"Fetching {sport} feed...")
        try:
            html = get_html(url)
            items = parse_html(html)
            image_sources["men"][sport] = items
            print("Image sources fetched successfully!")
        except Exception as e:
            print(f"Error fetching {sport} feed: {e}")
            
    for sport, url in womanLinks.items():
        print(f"Fetching {sport} feed...")
        try:
            html = get_html(url)
            items = parse_html(html)
            image_sources["women"][sport] = items
            print("Image sources fetched successfully!")
        except Exception as e:
            print(f"Error fetching {sport} feed: {e}")
            
    save_to_json_file(image_sources, "image_sources.json")

    # Fetch and parse the feed
    # root = fetch_rss_feed(rss_feed_url)
    # items = parse_rss_feed(root)
    for sport, url in menFeeds.items():
        print(f"Fetching {sport} feed...")
        try:
            root = fetch_rss_feed(url)
            items = parse_rss_feed(root)
            categorized_data["men"][sport] = items
            print("Feed fetched successfully!")
        except Exception as e:
            print(f"Error fetching {sport} feed: {e}")
    
    for sport, url in womanFeeds.items():
        print(f"Fetching {sport} feed...")
        try:
            root = fetch_rss_feed(url)
            items = parse_rss_feed(root)
            categorized_data["women"][sport] = items
            print("Feed fetched successfully!")
        except Exception as e:
            print(f"Error fetching {sport} feed: {e}")
            
    
    # Combine image sources into categorized_data for men
    for sport, entries in categorized_data["men"].items():
        if sport in image_sources["men"]:
            images = image_sources["men"][sport]
            for idx, entry in enumerate(entries):
                if idx < len(images):  # Ensure there's a matching image
                    entry["image"] = images[idx]
                else:
                    entry["image"] = None  # Handle case where images are fewer

    # Combine image sources into categorized_data for women
    for sport, entries in categorized_data["women"].items():
        if sport in image_sources["women"]:
            images = image_sources["women"][sport]
            for idx, entry in enumerate(entries):
                if idx < len(images):  # Ensure there's a matching image
                    entry["image"] = images[idx]
                else:
                    entry["image"] = None  # Handle case where images are fewer
        
         
    

    # Save to JSON file
    save_to_json_file(categorized_data, json_file_path)

    print(f"Data saved to {json_file_path}")
    
 