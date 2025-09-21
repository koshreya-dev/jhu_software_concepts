"""
Flask application providing a web-based interface to interact with the dataset. 
Uses flash messages to inform the user of scraping/analysis progress.
"""

import os
import subprocess
import threading
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg_pool

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for flash messages

# Use a connection pool
pool = psycopg_pool.ConnectionPool(os.environ['DATABASE_URL'])

# Lock for safe concurrent access
scrape_lock = threading.Lock()
SCRAPING_IN_PROGRESS = False

# Run the scraper in a background thread.
def run_scraper():
    global SCRAPING_IN_PROGRESS
    with scrape_lock:
        SCRAPING_IN_PROGRESS = True
    try:
        # Run your update + reload pipeline
        subprocess.run(["python", "module_3/update.py"], check=True)
        subprocess.run(["python", "module_3/reload_data.py"], check=True)
    except Exception as e:
        print("Scraping failed:", e)
    finally:
        with scrape_lock:
            SCRAPING_IN_PROGRESS = False
            
# Handle Pull Data button.
@app.route("/pull", methods=["POST"])
def pull_data():
    global SCRAPING_IN_PROGRESS
    with scrape_lock:
        if SCRAPING_IN_PROGRESS:
            flash("A scrape is already running. Please wait until it finishes.")
            return redirect(url_for("index"))

        # Start background scraper
        thread = threading.Thread(target=run_scraper, daemon=True)
        thread.start()
        flash("Scraping started! This may take a few minutes.")

    return redirect(url_for("index"))

# Handle Update Analysis button.
@app.route("/update", methods=["POST"])
def update_analysis():
    global SCRAPING_IN_PROGRESS
    with scrape_lock:
        if SCRAPING_IN_PROGRESS:
            flash("Cannot update analysis while scraping is in progress.")
            return redirect(url_for("index"))

    # No extra logic needed — just re-render index
    flash("Analysis updated with the latest database results.")
    return redirect(url_for("index"))

# Handles all the queries.
@app.route('/')
def index():
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            # Run all the queries
            
            # Query 1: Count of all students
            cur.execute("SELECT COUNT(*) FROM applicants;")
            total_count = cur.fetchone()[0]

            # Query 2: Count of international students
            cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international = 'International';")
            international_count = cur.fetchone()[0]

            # Query 3: Count of American students
            cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international = 'American';")
            us_count = cur.fetchone()[0]

            # Query 4: Count of neither American nor international students
            cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international NOT IN ('International','American');")
            other_count = cur.fetchone()[0]

            # Query 5: Percentage of international students
            percent_international = (international_count / total_count * 100) if total_count else 0

            # Query 6: Average GPA, GRE, GRE V, GRE AW
            cur.execute("""
                SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw)
                FROM applicants
                WHERE gpa IS NOT NULL AND gre IS NOT NULL AND gre_v IS NOT NULL AND gre_aw IS NOT NULL;
            """)
            avg_metrics = cur.fetchone() or (None, None, None, None)

            # Query 7: Average GPA of American students in Fall 2025
            cur.execute("""
                SELECT AVG(gpa)
                FROM applicants
                WHERE us_or_international = 'American' AND term = 'Fall 2025' AND gpa IS NOT NULL;
            """)
            avg_gpa_american = cur.fetchone()[0]

            # Query 8: Acceptance count for Fall 2025
            cur.execute("""
                SELECT COUNT(*)
                FROM applicants
                WHERE term = 'Fall 2025' AND status LIKE 'Accepted%';
            """)
            acceptance_count = cur.fetchone()[0]

            # Query 9: Acceptance percent for Fall 2025
            cur.execute("""
                SELECT COUNT(*)
                FROM applicants
                WHERE term = 'Fall 2025';
            """)
            fall_2025_total_count = cur.fetchone()[0]

            acceptance_percent = (acceptance_count / fall_2025_total_count * 100) if fall_2025_total_count else 0
           
            # Query 10: Average GPA of accepted applicants in Fall 2025
            cur.execute("""
                SELECT AVG(gpa)
                FROM applicants
                WHERE term = 'Fall 2025' AND status LIKE 'Accepted%' AND gpa IS NOT NULL;
            """)
            avg_gpa_accepted = cur.fetchone()[0]
            
            # Query 11: JHU Masters Computer Science count
            cur.execute("""
                SELECT COUNT(*)
                FROM applicants
                WHERE
                    llm_generated_university = 'Johns Hopkins University'
                    AND degree = 'Masters'
                    AND llm_generated_program = 'Computer Science';
            """)
            jhu_masters_cs_count = cur.fetchone()[0]
            
            # Query 11: Georgetown University, PhD in Computer Science, 2025
            cur.execute("""
                SELECT COUNT(*)
                FROM applicants
                WHERE
                    llm_generated_university = 'Georgetown University'
                    AND degree = 'PhD'
                    AND llm_generated_program = 'Computer Science'
                    AND term like '%2025';
            """)
            gtu_phd_25 = cur.fetchone()[0]
    
            # Query 12: How many entries from 2023 are acceptances from \
                # applicants who applied to University of Chicago for a \
                    # Masters in Computer Science?
            cur.execute("""
                SELECT COUNT(*)
                FROM applicants
                WHERE
                    llm_generated_university = 'University of Chicago'
                    AND degree = 'Masters'
                    AND llm_generated_program = 'Computer Science'
                    AND term like '%2023';
            """)
            uc_cs_23 = cur.fetchone()[0]
    
            # Query 13: What is the average admit GPA of PhD admits in Boston University?
            cur.execute("""
                SELECT AVG(gpa)
                FROM applicants
                WHERE
                    llm_generated_university = 'Boston University'
                    AND degree = 'PhD';
                    """)
            BU_phd = cur.fetchone()[0]

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
            'BU_phd': round(BU_phd, 2) if BU_phd else 'N/A'
        }

        return render_template('index.html', **context)

    finally:
        pool.putconn(conn)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
