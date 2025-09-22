# Module 4 Assignment – Test Suite

**Name:** Shreya Kodati (skodati1)  
**Module Info:** Module 4 Pytest and Sphinx – Due on 09/22/2025 at 11:59 EST

## Approach

### tests/test_analysis_format.py: 
Tests the correctness and formatting of analysis metrics. Verifies percentages are rounded to two decimal places. Ensures labels in the dashboard match expected values. Confirms computed averages and counts are correctly displayed.

### tests/test_buttons.py: 
Tests the behavior of Flask endpoints triggered by front-end buttons. /pull button: Checks scraping is triggered and handles concurrent requests. /update button: Verifies that analysis updates correctly when no scrape is in progress. Tests response codes and flash messages for busy gating scenarios.

### tests/test_db_insert.py: 
Tests database insertion and data integrity for applicant data. Ensures new data rows are inserted correctly. Validates idempotency: duplicate pulls do not create duplicate records. Confirms basic query functions return expected keys and values.

### tests/test_flask_page.py: 
Tests overall Flask application setup and route availability. Ensures the Flask app factory exists and can be instantiated. Confirms routes (/, /pull, /update) return expected status codes.

### tests/test_integration_end_to_end.py: 
End-to-end tests combining scraping, database update, and front-end rendering. Simulates a full workflow: scraping → reload → analysis → page render. Checks multiple pulls with overlapping data remain unique. Validates final displayed metrics match the expected database state.

## Sphinx Documentation
- **Location:** `module_4/docs/source/`  
- **Files included:**
  - `conf.py` — Sphinx configuration, autodoc setup
  - `index.rst` — Overview, architecture, API reference, testing guide
  - `Makefile` / `make.bat` — build commands for HTML
  - `_build/` — generated HTML output
- **Build command:**  
  ```bash
  sphinx-build -b html module_4/docs/source module_4/docs/build/html
Autodoc modules documented:
scrape.py
clean.py
load_data.py
query_data.py
flask_app.py

### GitLab CI Integration
Pipeline is functioning.

### References:
Lecture notes, course readings, documentation for testing Flask apps with Python unittest and pytest, and sphinx documentation.

### Known Bugs
Tests rely on a live database connection and may return 404 if routes are not correctly registered. Tests show room for improvement across code.