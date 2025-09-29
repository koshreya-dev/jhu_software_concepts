"""
Refreshes the existing applicant dataset with new scraped data.
Reads temporary JSON files produced by the scraper and LLM pipeline.
Cleans up formatting issues and merges new rows into the database.
"""
import os
import json
import psycopg_pool
from .utils import create_record_from_json

# Use the 'DATABASE_URL' environment variable to connect to the database.
# pylint: disable=consider-using-sys-exit
pool = psycopg_pool.ConnectionPool(os.environ['DATABASE_URL'], min_size=0, max_size=80)

# Use dataset that is created from running update_data.py
JSONL_FILE_PATH = r'C:\Users\Shreya\jhu_software_concepts\module_3\temp_new_rows_llm.json'
TABLE_NAME = 'applicants'

# Empty list to populate
DATA_TO_INSERT = []

# Open and process the JSONL file
try:
    with open(JSONL_FILE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            record = create_record_from_json(line)
            DATA_TO_INSERT.append(record)
except FileNotFoundError:
    print(f"Error: The file {JSONL_FILE_PATH} was not found.")
    exit()
except json.JSONDecodeError as e:
    print(f"Error decoding JSON from file: {e}")
    exit()

# Re-order data for insertion
DATA_TO_INSERT.reverse()

# Insert data into the database
if not DATA_TO_INSERT:
    print("No records to insert. The JSONL file might be empty or invalid.")
else:
    columns = [
        'program', 'comments', 'date_added', 'url', 'status', 'term',
        'us_or_international', 'gpa', 'gre', 'gre_v', 'gre_aw', 'degree',
        'llm_generated_program', 'llm_generated_university'
    ]

    with pool.connection() as conn:
        with conn.cursor() as cur:
            # Use executemany for bulk insertion
            SQL_COMMAND = (
                f"INSERT INTO {TABLE_NAME} ({', '.join(columns)}) "
                f"VALUES ({', '.join(['%s'] * len(columns))})"
            )
            cur.executemany(SQL_COMMAND, DATA_TO_INSERT)
            print(f"Successfully inserted {len(DATA_TO_INSERT)} records into {TABLE_NAME}")

# Close the pool
pool.close()
print("Script finished and pool closed.")
