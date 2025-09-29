"""Tests for database insert behavior with FakePool."""

import pytest
from module_4.src.front_end.app_factory import create_app
from .conftest import FakePool


@pytest.mark.db
def test_inserts_unique_urls_only():
    """Ensure FakePool inserts only unique URLs."""
    fake_pool = FakePool()

    def fake_scraper():
        return [{"url": "u1"}, {"url": "u1"}]

    app = create_app(pool=fake_pool, scraper=fake_scraper)
    app.config["TESTING"] = True
    client = app.test_client()

    client.post("/pull-data")
    assert len(fake_pool.data) == 1


@pytest.mark.db
def test_double_insert(populated_client):
    """Ensure posting /pull-data twice inserts only two rows."""
    client, pool = populated_client

    client.post("/pull-data")
    client.post("/pull-data")

    assert len(pool.data) == 2
