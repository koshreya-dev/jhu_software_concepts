# tests/test_db_insert.py
import pytest

class FakePool:
    def __init__(self, initial=None):
        self.data = list(initial or [])
    def insert_rows(self, rows):
        existing = {r.get("url") for r in self.data if r.get("url")}
        for r in rows:
            if r.get("url") not in existing:
                self.data.append(r)
                existing.add(r.get("url"))

@pytest.mark.db
def test_insert_on_pull_and_required_fields(monkeypatch):
    """
    a.i Before: table empty
    a.ii After POST /pull-data new rows exist with required non-null fields
    """
    from module_4.src.front_end.app_factory import create_app

    # start with empty pool
    fake_pool = FakePool(initial=[])
    # scraper will return rows that the loader/insert should write
    scraped = [
        {"url": "https://dbtest/1", "gpa": 3.8, "term": "Fall 2025", "status": "Accepted"}
    ]
    def fake_scraper(): return scraped

    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    # Before: empty
    assert len(fake_pool.data) == 0

    r = client.post("/pull-data")
    assert r.status_code in (200, 202)
    j = r.get_json()
    assert j.get("ok") is True

    # After: row inserted
    assert len(fake_pool.data) >= 1
    row = next((x for x in fake_pool.data if x.get("url") == "https://dbtest/1"), None)
    assert row is not None

    # Required non-null fields exist (example Module-3 fields)
    required = ["url", "gpa", "term", "status"]
    for f in required:
        assert f in row and row[f] is not None

@pytest.mark.db
def test_idempotency_duplicate_pulls_do_not_duplicate(monkeypatch):
    from module_4.src.front_end.app_factory import create_app

    fake_pool = FakePool(initial=[])
    scraped = [{"url": "https://dbtest/dup", "gpa": 3.6, "term": "Fall 2025", "status": "Applied"}]
    def fake_scraper(): return scraped

    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    # First pull
    r1 = client.post("/pull-data")
    assert r1.status_code in (200, 202)
    # Second pull (same data)
    r2 = client.post("/pull-data")
    assert r2.status_code in (200, 202)

    occurrences = [r for r in fake_pool.data if r.get("url") == "https://dbtest/dup"]
    assert len(occurrences) == 1

@pytest.mark.db
def test_simple_query_function_returns_expected_keys():
    """
    Query the rendered analysis page to ensure expected keys exist.
    Adapted to match current template which uses visible text, not data-key attributes.
    """
    from module_4.src.front_end.app_factory import create_app

    fake_pool = FakePool(initial=[{"url": "u1", "us_or_international": "International", "gpa": 3.5, "term": "Fall 2025", "status": "Accepted"}])
    def fake_scraper(): return []

    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    res = client.get("/analysis")
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    # Look for text snippets instead of data-key attributes
    expected_texts = [
        'Applicant count',
        'Percent International',
        'Average GPA',
        'Average GRE',
        'Average GRE V',
        'Average GRE AW',
        'Average GPA American',
        'Acceptance percent',
        'Average GPA Acceptance',
        'JHU for a masters degrees in Computer Science',
        'Georgetown University for a PhD in Computer Science',
        'University of Chicago for a Masters in Computer Science',
        'Boston University for a PhD'
    ]

    for text in expected_texts:
        assert text in html

