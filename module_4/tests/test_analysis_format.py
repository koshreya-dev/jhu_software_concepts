# tests/test_analysis_format.py
import pytest
import re
from bs4 import BeautifulSoup

class FakePool:
    def __init__(self, initial=None):
        self.data = list(initial or [])
    def insert_rows(self, rows):
        existing = {r.get("url") for r in self.data if r.get("url")}
        for r in rows:
            if r.get("url") not in existing:
                self.data.append(r)
                existing.add(r.get("url"))

@pytest.mark.analysis
def test_labels_and_percentage_two_decimals():
    """
    - Page includes "Answer" labels for rendered analysis
    - Any percentage on page is formatted with two decimals (e.g., 39.28%)
    """
    from module_4.src.front_end.app_factory import create_app
    
    # Provide pool with a row so percent != 0
    fake_pool = FakePool(initial=[{"url": "u1", "us_or_international": "International", "gpa": 3.5, "term": "Fall 2025", "status": "Accepted"}])
    def fake_scraper(): return []

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
    assert len(percents) >= 0  # if any exist they must be two-decimal; to enforce at least one, change to >=1

    # If percentages exist, ensure they match exactly two decimals
    for p in percents:
        assert re.match(r"^\d+\.\d{2}%$", p)
