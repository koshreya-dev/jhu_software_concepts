"""
Flask application providing a web-based interface to interact with the dataset.
It displays various statistics and allows users to trigger a data scraping job.
"""
import os
import subprocess
import threading
from flask import Flask, render_template, redirect, url_for, flash
import psycopg_pool
from module_5.src.sql_utils import (
    build_count_query, build_avg_query,
    build_where_equals, build_where_like,
    build_where_not_in, build_where_and
)
from module_5.src.query_helpers import (
    query_american_fall_2025_gpa,
    query_fall_2025_accepted_count,
    query_fall_2025_accepted_gpa,
    query_university_program_degree,
    query_university_program_degree_term,
    query_avg_all_metrics
)


# pylint: disable=W0603, W0718, W0602, R0914, R0915


# Initialize the Flask application.
app = Flask(__name__)
app.secret_key = ""  # Needed for flash messages.

# Use a connection pool for efficient database connections.
pool = psycopg_pool.ConnectionPool(os.environ['DATABASE_URL'])

# Lock for safe concurrent access to shared resources.
scrape_lock = threading.Lock()
SCRAPING_IN_PROGRESS = False

# Add a query result limit for safety
QUERY_LIMIT = 1000000


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
        flash(
            "Scraping failed: An error occurred during the update process.",
            "danger"
        )
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
            flash(
                "A scrape is already running. Please wait until it finishes.",
                "warning"
            )
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
            flash(
                "Cannot update analysis while scraping is in progress.",
                "warning"
            )
            return redirect(url_for("index"))

    # Re-render the index page with a success message.
    flash("Analysis updated with the latest database results.", "success")
    return redirect(url_for("index"))


@app.route('/')
def index():
    """
    Handles the main index page, displaying analysis from the dataset.

    This function connects to the database, executes several queries to
    fetch analytics, and passes the results to the 'index.html' template
    for rendering.
    """
    conn = pool.getconn()
    context = {}
    try:
        with conn.cursor() as cur:
            # Query 1: Count of all applicants.
            query = build_count_query('applicants', limit=QUERY_LIMIT)
            cur.execute(query)
            total_count = cur.fetchone()[0]

            # Query 2: Count of international applicants.
            where_clause, params = build_where_equals(
                'us_or_international', 'International'
            )
            query = build_count_query(
                'applicants', where_clause, limit=QUERY_LIMIT
            )
            cur.execute(query, params)
            international_count = cur.fetchone()[0]

            # Query 3: Count of American applicants.
            where_clause, params = build_where_equals(
                'us_or_international', 'American'
            )
            query = build_count_query(
                'applicants', where_clause, limit=QUERY_LIMIT
            )
            cur.execute(query, params)

            # Query 4: Count of neither American nor international.
            where_clause, params = build_where_not_in(
                'us_or_international', ['International', 'American']
            )
            query = build_count_query(
                'applicants', where_clause, limit=QUERY_LIMIT
            )
            cur.execute(query, params)

            # Query 5: Percentage of international students.
            if total_count:
                percent_international = (
                    international_count / total_count * 100
                )
            else:
                percent_international = 0

            # Query 6: Average GPA, GRE, GRE V, GRE AW.
            avg_metrics = query_avg_all_metrics(cur, QUERY_LIMIT)

            # Query 7: Average GPA of American students in Fall 2025.
            avg_gpa_american = query_american_fall_2025_gpa(
                cur, QUERY_LIMIT
            )

            # Query 8: Fall 2025 total count
            where_clause, params = build_where_equals('term', 'Fall 2025')
            query = build_count_query(
                'applicants', where_clause, limit=QUERY_LIMIT
            )
            cur.execute(query, params)
            fall_2025_total_count = cur.fetchone()[0]

            # Query 9: Acceptance count for Fall 2025.
            acceptance_count = query_fall_2025_accepted_count(
                cur, QUERY_LIMIT
            )

            if fall_2025_total_count:
                acceptance_percent = (
                    acceptance_count / fall_2025_total_count * 100
                )
            else:
                acceptance_percent = 0

            # Query 10: Average GPA of accepted applicants in Fall 2025.
            avg_gpa_accepted = query_fall_2025_accepted_gpa(
                cur, QUERY_LIMIT
            )

            # Query 11: JHU Masters Computer Science count.
            jhu_masters_cs_count = query_university_program_degree(
                cur, 'Johns Hopkins University', 'Masters',
                'Computer Science', QUERY_LIMIT
            )

            # Query 12: Georgetown University, PhD in CS, 2025 count.
            gtu_phd_25 = query_university_program_degree_term(
                cur, 'Georgetown University', 'PhD',
                'Computer Science', '%2025', QUERY_LIMIT
            )

            # Query 13: UChicago Masters CS 2023 accepted count.
            clause1, params1 = build_where_equals(
                'llm_generated_university', 'University of Chicago'
            )
            clause2, params2 = build_where_equals('degree', 'Masters')
            clause3, params3 = build_where_equals(
                'llm_generated_program', 'Computer Science'
            )
            clause4, params4 = build_where_like('term', '%2023')
            clause5, params5 = build_where_like('status', 'Accepted%')
            where_clause, params = build_where_and([
                (clause1, params1), (clause2, params2),
                (clause3, params3), (clause4, params4), (clause5, params5)
            ])
            query = build_count_query(
                'applicants', where_clause, limit=QUERY_LIMIT
            )
            cur.execute(query, params)
            uc_cs_23 = cur.fetchone()[0]

            # Query 14: Average admit GPA of PhD at Boston University.
            clause1, params1 = build_where_equals(
                'llm_generated_university', 'Boston University'
            )
            clause2, params2 = build_where_equals('degree', 'PhD')
            clause3, params3 = build_where_like('status', 'Accepted%')
            where_clause, params = build_where_and([
                (clause1, params1), (clause2, params2), (clause3, params3)
            ])
            query = build_avg_query(
                'applicants', ['gpa'], where_clause, limit=QUERY_LIMIT
            )
            cur.execute(query, params)
            bu_phd = cur.fetchone()[0]

            # Populate the context dictionary with the fetched data.
            context = {
                'applicant_count': total_count,
                'percent_international': round(percent_international, 2),
                'avg_gpa': (
                    round(avg_metrics[0], 2) if avg_metrics[0] else 'N/A'
                ),
                'avg_gre': (
                    round(avg_metrics[1], 2) if avg_metrics[1] else 'N/A'
                ),
                'avg_gre_v': (
                    round(avg_metrics[2], 2) if avg_metrics[2] else 'N/A'
                ),
                'avg_gre_aw': (
                    round(avg_metrics[3], 2) if avg_metrics[3] else 'N/A'
                ),
                'avg_gpa_american': (
                    round(avg_gpa_american, 2)
                    if avg_gpa_american else 'N/A'
                ),
                'acceptance_percent': round(acceptance_percent, 2),
                'avg_gpa_accepted': (
                    round(avg_gpa_accepted, 2)
                    if avg_gpa_accepted else 'N/A'
                ),
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
