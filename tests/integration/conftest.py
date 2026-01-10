"""Fixtures for Charge Cheapest integration tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    hass.config = MagicMock()
    hass.config.components = {"tibber"}
    hass.config.path = MagicMock(return_value="/config/custom_templates")
    hass.states = MagicMock()
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()
    hass.services.has_service = MagicMock(return_value=False)
    hass.services.async_register = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_entries = MagicMock(return_value=[])
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.async_create_task = MagicMock()
    hass.helpers = MagicMock()
    hass.helpers.entity_registry = MagicMock()
    hass.helpers.entity_registry.async_get = MagicMock(return_value=MagicMock(entities=MagicMock(values=MagicMock(return_value=[]))))
    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "battery_soc_sensor": "sensor.battery_soc",
        "battery_charging_switch": "switch.battery_charging",
        "price_sensor": "sensor.tibber_prices",
        "night_start_time": "23:00:00",
        "night_end_time": "06:00:00",
        "night_target_soc": 60,
        "day_schedule_enabled": False,
        "day_start_time": "09:00:00",
        "day_end_time": "16:00:00",
        "day_target_soc": 50,
        "evening_peak_start": "17:00:00",
        "evening_peak_end": "21:00:00",
        "evening_peak_target_soc": 50,
    }
    entry.options = {}
    entry.source = "user"
    entry.add_update_listener = MagicMock()
    entry.async_on_unload = MagicMock()
    return entry


@pytest.fixture
def mock_tibber_state():
    """Create mock Tibber price sensor state."""
    state = MagicMock()
    state.state = "0.25"
    state.attributes = {
        "today": [
            {"total": 0.20},
            {"total": 0.22},
            {"total": 0.25},
            {"total": 0.28},
            {"total": 0.35},
            {"total": 0.30},
            {"total": 0.25},
            {"total": 0.22},
            {"total": 0.20},
            {"total": 0.18},
            {"total": 0.15},
            {"total": 0.12},
            {"total": 0.15},
            {"total": 0.18},
            {"total": 0.22},
            {"total": 0.25},
            {"total": 0.28},
            {"total": 0.35},
            {"total": 0.40},
            {"total": 0.45},
            {"total": 0.40},
            {"total": 0.35},
            {"total": 0.30},
            {"total": 0.25},
        ],
        "tomorrow": [
            {"total": 0.18},
            {"total": 0.15},
            {"total": 0.12},
            {"total": 0.10},
            {"total": 0.12},
            {"total": 0.15},
            {"total": 0.18},
            {"total": 0.22},
            {"total": 0.25},
            {"total": 0.28},
            {"total": 0.30},
            {"total": 0.32},
            {"total": 0.30},
            {"total": 0.28},
            {"total": 0.25},
            {"total": 0.28},
            {"total": 0.35},
            {"total": 0.42},
            {"total": 0.48},
            {"total": 0.45},
            {"total": 0.40},
            {"total": 0.35},
            {"total": 0.30},
            {"total": 0.25},
        ],
    }
    return state


@pytest.fixture
def mock_battery_soc_state():
    """Create mock battery SOC sensor state."""
    state = MagicMock()
    state.state = "45"
    state.attributes = {"unit_of_measurement": "%"}
    return state


@pytest.fixture
def mock_battery_capacity_state():
    """Create mock battery capacity sensor state."""
    state = MagicMock()
    state.state = "10"
    state.attributes = {"unit_of_measurement": "kWh"}
    return state


@pytest.fixture
def mock_charging_power_state():
    """Create mock charging power input_number state."""
    state = MagicMock()
    state.state = "3000"
    state.attributes = {"unit_of_measurement": "W"}
    return state


@pytest.fixture
def mock_charging_switch_state():
    """Create mock charging switch state."""
    state = MagicMock()
    state.state = "off"
    return state


def create_state_getter(states_dict: dict[str, Any]):
    """Create a state getter function from a dictionary."""
    def get_state(entity_id: str):
        return states_dict.get(entity_id)
    return get_state
