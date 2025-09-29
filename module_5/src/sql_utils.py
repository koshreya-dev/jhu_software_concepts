"""
Shared SQL utility functions for safe query composition.
Provides helpers to build parameterized queries using psycopg.sql.
"""
from psycopg import sql


def build_count_query(table_name, where_clause=None, limit=None):
    """
    Builds a COUNT(*) query with optional WHERE clause and LIMIT.

    Args:
        table_name: Name of the table to query
        where_clause: Optional SQL composable for WHERE condition
        limit: Optional integer limit for the query

    Returns:
        A composed SQL query object
    """
    query = sql.SQL("SELECT COUNT(*) FROM {table}").format(
        table=sql.Identifier(table_name)
    )

    if where_clause:
        query = sql.SQL("{base} WHERE {condition}").format(
            base=query,
            condition=where_clause
        )

    if limit:
        query = sql.SQL("{base} LIMIT {limit}").format(
            base=query,
            limit=sql.Literal(limit)
        )

    return query


def build_avg_query(table_name, columns, where_clause=None, limit=None):
    """
    Builds an AVG() query for multiple columns with optional WHERE and LIMIT.

    Args:
        table_name: Name of the table to query
        columns: List of column names to average
        where_clause: Optional SQL composable for WHERE condition
        limit: Optional integer limit for the query

    Returns:
        A composed SQL query object
    """
    avg_fields = sql.SQL(', ').join(
        sql.SQL("AVG({col})").format(col=sql.Identifier(col))
        for col in columns
    )

    query = sql.SQL("SELECT {fields} FROM {table}").format(
        fields=avg_fields,
        table=sql.Identifier(table_name)
    )

    if where_clause:
        query = sql.SQL("{base} WHERE {condition}").format(
            base=query,
            condition=where_clause
        )

    if limit:
        query = sql.SQL("{base} LIMIT {limit}").format(
            base=query,
            limit=sql.Literal(limit)
        )

    return query


def build_insert_query(table_name, columns):
    """
    Builds an INSERT query with placeholders for the given columns.

    Args:
        table_name: Name of the table to insert into
        columns: List of column names

    Returns:
        A composed SQL query object
    """
    return sql.SQL("INSERT INTO {table} ({fields}) VALUES ({placeholders})").format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
        placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
    )


def build_where_equals(column, value):
    """
    Builds a WHERE clause for column = value.

    Args:
        column: Column name
        value: Value to compare (will be parameterized)

    Returns:
        A tuple of (SQL composable, list of parameters)
    """
    clause = sql.SQL("{col} = %s").format(col=sql.Identifier(column))
    return clause, [value]


def build_where_like(column, pattern):
    """
    Builds a WHERE clause for column LIKE pattern.

    Args:
        column: Column name
        pattern: Pattern to match (will be parameterized)

    Returns:
        A tuple of (SQL composable, list of parameters)
    """
    clause = sql.SQL("{col} LIKE %s").format(col=sql.Identifier(column))
    return clause, [pattern]


def build_where_in(column, values):
    """
    Builds a WHERE clause for column IN (values).

    Args:
        column: Column name
        values: List of values (will be parameterized)

    Returns:
        A tuple of (SQL composable, list of parameters)
    """
    placeholders = sql.SQL(', ').join(sql.Placeholder() * len(values))
    clause = sql.SQL("{col} IN ({vals})").format(
        col=sql.Identifier(column),
        vals=placeholders
    )
    return clause, values


def build_where_not_in(column, values):
    """
    Builds a WHERE clause for column NOT IN (values).

    Args:
        column: Column name
        values: List of values (will be parameterized)

    Returns:
        A tuple of (SQL composable, list of parameters)
    """
    placeholders = sql.SQL(', ').join(sql.Placeholder() * len(values))
    clause = sql.SQL("{col} NOT IN ({vals})").format(
        col=sql.Identifier(column),
        vals=placeholders
    )
    return clause, values


def build_where_and(clauses_with_params):
    """
    Combines multiple WHERE clauses with AND.

    Args:
        clauses_with_params: List of tuples (SQL composable, parameters list)

    Returns:
        A tuple of (combined SQL composable, flattened parameters list)
    """
    clauses = [c[0] for c in clauses_with_params]
    params = [p for c in clauses_with_params for p in c[1]]

    combined = sql.SQL(' AND ').join(clauses)
    return combined, params
