"""
Provides SQL queries for analyzing the applicant data.
Contains parameterized queries for filtering by program, degree, status,
and date ranges. Allows exporting query results to JSON or printing
directly to the console.
"""
import os
import psycopg_pool
from psycopg import sql
from .sql_utils import (
    build_count_query, build_avg_query,
    build_where_equals, build_where_not_in
)
from .query_helpers import (
    query_american_fall_2025_gpa,
    query_fall_2025_accepted_count,
    query_fall_2025_accepted_gpa,
    query_university_program_degree,
    query_university_program_degree_term,
    query_avg_all_metrics
)

# Add a query result limit for safety
QUERY_LIMIT = 1000000


def _fetch_metrics(cur):
    """
    Executes all SQL queries and returns the results in a dictionary.
    """
    metrics = {}

    # Query 1: Total count
    query = build_count_query('applicants', limit=QUERY_LIMIT)
    cur.execute(query)
    metrics['total_count'] = cur.fetchone()[0]

    # Query 2: International count
    where_clause, params = build_where_equals(
        'us_or_international', 'International'
    )
    query = build_count_query('applicants', where_clause, limit=QUERY_LIMIT)
    cur.execute(query, params)
    metrics['international_count'] = cur.fetchone()[0]

    # Query 3: US count
    where_clause, params = build_where_equals(
        'us_or_international', 'American'
    )
    query = build_count_query('applicants', where_clause, limit=QUERY_LIMIT)
    cur.execute(query, params)
    metrics['us_count'] = cur.fetchone()[0]

    # Query 4: Other count
    where_clause, params = build_where_not_in(
        'us_or_international', ['International', 'American']
    )
    query = build_count_query('applicants', where_clause, limit=QUERY_LIMIT)
    cur.execute(query, params)
    metrics['other_count'] = cur.fetchone()[0]

    # Calculate percent international
    if metrics['total_count'] > 0:
        metrics['percent_international'] = (
            (metrics['international_count'] / metrics['total_count']) * 100
        )
    else:
        metrics['percent_international'] = 0

    # Query 5: Average metrics
    metrics['avg_metrics'] = query_avg_all_metrics(cur, QUERY_LIMIT)

    # Query 6: Average GPA American
    metrics['avg_gpa_american'] = query_american_fall_2025_gpa(
        cur, QUERY_LIMIT
    )

    # Query 7: Acceptance count
    metrics['acceptance_count'] = query_fall_2025_accepted_count(
        cur, QUERY_LIMIT
    )

    # Query 8: Fall 2025 total count
    where_clause, params = build_where_equals('term', 'Fall 2025')
    query = build_count_query('applicants', where_clause, limit=QUERY_LIMIT)
    cur.execute(query, params)
    fall_2025_total_count = cur.fetchone()[0]
    metrics['fall_2025_total_count'] = fall_2025_total_count
    if fall_2025_total_count > 0:
        metrics['acceptance_percent'] = (
            (metrics['acceptance_count'] / fall_2025_total_count) * 100
        )
    else:
        metrics['acceptance_percent'] = 0

    # Query 9: Average GPA accepted
    metrics['avg_gpa_accepted'] = query_fall_2025_accepted_gpa(
        cur, QUERY_LIMIT
    )

    # Query 10: JHU Masters CS count
    metrics['jhu_masters_cs_count'] = query_university_program_degree(
        cur, 'Johns Hopkins University', 'Masters',
        'Computer Science', QUERY_LIMIT
    )

    # Query 11: Georgetown PhD 2025
    metrics['gtu_phd_25'] = query_university_program_degree_term(
        cur, 'Georgetown University', 'PhD',
        'Computer Science', '%2025', QUERY_LIMIT
    )

    # Query 12: UChicago Masters 2023
    metrics['uc_cs_23'] = query_university_program_degree_term(
        cur, 'University of Chicago', 'Masters',
        'Computer Science', '%2023', QUERY_LIMIT
    )

    # Query 13: Boston University PhD average GPA
    where_clause, params = build_where_equals(
        'llm_generated_university', 'Boston University'
    )
    where_clause2, params2 = build_where_equals('degree', 'PhD')
    combined_clause = sql.SQL("{c1} AND {c2}").format(
        c1=where_clause, c2=where_clause2
    )
    combined_params = params + params2
    query = build_avg_query(
        'applicants', ['gpa'], combined_clause, limit=QUERY_LIMIT
    )
    cur.execute(query, combined_params)
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
    pct_int = metrics['percent_international']
    print(f"Percent International: {pct_int:.2f}%")
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
    print(
        f"JHU Masters Computer Science count: "
        f"{metrics['jhu_masters_cs_count']}"
    )
    print(
        f"Georgetown PhD 2025 Computer Science count: "
        f"{metrics['gtu_phd_25']}"
    )
    print(
        f"UChicago Masters 2023 Computer Science count: "
        f"{metrics['uc_cs_23']}"
    )
    print(
        f"Average GPA of PhD at Boston University: "
        f"{metrics['bu_phd']:.2f}"
    )


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
