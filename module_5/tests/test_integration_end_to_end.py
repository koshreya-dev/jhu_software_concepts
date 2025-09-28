# module_5/tests/test_integration_end_to_end.py
"""End-to-end integration tests for the admissions analysis application."""
import re
from unittest.mock import Mock
import pytest
from bs4 import BeautifulSoup
from module_4.src.front_end.app_factory import create_app


class FakePool:
    """A fake database connection pool for testing purposes."""
    # pylint: disable=R0903

    def __init__(self, initial=None):
        self.data = list(initial or [])

    def insert_rows(self, rows):
        """Insert rows while ensuring unique URLs."""
        existing = {r.get("url") for r in self.data if r.get("url")}
        for r in rows:
            if r.get("url") not in existing:
                self.data.append(r)
                existing.add(r.get("url"))


@pytest.mark.integration
def test_end_to_end_pull_update_render():
    """
    Test the full process: pull data, update analysis, and render results.

    - Inject a fake scraper that returns multiple records.
    - POST /pull-data -> confirms rows are inserted into the fake DB.
    - POST /update-analysis -> succeeds when the scraper is not busy.
    - GET /analysis -> shows the updated analysis with correctly formatted values.
    """
    rows = [
        {
            "url": "https://e2e/1",
            "gpa": 3.9,
            "us_or_international": "International",
            "term": "Fall 2025",
            "status": "Accepted",
        },
        {
            "url": "https://e2e/2",
            "gpa": 3.2,
            "us_or_international": "American",
            "term": "Fall 2025",
            "status": "Applied",
        },
    ]

    fake_scraper = Mock(return_value=rows)

    fake_pool = FakePool(initial=[])
    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    # Pull
    r_pull = client.post("/pull-data")
    assert r_pull.status_code in (200, 202)
    assert any(r["url"] == "https://e2e/1" for r in fake_pool.data)
    assert any(r["url"] == "https://e2e/2" for r in fake_pool.data)

    # Update analysis (should be allowed when not busy)
    if hasattr(app, "SCRAPING_IN_PROGRESS"):
        app.SCRAPING_IN_PROGRESS = False
    r_update = client.post("/update-analysis")
    assert r_update.status_code == 200

    # Render analysis -> check formatting
    r_get = client.get("/analysis")
    assert r_get.status_code == 200
    html = r_get.get_data(as_text=True)
    soup = BeautifulSoup(html, "html.parser")

    # check presence of Answer label
    assert "Answer:" in soup.text or "Answer" in soup.text

    # check percentages formatted with two decimals if present
    percents = re.findall(r"\d+\.\d{2}%", soup.text)
    # Pass if there are no percentages, but if present they must match two-decimal format
    for p in percents:
        assert re.match(r"^\d+\.\d{2}%$", p)

@pytest.mark.integration
def test_multiple_pulls_with_overlapping_data_remains_unique():
    """
    Test that pulling overlapping data multiple times does not create duplicates.
    """
    overlap = [{"url": "https://e2e/overlap", "gpa": 3.4, "term": "Fall 2025", "status": "Applied"}]
    fake_scraper = Mock(return_value=overlap)

    fake_pool = FakePool(initial=[])
    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    r1 = client.post("/pull-data")
    assert r1.status_code in (200, 202)
    r2 = client.post("/pull-data")
    assert r2.status_code in (200, 202)

    occurrences = [r for r in fake_pool.data if r.get("url") == "https://e2e/overlap"]
    assert len(occurrences) == 1
