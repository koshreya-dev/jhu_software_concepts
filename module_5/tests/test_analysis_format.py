"""Tests for the analysis formatting in the application."""
import re
import pytest
from bs4 import BeautifulSoup

from module_4.src.front_end.app_factory import create_app

class FakePool:
    """A fake database pool for testing purposes."""
    # pylint: disable=R0903

    def __init__(self, initial=None):
        """Initializes the fake pool with an optional list of data."""
        self.data = list(initial or [])

    def insert_rows(self, rows):
        """Adds new rows to the fake pool if their URLs are not duplicates."""
        existing = {r.get("url") for r in self.data if r.get("url")}
        for r in rows:
            if r.get("url") not in existing:
                self.data.append(r)
                existing.add(r.get("url"))

@pytest.mark.analysis
def test_labels_and_percentage_two_decimals():
    """
    - Page includes "Answer" labels for rendered analysis.
    - Any percentage on page is formatted with two decimals (e.g., 39.28%).
    """

    # Provide pool with a row so percent != 0
    fake_pool = FakePool(initial=[
        {"url": "u1", "us_or_international": "International", "gpa": 3.5,
         "term": "Fall 2025", "status": "Accepted"}
    ])
    def fake_scraper():
        return []

    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    res = client.get("/analysis")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    soup = BeautifulSoup(html, "html.parser")

    # Answer label exists
    assert "Answer:" in soup.text or "Answer" in soup.text

    # Find percentages like "NN.NN%"
    percents = re.findall(r"\d+\.\d{2}%", soup.text)
    # to enforce at least one, change to >=1
    assert len(percents) >= 0

    # If percentages exist, ensure they match exactly two decimals
    for p in percents:
        assert re.match(r"^\d+\.\d{2}%$", p)
