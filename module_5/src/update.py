"""
Updates applicant data by scraping new pages and processing them.
Calls scrape_data.py to fetch the latest results from The Grad Cafe.
Cleans and processes data using clean.py and the LLM-based reformatter.
Stores results into JSON files, which are later inserted into the database via reload_data.py.
"""
import json
import os
import subprocess
from .scrape_data import scrape_page
from .utils import HTTP_POOL_MANAGER, DEFAULT_USER_AGENT

# Module 2 just means old file and module 3 means file after updating.
# Naming has no effect on refreshing data beyond this module
MODULE2_FILE = "module_3/applicant_data.json.jsonl"
MODULE3_FILE = "module_3/applicant_data_fixed.jsonl"
LLM_APP_FILE = "module_2/llm_hosting/app.py"  # Path to your LLM CLI script
MAX_PAGE = 2000  # max number of pages to try if no stop condition

# Temp files to store in different json formats after scraping and
# running through LLM
TEMP_INPUT_FILE = "module_3/temp_new_rows.json"
TEMP_OUTPUT_FILE = "module_3/temp_new_rows_llm.json"


def convert_to_jsonl(input_file, output_file):
    """
    Converts a multi-line JSON file containing a JSON array into a
    single-line JSONL format.

    Args:
        input_file (str): Path to the input JSON file (containing an array).
        output_file (str): Path for the output JSONL file.
    """
    objs = []
    buffer = ""

    # Read and parse objects
    with open(input_file, "r", encoding="utf-8") as infile:

        for line in infile:
            line = line.strip()
            if not line:
                continue
            buffer += line
            try:
                obj = json.loads(buffer)
                objs.append(obj)
                buffer = ""  # reset after parse
            except json.JSONDecodeError:
                # keep accumulating until valid JSON object
                continue

    # Save in JSONL format (1 object per line)
    with open(output_file, "w", encoding="utf-8") as outfile:
        for obj in objs:
            outfile.write(json.dumps(obj, ensure_ascii=False))
            outfile.write("\n")

    print(f"Converted {len(objs)} objects → {output_file}")


# convert_to_jsonl(MODULE2_FILE, MODULE3_FILE) # This line was likely for initial setup

def load_jsonl(filepath):
    """
    Loads a JSONL file (one JSON object per line) into a list of dictionaries.

    Args:
        filepath (str): Path to the JSONL file.

    Returns:
        list: A list of dictionaries representing the JSON objects.
    """
    data = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON line: {line[:50]}... Error: {e}")
    return data


def load_json_array(filepath):
    """
    Loads a JSON array from a file into a list of dictionaries.

    Args:
        filepath (str): Path to the JSON array file.

    Returns:
        list: A list of dictionaries, or an empty list if the file is not found or invalid.
    """
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as file2:
        try:
            return json.load(file2)
        except json.JSONDecodeError as e:
            print(f"Failed to load JSON array: {e}")
            return []


def save_jsonl(data, filepath):
    """
    Saves a list of dictionaries as a JSONL file.

    Args:
        data (list): List of dictionaries to save.
        filepath (str): Path to the output JSONL file.
    """
    with open(filepath, "w", encoding="utf-8") as file3:
        for row in data:
            json.dump(row, file3, ensure_ascii=False)
            file3.write("\n")


def save_json_array(data, filepath):
    """
    Saves a list of dictionaries as a formatted JSON array file.

    Args:
        data (list): List of dictionaries to save.
        filepath (str): Path to the output JSON array file.
    """
    with open(filepath, "w", encoding="utf-8") as file4:
        json.dump(data, file4, ensure_ascii=False, indent=4)


def run_llm_on_file(input_file, output_file):
    """
    Calls the LLM CLI script to process a JSON file and add additional columns.

    Args:
        input_file (str): Path to the input JSON file.
        output_file (str): Path to the output JSON file.
    """
    subprocess.run([
        "python", LLM_APP_FILE,
        "--file", input_file,
        "--out", output_file,
        "--append"  # optional
    ], check=True)


def update_data():
    """
    Scrapes new data, processes it with the LLM, and prepares it for insertion.
    """
    existing_data = load_jsonl(MODULE3_FILE)
    latest_url = existing_data[0]["url"] if existing_data else None

    print(f"Latest URL in JSONL: {latest_url}")

    new_rows = []
    stop_scraping = False

    # Leverage the pattern from scrape_data.py to initialize HTTP objects
    http_pool_manager = HTTP_POOL_MANAGER
    user_agent = DEFAULT_USER_AGENT

    for page in range(1, MAX_PAGE + 1):
        # Now, call scrape_page with the required arguments
        rows = scrape_page(page, http_pool_manager, user_agent)
        if not rows:
            break

        for row in rows:
            if row["url"] == latest_url:
                stop_scraping = True
                break
            new_rows.append(row)

        if stop_scraping:
            break

    if not new_rows:
        print("No new rows found. JSONL is up to date.")
        return

    print(f"Found {len(new_rows)} new rows. Running LLM standardization...")

    save_json_array(new_rows, TEMP_INPUT_FILE)

    # Call LLM CLI to process
    run_llm_on_file(TEMP_INPUT_FILE, TEMP_OUTPUT_FILE)

def load_json_objects(filepath):
    """
    Loads newline-separated JSON objects from a file into a list.

    Args:
        filepath (str): Path to the JSON file with newline-separated objects.

    Returns:
        list: List of dictionaries.
    """
    objs = []
    with open(filepath, "r", encoding="utf-8") as file5:
        buffer = ""
        for line in file5:
            line = line.strip()
            if not line:
                continue
            buffer += line
            # Try parsing object
            try:
                obj = json.loads(buffer)
                objs.append(obj)
                buffer = ""  # reset after successful parse
            except json.JSONDecodeError:
                # not complete yet, keep accumulating
                continue
    return objs


def save_json_objects(filepath, objs):
    """
    Saves a list of dictionaries as newline-separated JSON objects.

    Args:
        filepath (str): Path to the output JSON file.
        objs (list): List of dictionaries to save.
    """
    with open(filepath, "w", encoding="utf-8") as file6:
        for obj in objs:
            json.dump(obj, file6, ensure_ascii=False)
            file6.write("\n")


def prepend_llm_to_app(llm_file, app_file):
    """
    Prepends data from the LLM output file to the main applicant data file.

    Args:
        llm_file (str): Path to the LLM processed data file.
        app_file (str): Path to the main applicant data file.
    """
    # Load both
    llm_objs = load_json_objects(llm_file)
    app_objs = load_json_objects(app_file)

    # Prepend LLM rows to application rows
    combined = llm_objs + app_objs

    # Save back to app_file
    save_json_objects(app_file, combined)

    print(f"Prepended {len(llm_objs)} LLM rows. New total: {len(combined)}")

if __name__ == "__main__":
    update_data()
    prepend_llm_to_app(TEMP_OUTPUT_FILE, MODULE2_FILE)

    # Remove temporary files
    files_to_delete = [MODULE3_FILE, TEMP_INPUT_FILE]
    for f in files_to_delete:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted: {f}")
