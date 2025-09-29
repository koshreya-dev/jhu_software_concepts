"""Tests for general Flask page routes."""

import pytest

@pytest.mark.pages
def test_analysis_page_loads(flask_test_client):
    """Ensure /analysis page loads successfully."""
    res = flask_test_client.get("/analysis")
    assert res.status_code == 200
