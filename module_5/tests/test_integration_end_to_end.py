"""Integration tests simulating end-to-end scraping and database behavior."""

import pytest
from module_5.tests.conftest import assert_valid_analysis

@pytest.mark.integration
def test_end_to_end_analysis_percentages(populated_client):
    """
    Ensure analysis shows valid percentages after data insertion.
    Uses a pre-populated fake pool via the populated_client fixture.
    """
    client = populated_client

    # Simulate adding one more row
    def fake_scraper():
        return [{"url": "u2", "us_or_international": "US",
                 "gpa": 3.9, "term": "Spring 2026", "status": "Rejected"}]

    # Replace app scraper temporarily
    client.application.scraper = fake_scraper

    # Call /analysis to render percentages
    res = client.get("/analysis")
    assert res.status_code == 200

    # Use shared helper to validate analysis content
    assert_valid_analysis(res)


@pytest.mark.integration
def test_double_insert(populated_client):
    """Ensure posting /pull-data twice inserts only two rows."""
    client, pool = populated_client

    client.post("/pull-data")
    client.post("/pull-data")

    # Only two unique URLs should exist in the fake pool
    assert len(pool.data) == 2
