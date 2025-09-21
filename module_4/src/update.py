"""
Updates applicant data by scraping new pages and processing them. 
Calls scrape_data.py to fetch the latest results from The Grad Cafe. 
Cleans and processes data using clean.py and the LLM-based reformatter. 
Stores results into JSON files, which are later inserted into the database via reload_data.py.
"""
import json
import os
from scrape_data import scrape_page
import subprocess

# Module 2 just means old file and module 3 means file after updating. 
# Naming has no effect on refreshing data beyond this module
MODULE2_FILE = "module_3/applicant_data.json.jsonl"
MODULE3_FILE = "module_3/applicant_data_fixed.jsonl"
LLM_APP_FILE = "module_2/llm_hosting/app.py"  # Path to your LLM CLI script
MAX_PAGE = 2000  # max number of pages to try if no stop condition

# Temp files to store in different json formats after scraping and 
# running through LLM
temp_input_file = "module_3/temp_new_rows.json"
temp_output_file = "module_3/temp_new_rows_llm.json"

# Convert multi-line JSON objects into single-line JSONL format.
def convert_to_jsonl(input_file, output_file):
    objs = []
    buffer = ""

    # Read and parse objects
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
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
    with open(output_file, "w", encoding="utf-8") as f:
        for obj in objs:
            f.write(json.dumps(obj, ensure_ascii=False))
            f.write("\n")

    print(f"Converted {len(objs)} objects → {output_file}")

convert_to_jsonl(MODULE2_FILE, MODULE3_FILE)

# Load JSONL file as a list of dicts
def load_jsonl(filepath):
    data = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON line: {line[:50]}... Error: {e}")
    return data

# Load a JSON array from file
def load_json_array(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Failed to load JSON array: {e}")
            return []

# Save list of dicts as JSONL
def save_jsonl(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        for row in data:
            json.dump(row, f, ensure_ascii=False)
            f.write("\n")
# Save list of dicts as JSON array (for LLM input)
def save_json_array(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Call the LLM CLI to add the two extra columns
def run_llm_on_file(input_file, output_file):
    subprocess.run([
        "python", LLM_APP_FILE,
        "--file", input_file,
        "--out", output_file,
        "--append"  # optional
    ], check=True)

# update the data based on latest entry in original json
def update_data():
    existing_data = load_jsonl(MODULE3_FILE)
    latest_url = existing_data[0]["url"] if existing_data else None

    print(f"Latest URL in JSONL: {latest_url}")

    new_rows = []
    stop_scraping = False

    for page in range(1, MAX_PAGE + 1):
        rows = scrape_page(page)
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

    save_json_array(new_rows, temp_input_file)

    # Call LLM CLI to process
    run_llm_on_file(temp_input_file, temp_output_file)

# Load newline-separated JSON objects into a list.
def load_json_objects(filepath):
    objs = []
    with open(filepath, "r", encoding="utf-8") as f:
        buffer = ""
        for line in f:
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

# Save list of dicts as newline-separated JSON objects.
def save_json_objects(filepath, objs):
    with open(filepath, "w", encoding="utf-8") as f:
        for obj in objs:
            json.dump(obj, f, ensure_ascii=False)
            f.write("\n")

# Append llm results to beginning on json
def prepend_llm_to_app(llm_file, app_file):
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
    prepend_llm_to_app(temp_output_file, MODULE2_FILE)
    
    # Remove temporary files
    files_to_delete = [MODULE3_FILE, temp_input_file]
    for f in files_to_delete:
        try:
            if os.path.exists(f):
                os.remove(f)
                print(f"Deleted: {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")
