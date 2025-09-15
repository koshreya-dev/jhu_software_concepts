from bs4 import BeautifulSoup
import json
import os
import urllib3
from urllib import robotparser
import urllib.error
from clean import clean_data


# Leverage urllib3 connection pooling capability
http = urllib3.PoolManager()
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"

# Leverage urllib for robotparser
def _robot_parser(site_url, agent=USER_AGENT):
    """Checks robots.txt for permission to scrape."""
    
    base_url = "https://www.thegradcafe.com/"
    parser = robotparser.RobotFileParser()
    parser.set_url(f"{base_url}robots.txt")
    
    try:
        parser.read()
    except urllib.error.URLError as e:
        message = f"Failed to read robots.txt for {site_url}: {e}"
        with open("robots_log.txt", "a", encoding="utf-8") as f:
            f.write(message + "\n")
        print(message)
        return False

    # Check if I have permission to access the page.
    can_fetch = parser.can_fetch(agent, site_url)
    if can_fetch:
        print(f'{site_url} permitted per robots.txt.')
        message = f'{site_url} permitted per robots.txt.'
    else:
        print(f'{site_url} NOT permitted per robots.txt.')
        message = f'{site_url} NOT permitted per robots.txt.'
        
    # Log to file
    with open("robots_log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")
        
    return can_fetch

# 
def scrape_page(page=1):
    """Scrape each page using BeautifulSoup"""
    
    # Update url based on page
    url = f"https://www.thegradcafe.com/survey/index.php?page={page}"

    # Skip page if no permission, based on robot.txt
    if not _robot_parser(url):
        print(f"Skipping page {page} due to robots.txt restrictions.")
        return []

    # Leverage pool manager to get data at url and input into BeautifulSoup
    response = http.request("GET", url)
    soup = BeautifulSoup(response.data, "html.parser")
    
    # Call clean_data from clean.py
    rows = clean_data(soup)

    return rows

def save_data(all_data, file_path):
    """Save cleaned data into a json file"""
    
    # Save into module_2 folder
    os.makedirs("module_2", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)
        
    return print(f"Saved {len(all_data)} rows to {file_path}")

def load_data(filepath):
    """
    Load applicant data from JSON file. If the file exists, 
    returns the data and prints the number of entries.
    """
    
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded {len(data)} entries from {filepath}")
        return data
    else:
        print(f"No existing file found at {filepath}. Starting with empty data.")
        return []

if __name__ == "__main__":
    
    # Initialize list
    all_data = []
    
    # Loop through enough pages for >30,000 responses
    for p in range(1, 2000): 
        all_data.extend(scrape_page(p))

    # Outputinto json
    save_data(all_data, file_path = "module_2/applicant_data.json")
    
    # Confirm that data is loaded correctly
    load_data("module_2/applicant_data.json")