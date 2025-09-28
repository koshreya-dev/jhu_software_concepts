"""
Provides SQL queries for analyzing the applicant data.
Contains parameterized queries for filtering by program, degree, status, and date ranges.
Allows exporting query results to JSON or printing directly to the console.
"""
import os
import psycopg_pool

def _fetch_metrics(cur):
    """
    Executes all SQL queries and returns the results in a dictionary.
    """
    metrics = {}

    # Execute all queries
    cur.execute("SELECT COUNT(*) FROM applicants;")
    metrics['total_count'] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international = 'International';")
    metrics['international_count'] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international = 'American';")
    metrics['us_count'] = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE us_or_international NOT IN ('International', 'American');
    """)
    metrics['other_count'] = cur.fetchone()[0]

    cur.execute("""
        SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw)
        FROM applicants
        WHERE gpa IS NOT NULL AND gre IS NOT NULL AND gre_v IS NOT NULL AND gre_aw IS NOT NULL;
    """)
    metrics['avg_metrics'] = cur.fetchone()

    cur.execute("""
        SELECT AVG(gpa) FROM applicants
        WHERE us_or_international = 'American' AND term = 'Fall 2025' AND gpa IS NOT NULL;
    """)
    metrics['avg_gpa_american'] = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term = 'Fall 2025' AND status LIKE 'Accepted%';
    """)
    metrics['acceptance_count'] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2025';")
    fall_2025_total_count = cur.fetchone()[0]
    metrics['fall_2025_total_count'] = fall_2025_total_count
    metrics['acceptance_percent'] = (
        (metrics['acceptance_count'] / fall_2025_total_count) * 100
    ) if fall_2025_total_count > 0 else 0

    cur.execute("""
        SELECT AVG(gpa) FROM applicants
        WHERE term = 'Fall 2025' AND status LIKE 'Accepted%' AND gpa IS NOT NULL;
    """)
    metrics['avg_gpa_accepted'] = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM applicants
        WHERE llm_generated_university = 'Johns Hopkins University'
        AND degree = 'Masters' AND llm_generated_program = 'Computer Science';
    """)
    metrics['jhu_masters_cs_count'] = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM applicants
        WHERE llm_generated_university = 'Georgetown University'
        AND degree = 'PhD' AND llm_generated_program = 'Computer Science'
        AND term LIKE '%2025';
    """)
    metrics['gtu_phd_25'] = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM applicants
        WHERE llm_generated_university = 'University of Chicago'
        AND degree = 'Masters' AND llm_generated_program = 'Computer Science'
        AND term LIKE '%2023';
    """)
    metrics['uc_cs_23'] = cur.fetchone()[0]

    cur.execute("""
        SELECT AVG(gpa) FROM applicants
        WHERE llm_generated_university = 'Boston University' AND degree = 'PhD';
    """)
    metrics['bu_phd'] = cur.fetchone()[0]

    return metrics

def _print_metrics(metrics):
    """
    Prints the collected metrics to the console.
    """
    print(f"Applicant count: {metrics['total_count']}")
    print(f"International count: {metrics['international_count']}")
    print(f"US count: {metrics['us_count']}")
    print(f"Other count: {metrics['other_count']}")
    print(f"Percent International: {metrics['percent_international']:.2f}%")
    avg_metrics = [
        f"Average GPA: {metrics['avg_metrics'][0]}",
        f"Average GRE: {metrics['avg_metrics'][1]}",
        f"Average GRE V: {metrics['avg_metrics'][2]}",
        f"Average GRE AW: {metrics['avg_metrics'][3]}"
    ]
    print(", ".join(avg_metrics))
    print(f"Average GPA American: {metrics['avg_gpa_american']:.2f}")
    print(f"Acceptance count: {metrics['acceptance_count']}")
    print(f"Acceptance percent: {metrics['acceptance_percent']:.2f}%")
    print(f"Average GPA Acceptance: {metrics['avg_gpa_accepted']:.2f}")
    print(f"JHU Masters Computer Science count: {metrics['jhu_masters_cs_count']}")
    print(f"Georgetown PhD 2025 Computer Science count: {metrics['gtu_phd_25']}")
    print(f"UChicago Masters 2023 Computer Science count: {metrics['uc_cs_23']}")
    print(f"Average GPA of PhD at Boston University: {metrics['bu_phd']:.2f}")

def analyze_applicant_data():
    """
    Connects to the database and executes a series of SQL queries
    to analyze applicant data.
    """
    try:
        pool = psycopg_pool.ConnectionPool(os.environ['DATABASE_URL'])
    except KeyError:
        print("Error: DATABASE_URL environment variable is not set.")
        return

    with pool:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                metrics = _fetch_metrics(cur)

    _print_metrics(metrics)

if __name__ == "__main__":
    analyze_applicant_data()
