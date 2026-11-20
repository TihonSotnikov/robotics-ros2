"""Test motion parameter validation without starting a ROS node."""

from patrol.patrol import validate_parameter
import pytest


@pytest.mark.parametrize('value', [10.0, 5.0, 1.0, 30.0])
def test_accepts_publish_frequency(value: float) -> None:
    """Accept the default, the new rate and both endpoints."""
    assert validate_parameter('publish_hz', value) == ''


@pytest.mark.parametrize('value', [0.0, -1.0, 30.1, float('nan'), float('inf')])
def test_rejects_publish_frequency(value: float) -> None:
    """Reject non-finite frequencies and frequencies outside the range."""
    assert validate_parameter('publish_hz', value)
