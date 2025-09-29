"""
Flask application providing a web-based interface to interact with the dataset.
It displays various statistics and allows users to trigger a data scraping job.
"""
import os
import subprocess
import threading
from flask import Flask, render_template, redirect, url_for, flash
import psycopg_pool
# pylint: disable=W0603, W0718, W0602, R0914


# Initialize the Flask application.
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages.

# Use a connection pool for efficient database connections.
pool = psycopg_pool.ConnectionPool(os.environ['DATABASE_URL'])

# Lock for safe concurrent access to shared resources like the SCRAPING_IN_PROGRESS flag.
scrape_lock = threading.Lock()
SCRAPING_IN_PROGRESS = False

def run_scraper():
    """
    Runs the data scraping and reloading pipeline in a background thread.

    This function sets a global flag to indicate that a scrape is in progress,
    executes the 'update.py' and 'reload_data.py' scripts, and then resets
    the flag. Flash messages are used to notify the user of the outcome.
    """
    global SCRAPING_IN_PROGRESS
    with scrape_lock:
        SCRAPING_IN_PROGRESS = True
    try:
        # Run the update + reload pipeline.
        subprocess.run(["python", "module_3/update.py"], check=True)
        subprocess.run(["python", "module_3/reload_data.py"], check=True)
        print("Scraping and reloading successful.")
    except Exception as e:
        print("Scraping failed:", e)
        # Use a category like "danger" or "error" for styling in the template.
        flash("Scraping failed: An error occurred during the update process.", "danger")
    finally:
        with scrape_lock:
            SCRAPING_IN_PROGRESS = False

@app.route("/pull", methods=["POST"])
def pull_data():
    """
    Handles the "Pull Data" button.

    This route starts the scraping process in a background thread if one is
    not already running. It uses a lock to prevent concurrent scraping jobs.
    """
    global SCRAPING_IN_PROGRESS
    with scrape_lock:
        if SCRAPING_IN_PROGRESS:
            flash("A scrape is already running. Please wait until it finishes.", "warning")
            return redirect(url_for("index"))

        # Start the scraper in a background thread.
        thread = threading.Thread(target=run_scraper, daemon=True)
        thread.start()
        flash("Scraping started! This may take a few minutes.", "info")

    return redirect(url_for("index"))

@app.route("/update", methods=["POST"])
def update_analysis():
    """
    Handles the "Update Analysis" button.

    This route triggers a re-render of the index page to show the latest
    analysis results from the database. It prevents the update if a scrape
    is currently in progress to avoid displaying stale data.
    """
    global SCRAPING_IN_PROGRESS
    with scrape_lock:
        if SCRAPING_IN_PROGRESS:
            flash("Cannot update analysis while scraping is in progress.", "warning")
            return redirect(url_for("index"))

    # Re-render the index page with a success message.
    flash("Analysis updated with the latest database results.", "success")
    return redirect(url_for("index"))

@app.route('/')
def index():
    """
    Handles the main index page, displaying analysis from the dataset.

    This function connects to the database, executes several queries to fetch
    analytics, and passes the results to the 'index.html' template for rendering.
    """
    conn = pool.getconn()
    context = {}
    try:
        with conn.cursor() as cur:
            # Query 1: Count of all applicants.
            cur.execute("SELECT COUNT(*) FROM applicants;")
            total_count = cur.fetchone()[0]

            # Query 2: Count of international applicants.
            cur.execute(
                "SELECT COUNT(*) FROM applicants WHERE us_or_international = 'International';"
            )
            international_count = cur.fetchone()[0]

            # Query 3: Count of American applicants.
            cur.execute(
                "SELECT COUNT(*) FROM applicants WHERE us_or_international = 'American';"
            )
            # us_count = cur.fetchone()[0]

            # Query 4: Count of neither American nor international applicants.
            cur.execute(
                "SELECT COUNT(*) FROM applicants "
                "WHERE us_or_international NOT IN ('International','American');"
            )
            # other_count = cur.fetchone()[0]

            # Query 5: Percentage of international students.
            percent_international = (
                (international_count / total_count * 100) if total_count else 0
            )

            # Query 6: Average GPA, GRE, GRE V, GRE AW.
            cur.execute(
                "SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw) FROM applicants "
                "WHERE gpa IS NOT NULL AND gre IS NOT NULL "
                "AND gre_v IS NOT NULL AND gre_aw IS NOT NULL;"
            )
            avg_metrics = cur.fetchone() or (None, None, None, None)

            # Query 7: Average GPA of American students in Fall 2025.
            cur.execute(
                "SELECT AVG(gpa) FROM applicants WHERE us_or_international = 'American' "
                "AND term = 'Fall 2025' AND gpa IS NOT NULL;"
            )
            avg_gpa_american = cur.fetchone()[0]

            # Query 8 & 9: Acceptance count and percentage for Fall 2025.
            cur.execute("SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2025';")
            fall_2025_total_count = cur.fetchone()[0]

            cur.execute(
                "SELECT COUNT(*) FROM applicants "
                "WHERE term = 'Fall 2025' AND status LIKE 'Accepted%';"
            )
            acceptance_count = cur.fetchone()[0]

            acceptance_percent = (
                (acceptance_count / fall_2025_total_count * 100)
                if fall_2025_total_count
                else 0
            )

            # Query 10: Average GPA of accepted applicants in Fall 2025.
            cur.execute(
                "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2025' "
                "AND status LIKE 'Accepted%' AND gpa IS NOT NULL;"
            )
            avg_gpa_accepted = cur.fetchone()[0]

            # Query 11: JHU Masters Computer Science count.
            cur.execute(
                "SELECT COUNT(*) FROM applicants "
                "WHERE llm_generated_university = 'Johns Hopkins University' "
                "AND degree = 'Masters' AND llm_generated_program = 'Computer Science';"
            )
            jhu_masters_cs_count = cur.fetchone()[0]

            # Query 12: Georgetown University, PhD in Computer Science, 2025 count.
            cur.execute(
                "SELECT COUNT(*) FROM applicants "
                "WHERE llm_generated_university = 'Georgetown University' "
                "AND degree = 'PhD' AND llm_generated_program = 'Computer Science' "
                "AND term LIKE '%2025';"
            )
            gtu_phd_25 = cur.fetchone()[0]

            # Query 13: How many accepted entries from 2023 for UChicago Masters CS.
            cur.execute(
                "SELECT COUNT(*) FROM applicants "
                "WHERE llm_generated_university = 'University of Chicago' "
                "AND degree = 'Masters' AND llm_generated_program = 'Computer Science' "
                "AND term LIKE '%2023' AND status LIKE 'Accepted%';"
            )
            uc_cs_23 = cur.fetchone()[0]

            # Query 14: What is the average admit GPA of PhD admits in Boston University?
            cur.execute(
                "SELECT AVG(gpa) FROM applicants "
                "WHERE llm_generated_university = 'Boston University' "
                "AND degree = 'PhD' AND status LIKE 'Accepted%';")
            bu_phd = cur.fetchone()[0]

            # Populate the context dictionary with the fetched data.
            context = {
                'applicant_count': total_count,
                'percent_international': round(percent_international, 2),
                'avg_gpa': round(avg_metrics[0], 2) if avg_metrics[0] else 'N/A',
                'avg_gre': round(avg_metrics[1], 2) if avg_metrics[1] else 'N/A',
                'avg_gre_v': round(avg_metrics[2], 2) if avg_metrics[2] else 'N/A',
                'avg_gre_aw': round(avg_metrics[3], 2) if avg_metrics[3] else 'N/A',
                'avg_gpa_american': round(avg_gpa_american, 2) if avg_gpa_american else 'N/A',
                'acceptance_percent': round(acceptance_percent, 2),
                'avg_gpa_accepted': round(avg_gpa_accepted, 2) if avg_gpa_accepted else 'N/A',
                'jhu_masters_cs_count': jhu_masters_cs_count,
                'gtu_phd_25': gtu_phd_25,
                'uc_cs_23': uc_cs_23,
                'bu_phd': round(bu_phd, 2) if bu_phd else 'N/A'
            }

        return render_template('index.html', **context)

    finally:
        pool.putconn(conn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
