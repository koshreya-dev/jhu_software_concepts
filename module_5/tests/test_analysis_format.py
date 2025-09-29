"""Tests for the analysis formatting in the application."""

import pytest
from .conftest import assert_valid_analysis

@pytest.mark.analysis
def test_labels_and_percentage_two_decimals(flask_test_client, fake_pool_fixture):
    """
    - Page includes "Answer" labels for rendered analysis.
    - Any percentage on page is formatted with two decimals (e.g., 39.28%).
    """
    # Preload fake pool with a row so percentages are non-zero
    fake_pool_fixture.insert_rows([
        {"url": "u1", "us_or_international": "International", "gpa": 3.5,
         "term": "Fall 2025", "status": "Accepted"}
    ])

    res = flask_test_client.get("/analysis")
    assert res.status_code == 200

    # Use shared helper to validate analysis content
    assert_valid_analysis(res)
