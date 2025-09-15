"""
Provides SQL queries for analyzing the applicant data. 
Contains parameterized queries for filtering by program, degree, status, and date ranges. 
Allows exporting query results to JSON or printing directly to the console.
"""


import os
import psycopg
import psycopg_pool

#Set up connection with psycopg connection pool
pool = psycopg_pool.ConnectionPool(os.environ['DATABASE_URL'])

#Get a connection from the pool.
conn = pool.getconn()

with conn.cursor() as cur:

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
    cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international != 'International' AND us_or_international != 'American';")
    other_count = cur.fetchone()[0]

    # Query 5: Percentage of international students
    if total_count > 0:
        percent_international = (international_count / total_count) * 100
    else:
        percent_international = 0

    # Query 6: Average GPA, GRE, GRE V, GRE AW
    cur.execute("""
        SELECT
            AVG(gpa),
            AVG(gre),
            AVG(gre_v),
            AVG(gre_aw)
        FROM applicants
        WHERE gpa IS NOT NULL AND gre IS NOT NULL AND gre_v IS NOT NULL AND gre_aw IS NOT NULL;
    """)
    avg_metrics = cur.fetchone()

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
    if fall_2025_total_count > 0:
        acceptance_percent = (acceptance_count / fall_2025_total_count) * 100
    else:
        acceptance_percent = 0

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

    # --- Terminal Output ---
    print(f"Applicant count: {total_count}")
    print(f"International count: {international_count}")
    print(f"US count: {us_count}")
    print(f"Other count: {other_count}")
    print(f"Percent International: {percent_international}%")
    print(f"Average GPA: {avg_metrics[0]}, Average GRE: {avg_metrics[1]}, Average GRE V: {avg_metrics[2]}, Average GRE AW: {avg_metrics[3]}")
    print(f"Average GPA American: {avg_gpa_american}")
    print(f"Acceptance count: {acceptance_count}")
    print(f"Acceptance percent: {acceptance_percent}%")
    print(f"Average GPA Acceptance: {avg_gpa_accepted}")
    print(f"JHU Masters Computer Science count: {jhu_masters_cs_count}")
    print(f"Georgetown PhD 2025 Computer Science count: {gtu_phd_25}")
    print(f"UChicago Masters 2023 Computer Science count: {uc_cs_23}")
    print(f"Average GPA of PhD Acceptance at Boston University: {BU_phd}")


#   # Calculate the average GPA needed for each course
#   cur.execute("""
#     SELECT AVG(c.gpa) 
#     FROM courses c;""")

#   print("Average GPA for each course: ", cur.fetchall())

