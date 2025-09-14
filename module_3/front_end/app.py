import os
from flask import Flask, render_template
import psycopg_pool

app = Flask(__name__)

# Use a connection pool
pool = psycopg_pool.ConnectionPool(os.environ['DATABASE_URL'])

@app.route('/')
def index():
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            # Run all the queries (based on query_Data.py)

            cur.execute("SELECT COUNT(*) FROM applicants;")
            total_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international = 'International';")
            international_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international = 'American';")
            us_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international != 'International' AND us_or_international != 'American';")
            other_count = cur.fetchone()[0]

            percent_international = (international_count / total_count * 100) if total_count else 0

            cur.execute("""
                SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw)
                FROM applicants
                WHERE gpa IS NOT NULL AND gre IS NOT NULL AND gre_v IS NOT NULL AND gre_aw IS NOT NULL;
            """)
            avg_metrics = cur.fetchone()

            cur.execute("""
                SELECT AVG(gpa)
                FROM applicants
                WHERE us_or_international = 'American' AND term = 'Fall 2025' AND gpa IS NOT NULL;
            """)
            avg_gpa_american = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM applicants
                WHERE term = 'Fall 2025' AND status LIKE 'Accepted%';
            """)
            acceptance_count = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM applicants
                WHERE term = 'Fall 2025';
            """)
            fall_2025_total_count = cur.fetchone()[0]

            acceptance_percent = (acceptance_count / fall_2025_total_count * 100) if fall_2025_total_count else 0

            cur.execute("""
                SELECT AVG(gpa)
                FROM applicants
                WHERE term = 'Fall 2025' AND status LIKE 'Accepted%' AND gpa IS NOT NULL;
            """)
            avg_gpa_accepted = cur.fetchone()[0]

        # Prepare context data
        context = {
            'applicant_count': total_count,
            'percent_international': round(percent_international, 2),
            'avg_gpa': round(avg_metrics[0], 2),
            'avg_gre': round(avg_metrics[1], 2),
            'avg_gre_v': round(avg_metrics[2], 2),
            'avg_gre_aw': round(avg_metrics[3], 2),
            'avg_gpa_american': round(avg_gpa_american, 2) if avg_gpa_american else 'N/A',
            'acceptance_percent': round(acceptance_percent, 2),
            'avg_gpa_accepted': round(avg_gpa_accepted, 2) if avg_gpa_accepted else 'N/A'
        }

        return render_template('index.html', **context)

    finally:
        pool.putconn(conn)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)