# Module 2 Assignment 
Name: Shreya Kodati (skodati1)

Module Info: Module 2 Due on 09/7/2025 at 11:59 EST

Approach: 

## scrape_data.py

_robot_parser
Checks whether scraping the provided URL is allowed by the site’s robots.txt. It reads the robots.txt file of The Grad Cafe and uses Python’s robotparser to determine permission, and it prints a message indicating whether access is allowed or denied. 

scrape_page
Scrapes a specific page from The Grad Cafe survey results. First, it verifies permission using _robot_parser, then fetches the HTML using urllib3.PoolManager. It parses the page with BeautifulSoup and calls clean_data from clean.py to extract structured information.

save_data(all_data)
Saves the collected data into a JSON file in the module_2 folder. Automatically creates the folder if it doesn’t exist and uses json.dump with indentation for the correct format. 

load_data(filepath="module_2/applicant_data.json")
Loads applicant data from a JSON file if it exists. Prints the number of entries loaded and returns the data as a list. If the file does not exist, prints a message and returns an empty list.

## clean.py

clean_data(soup)
Takes a BeautifulSoup object representing a page of The Grad Cafe survey results and extracts structured information. Iterates through table rows, capturing program, degree, date added, status, URL, term, international status, GPA, GRE scores, and comments. It cleans and flattens text where necessary to ensure consistent formatting. 

## app.py

LLM called to further clean the json outputted from scape_data.py


references: I used the readings and lecture notes, as well as the documentation from real-python for scraping and cleaning the website data.

Known Bugs:
There are no known bugs
