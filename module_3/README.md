Module 3 Assignment

Name: Shreya Kodati (skodati1)

Module Info: Module 3 SQL Data Analysis Due on 09/14/2025 at 11:59 EST

Approach:

load_data.py: Loads applicant data from the PostgreSQL database into a structured format for further analysis. Connects to the database using psycopg_pool and the environment variable DATABASE_URL.Executes a query to fetch all applicant records.Converts rows into JSON objects and saves them into module_3/applicant_data.json.jsonl.

reload_data.py: Refreshes the existing applicant dataset with new scraped data. Reads temporary JSON files produced by the scraper and LLM pipeline. Cleans up formatting issues and merges new rows into the database. 

query_data.py: Provides SQL queries for analyzing the applicant data. Contains parameterized queries for filtering by program, degree, status, and date ranges. Allows exporting query results to JSON or printing directly to the console.

update.py: Updates applicant data by scraping new pages and processing them. Calls scrape_data.py to fetch the latest results from The Grad Cafe. Cleans and processes data using clean.py and the LLM-based reformatter. Stores results into JSON files, which are later inserted into the database via reload_data.py.

Front-End Files
app.py: Flask application providing a web-based interface to interact with the dataset. Uses flash messages to inform the user of scraping/analysis progress.

/pull_data: Starts scraping and reloads data in a background thread.

/update_analysis: Updates analysis results from the latest database state.

templates/base.html: Shared layout for all web pages.Defines navigation bar with two main buttons: Pull Data and Update Analysis.Displays flash messages from Flask to notify users about scraping or updating events. Provides consistent styling and layout for child templates.

templates/index.html:Main landing page of the application.Extends base.html and contains the analysis dashboard.Displays query results and visualizations powered by query_data.py. Refreshes after updates so users can immediately see new applicant statistics.

References:
I used lecture notes, course readings, Flask documentation, and psycopg_pool documentation for building database-backed Flask applications.

Known Bugs: No known bugs.