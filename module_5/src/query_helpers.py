"""
Helper functions to reduce code duplication in query operations.
Provides common query patterns used across multiple modules.
"""
from psycopg import sql
from .sql_utils import (
    build_count_query, build_avg_query,
    build_where_equals, build_where_like, build_where_and
)

# pylint: disable= R0913, R0917

def build_not_null_where_clause(columns):
    """
    Builds a WHERE clause checking that all columns are NOT NULL.

    Args:
        columns: List of column names to check

    Returns:
        SQL composable for WHERE clause
    """
    clauses = [
        sql.SQL("{col} IS NOT NULL").format(col=sql.Identifier(col))
        for col in columns
    ]
    return sql.SQL(" AND ").join(clauses)


def query_avg_gpa_with_conditions(cur, conditions, limit):
    """
    Queries average GPA with given conditions.

    Args:
        cur: Database cursor
        conditions: List of (clause, params) tuples
        limit: Query limit

    Returns:
        Average GPA value or None
    """
    gpa_null_clause = sql.SQL("{col} IS NOT NULL").format(
        col=sql.Identifier('gpa')
    )
    all_conditions = conditions + [(gpa_null_clause, [])]
    where_clause, params = build_where_and(all_conditions)
    query = build_avg_query('applicants', ['gpa'], where_clause, limit=limit)
    cur.execute(query, params)
    return cur.fetchone()[0]


def query_count_with_conditions(cur, conditions, limit):
    """
    Queries count with given conditions.

    Args:
        cur: Database cursor
        conditions: List of (clause, params) tuples
        limit: Query limit

    Returns:
        Count value
    """
    where_clause, params = build_where_and(conditions)
    query = build_count_query('applicants', where_clause, limit=limit)
    cur.execute(query, params)
    return cur.fetchone()[0]


def query_university_program_degree(cur, university, degree, program, limit):
    """
    Queries count for specific university, degree, and program.

    Args:
        cur: Database cursor
        university: University name
        degree: Degree type
        program: Program name
        limit: Query limit

    Returns:
        Count value
    """
    conditions = [
        build_where_equals('llm_generated_university', university),
        build_where_equals('degree', degree),
        build_where_equals('llm_generated_program', program)
    ]
    return query_count_with_conditions(cur, conditions, limit)


def query_university_program_degree_term(
    cur, university, degree, program, term_pattern, limit
):
    """
    Queries count for university, degree, program, and term pattern.

    Args:
        cur: Database cursor
        university: University name
        degree: Degree type
        program: Program name
        term_pattern: Term pattern for LIKE clause
        limit: Query limit

    Returns:
        Count value
    """
    conditions = [
        build_where_equals('llm_generated_university', university),
        build_where_equals('degree', degree),
        build_where_equals('llm_generated_program', program),
        build_where_like('term', term_pattern)
    ]
    return query_count_with_conditions(cur, conditions, limit)


def query_fall_2025_accepted_gpa(cur, limit):
    """
    Queries average GPA of accepted applicants in Fall 2025.

    Args:
        cur: Database cursor
        limit: Query limit

    Returns:
        Average GPA value or None
    """
    conditions = [
        build_where_equals('term', 'Fall 2025'),
        build_where_like('status', 'Accepted%')
    ]
    return query_avg_gpa_with_conditions(cur, conditions, limit)


def query_american_fall_2025_gpa(cur, limit):
    """
    Queries average GPA of American students in Fall 2025.

    Args:
        cur: Database cursor
        limit: Query limit

    Returns:
        Average GPA value or None
    """
    conditions = [
        build_where_equals('us_or_international', 'American'),
        build_where_equals('term', 'Fall 2025')
    ]
    return query_avg_gpa_with_conditions(cur, conditions, limit)


def query_fall_2025_accepted_count(cur, limit):
    """
    Queries count of accepted applicants in Fall 2025.

    Args:
        cur: Database cursor
        limit: Query limit

    Returns:
        Count value
    """
    conditions = [
        build_where_equals('term', 'Fall 2025'),
        build_where_like('status', 'Accepted%')
    ]
    return query_count_with_conditions(cur, conditions, limit)

def query_avg_all_metrics(cur, limit):
    """
    Queries average GPA, GRE, GRE V, and GRE AW with NOT NULL checks.

    Args:
        cur: Database cursor
        limit: Query limit

    Returns:
        Tuple of (avg_gpa, avg_gre, avg_gre_v, avg_gre_aw)
    """
    where_clause = build_not_null_where_clause(
        ['gpa', 'gre', 'gre_v', 'gre_aw']
    )
    query = build_avg_query(
        'applicants',
        ['gpa', 'gre', 'gre_v', 'gre_aw'],
        where_clause,
        limit=limit
    )
    cur.execute(query)
    return cur.fetchone()
