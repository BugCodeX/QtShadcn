"""Template for shared pytest fixtures via conftest.py."""

import pytest


@pytest.fixture(scope="session")
def app_config():
    """Return a configuration object used across the test suite."""
    return {"debug": True, "env": "test"}


@pytest.fixture
def temp_user(tmp_path):
    """Provide a temporary user record or data directory."""
    return {"id": 1, "home": tmp_path / "user"}


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Patch environment variables for the duration of a test."""
    monkeypatch.setenv("TEST_ENV", "true")
    return monkeypatch
