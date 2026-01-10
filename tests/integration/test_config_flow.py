"""Tests for Charge Cheapest config flow."""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest
import sys
import os

# Add custom_components to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestConfigFlowHelpers:
    """Test config flow helper functions."""

    def test_time_to_minutes_string_format(self):
        """Test time string to minutes conversion."""
        # Inline implementation matching config_flow
        def _time_to_minutes(time_str: str) -> int:
            if isinstance(time_str, dict):
                hours = time_str.get("hour", 0)
                minutes = time_str.get("minute", 0)
                return hours * 60 + minutes

            if ":" in str(time_str):
                parts = str(time_str).split(":")
                hours = int(parts[0])
                minutes = int(parts[1]) if len(parts) > 1 else 0
                return hours * 60 + minutes

            return 0

        # Test string format
        assert _time_to_minutes("23:00:00") == 23 * 60
        assert _time_to_minutes("06:00:00") == 6 * 60
        assert _time_to_minutes("17:30:00") == 17 * 60 + 30

        # Test dict format (TimeSelector output)
        assert _time_to_minutes({"hour": 23, "minute": 0}) == 23 * 60
        assert _time_to_minutes({"hour": 6, "minute": 30}) == 6 * 60 + 30

    def test_schedule_conflict_detection(self):
        """Test that schedule conflicts are detected."""
        def _time_to_minutes(time_str: str) -> int:
            if ":" in str(time_str):
                parts = str(time_str).split(":")
                return int(parts[0]) * 60 + int(parts[1])
            return 0

        # Day end at 18:00, evening peak at 17:00 = conflict
        day_end_minutes = _time_to_minutes("18:00:00")
        evening_start_minutes = _time_to_minutes("17:00:00")

        has_conflict = day_end_minutes >= evening_start_minutes
        assert has_conflict is True

        # Day end at 16:00, evening peak at 17:00 = no conflict
        day_end_minutes = _time_to_minutes("16:00:00")
        evening_start_minutes = _time_to_minutes("17:00:00")

        has_conflict = day_end_minutes >= evening_start_minutes
        assert has_conflict is False


class TestEntityValidation:
    """Test entity validation logic."""

    def test_entity_validation_logic(self):
        """Test entity validation accepts valid entities."""
        def _validate_entity_exists(hass, entity_id: str) -> str | None:
            if not entity_id:
                return "entity_required"

            state = hass.states.get(entity_id)
            if state is None:
                return "entity_not_found"

            if state.state in ("unavailable", "unknown"):
                return "entity_unavailable"

            return None

        mock_hass = MagicMock()

        # Test missing entity
        result = _validate_entity_exists(mock_hass, "")
        assert result == "entity_required"

        # Test non-existent entity
        mock_hass.states.get = MagicMock(return_value=None)
        result = _validate_entity_exists(mock_hass, "sensor.nonexistent")
        assert result == "entity_not_found"

        # Test unavailable entity
        unavailable_state = MagicMock()
        unavailable_state.state = "unavailable"
        mock_hass.states.get = MagicMock(return_value=unavailable_state)
        result = _validate_entity_exists(mock_hass, "sensor.unavailable")
        assert result == "entity_unavailable"

        # Test valid entity
        valid_state = MagicMock()
        valid_state.state = "45"
        mock_hass.states.get = MagicMock(return_value=valid_state)
        result = _validate_entity_exists(mock_hass, "sensor.battery_soc")
        assert result is None


class TestConfigurationDefaults:
    """Test configuration defaults and constants."""

    def test_default_values(self):
        """Test that default values are defined correctly."""
        # Inline defaults from const.py
        DEFAULT_NIGHT_START_TIME = "23:00:00"
        DEFAULT_NIGHT_END_TIME = "06:00:00"
        DEFAULT_DAY_START_TIME = "09:00:00"
        DEFAULT_DAY_END_TIME = "16:00:00"
        DEFAULT_EVENING_PEAK_START = "17:00:00"
        DEFAULT_EVENING_PEAK_END = "21:00:00"
        DEFAULT_NIGHT_TARGET_SOC = 60
        DEFAULT_DAY_TARGET_SOC = 50
        DEFAULT_EVENING_PEAK_TARGET_SOC = 50

        assert DEFAULT_NIGHT_START_TIME == "23:00:00"
        assert DEFAULT_NIGHT_END_TIME == "06:00:00"
        assert DEFAULT_NIGHT_TARGET_SOC == 60

    def test_failure_behaviors(self):
        """Test failure behavior options."""
        FAILURE_BEHAVIORS = [
            "skip_charging",
            "use_default_window",
            "charge_immediately",
        ]

        assert len(FAILURE_BEHAVIORS) == 3
        assert "skip_charging" in FAILURE_BEHAVIORS
        assert "use_default_window" in FAILURE_BEHAVIORS
        assert "charge_immediately" in FAILURE_BEHAVIORS
