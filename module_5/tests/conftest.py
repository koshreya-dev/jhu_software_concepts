"""Shared test fixtures and utilities for module_5 tests."""

from contextlib import contextmanager
import re
import pytest
from bs4 import BeautifulSoup
from module_4.src.front_end.app_factory import create_app


class FakePool:
    """Reusable fake database pool for testing."""

    # pylint: disable=R0903
    def __init__(self, initial=None):
        self.data = list(initial or [])

    def insert_rows(self, rows):
        """Insert rows while preventing duplicates based on 'url'."""
        existing = {r.get("url") for r in self.data if r.get("url")}
        for r in rows:
            if r.get("url") not in existing:
                self.data.append(r)
                existing.add(r.get("url"))


@pytest.fixture
def fake_pool_fixture():
    """Fixture that provides an empty FakePool."""
    return FakePool(initial=[])


@pytest.fixture
def fake_scraper_fixture():
    """Fixture scraper that returns no rows."""
    def scraper():
        return []
    return scraper


@pytest.fixture
# pylint: disable=redefined-outer-name
def flask_test_client(fake_pool_fixture, fake_scraper_fixture):
    """Provide a Flask test client with fake pool and scraper."""
    app = create_app(pool=fake_pool_fixture, scraper=fake_scraper_fixture)
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def populated_client():
    """Flask client with a fake pool preloaded by a scraper."""
    pool = FakePool()

    def scraper():
        return [{"url": "u1"}, {"url": "u2"}]

    app = create_app(pool=pool, scraper=scraper)
    app.config["TESTING"] = True
    client = app.test_client()
    return client, pool


@contextmanager
def busy_state_manager(app, is_busy):
    """Temporarily set the SCRAPING_IN_PROGRESS flag on the app."""
    original = getattr(app, "SCRAPING_IN_PROGRESS", False)
    app.SCRAPING_IN_PROGRESS = is_busy
    try:
        yield
    finally:
        app.SCRAPING_IN_PROGRESS = original


# ------------------------------
# Shared helpers for assertions
# ------------------------------

def assert_valid_analysis(res):
    """Assert that analysis response contains valid content with percentages."""
    html = res.get_data(as_text=True)
    soup = BeautifulSoup(html, "html.parser")
    assert "Answer:" in soup.text or "Answer" in soup.text

    percents = re.findall(r"\d+\.\d{2}%", soup.text)
    for p in percents:
        assert re.match(r"^\d+\.\d{2}%$", p)
