"""Template for a focused pytest test module."""

from unittest.mock import patch

import pytest


# Example fixture: create a clean, reusable dependency for every test.
@pytest.fixture
def sample_input():
    """Return a sample input dictionary for testing purposes."""
    return {"name": "example", "value": 42}


# Example parametrized test: covers multiple similar cases in one function.
@pytest.mark.parametrize("value,expected", [(1, 2), (2, 4), (3, 6)])
def test_double_value(value, expected):
    """Test that the double_value function returns the expected value."""
    assert value * 2 == expected


def test_process_sample(sample_input):
    """Test that the process_sample function returns the expected value."""
    # Arrange / Act / Assert pattern.
    result = sample_input["value"] + 1
    assert result == 43


# Example of mocking an external boundary without mocking the unit under test.
@patch("module_under_test.external_api_call")
def test_unit_with_mocked_api(mock_api):
    """Test that the unit_with_mocked_api function returns the expected value."""
    mock_api.return_value = {"ok": True}
    # call the function that uses external_api_call
    assert mock_api.called
