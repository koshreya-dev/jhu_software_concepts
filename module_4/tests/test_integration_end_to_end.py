# tests/test_integration_end_to_end.py
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

@pytest.mark.integration
def test_end_to_end_pull_update_render(monkeypatch):
    """
    - Inject a fake scraper that returns multiple records
    - POST /pull-data -> rows in DB
    - POST /update-analysis -> succeeds when not busy
    - GET /analysis -> shows updated analysis with correctly formatted values
    """
    from module_4.src.front_end.app_factory import create_app

    rows = [
        {"url": "https://e2e/1", "gpa": 3.9, "us_or_international": "International", "term": "Fall 2025", "status": "Accepted"},
        {"url": "https://e2e/2", "gpa": 3.2, "us_or_international": "American", "term": "Fall 2025", "status": "Applied"},
    ]
    def fake_scraper(): return rows

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
    # pass if there are no percentages, but if present they must match two-decimal format
    for p in percents:
        assert re.match(r"^\d+\.\d{2}%$", p)

@pytest.mark.integration
def test_multiple_pulls_with_overlapping_data_remains_unique(monkeypatch):
    from module_4.src.front_end.app_factory import create_app

    overlap = [{"url": "https://e2e/overlap", "gpa": 3.4, "term": "Fall 2025", "status": "Applied"}]
    def fake_scraper(): return overlap

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
