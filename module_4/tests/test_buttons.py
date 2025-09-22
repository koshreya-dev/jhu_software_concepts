import pytest

# Shared FakePool for all button tests
class FakePool:
    def __init__(self, initial=None):
        self.data = list(initial or [])

    def insert_rows(self, rows):
        existing = {r.get("url") for r in self.data if r.get("url")}
        for r in rows:
            if r.get("url") not in existing:
                self.data.append(r)
                existing.add(r.get("url"))

@pytest.mark.buttons
def test_post_pull_data_triggers_loader_and_returns_200(monkeypatch):
    """
    POST /pull-data
    - Returns 200 or 202
    - Triggers loader (fake scraper provides rows; loader inserts into fake pool)
    """
    from module_4.src.front_end.app_factory import create_app
    
    scraped = [{"url": "https://test/1", "gpa": 3.7, "term": "Fall 2025", "status": "Accepted"}]
    called = {"scraper": False}

    def fake_scraper():
        called["scraper"] = True
        return scraped

    fake_pool = FakePool()

    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    res = client.post("/pull-data")
    assert res.status_code in (200, 202)

    j = res.get_json()
    assert isinstance(j, dict)
    assert j.get("ok") is True

    # Loader/scraper should have run and rows inserted into fake_pool
    assert called["scraper"] is True
    assert any(r["url"] == "https://test/1" for r in fake_pool.data)

@pytest.mark.buttons
def test_post_update_analysis_returns_200_when_not_busy():
    """
    POST /update-analysis returns 200 when not busy
    """
    from module_4.src.front_end.app_factory import create_app

    fake_pool = FakePool()
    def fake_scraper(): return []

    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    # Ensure app not busy
    if hasattr(app, "SCRAPING_IN_PROGRESS"):
        app.SCRAPING_IN_PROGRESS = False

    res = client.post("/update-analysis")
    assert res.status_code == 200

@pytest.mark.buttons
def test_busy_gating_update_and_pull_return_409(monkeypatch):
    """
    When a pull is in progress:
    - POST /update-analysis returns 409 {"busy": True} and performs no update
    - POST /pull-data returns 409 {"busy": True}
    """
    from module_4.src.front_end.app_factory import create_app

    fake_pool = FakePool()
    def fake_scraper(): return []

    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    # Simulate busy
    app.SCRAPING_IN_PROGRESS = True

    r1 = client.post("/update-analysis")
    assert r1.status_code == 409
    assert r1.get_json() == {"busy": True}

    r2 = client.post("/pull-data")
    assert r2.status_code == 409
    assert r2.get_json() == {"busy": True}

    # Reset busy flag
    app.SCRAPING_IN_PROGRESS = False

@pytest.mark.buttons
def test_pull_data_scraper_failure(monkeypatch):
    """
    Negative-path test: simulate scraper failure.
    - Verify scraper raises
    - FakePool remains empty
    """
    from module_4.src.front_end.app_factory import create_app

    fake_pool = FakePool()

    def failing_scraper():
        raise RuntimeError("Scraper failed!")

    app = create_app(pool=fake_pool, scraper=failing_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    # Expect scraper to raise
    with pytest.raises(RuntimeError, match="Scraper failed!"):
        client.post("/pull-data")

    # Database should remain empty
    assert len(fake_pool.data) == 0