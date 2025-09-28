"""
This module contains functions for scraping applicant data from The Grad Cafe.

It includes functionality to:
- Check scraping permissions using robots.txt.
- Scrape data from multiple pages of the website using BeautifulSoup.
- Clean and process the scraped data.
- Save the cleaned data to a JSON file.
- Load the data from the JSON file for verification or further use.
"""
import json
import os
from urllib import robotparser
import urllib.error
import urllib3
from bs4 import BeautifulSoup
# The 'clean' module is likely in the same directory. The relative import is
# the correct way to handle this in a package structure.
from .clean import clean_data


def _robot_parser(site_url, agent):
    """
    Checks robots.txt for permission to scrape.
    Args:
        site_url (str): The URL to check.
        agent (str): The user agent string.
    Returns:
        bool: True if scraping is permitted, False otherwise.
    """
    base_url = "https://www.thegradcafe.com/"
    parser = robotparser.RobotFileParser()
    try:
        parser.set_url(f"{base_url}robots.txt")
        parser.read()
    except urllib.error.URLError as e:
        message = f"Failed to read robots.txt for {site_url}: {e}"
        with open("robots_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
        print(message)
        return False

    can_fetch = parser.can_fetch(agent, site_url)
    message = f"{site_url} {'permitted' if can_fetch else 'NOT permitted'} per robots.txt."
    print(message)
    with open("robots_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{message}\n")
    return can_fetch


def scrape_page(page, http_pool_manager, user_agent):
    """
    Scrape a single page using BeautifulSoup.
    Args:
        page (int): The page number to scrape.
        http_pool_manager (urllib3.PoolManager): The urllib3 pool manager.
        user_agent (str): The user agent string.
    Returns:
        list: A list of scraped data rows.
    """
    url = f"https://www.thegradcafe.com/survey/index.php?page={page}"

    if not _robot_parser(url, user_agent):
        print(f"Skipping page {page} due to robots.txt restrictions.")
        return []

    try:
        response = http_pool_manager.request("GET", url)
        soup = BeautifulSoup(response.data, "html.parser")
        rows = clean_data(soup)
        return rows
    except (urllib3.exceptions.MaxRetryError, urllib.error.URLError) as e:
        print(f"Failed to scrape page {page}: {e}")
        return []


def save_data(data, file_path):
    """
    Save cleaned data into a JSON file.
    Args:
        data (list): The list of data to save.
        file_path (str): The path to the output JSON file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Saved {len(data)} rows to {file_path}")


def load_data(filepath):
    """
    Load applicant data from a JSON file.
    Args:
        filepath (str): The path to the JSON file.
    Returns:
        list: The loaded data, or an empty list if the file doesn't exist.
    """
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded {len(data)} entries from {filepath}")
        return data
    print(f"No existing file found at {filepath}. Starting with empty data.")
    return []


def main():
    """Main function to run the scraping and data saving process."""
    # Initialize urllib3 PoolManager and USER_AGENT
    http_pool_manager = urllib3.PoolManager()
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    )

    all_data = []
    file_path = "module_2/applicant_data.json"

    for p in range(1, 2000):
        all_data.extend(scrape_page(p, http_pool_manager, user_agent))

    save_data(all_data, file_path)
    load_data(file_path)


if __name__ == "__main__":
    main()
