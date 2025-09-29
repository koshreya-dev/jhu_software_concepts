"""Tests for the /buttons page and related functionality."""

import pytest

@pytest.mark.buttons
def test_buttons_page_loads(flask_test_client):
    """Ensure the /buttons page loads correctly."""
    res = flask_test_client.get("/buttons")
    assert res.status_code == 200


@pytest.mark.buttons
def test_pull_data_button(flask_test_client):
    """Ensure /pull-data works without errors."""
    res = flask_test_client.post("/pull-data")
    assert res.status_code in (200, 302)


@pytest.mark.buttons
def test_reload_data_button(flask_test_client):
    """Ensure /reload-data works without errors."""
    res = flask_test_client.post("/reload-data")
    assert res.status_code in (200, 302)


@pytest.mark.buttons
def test_analysis_button(flask_test_client):
    """Ensure /analysis works without errors."""
    res = flask_test_client.get("/analysis")
    assert res.status_code == 200
