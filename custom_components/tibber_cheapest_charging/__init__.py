"""Tibber Cheapest Charging integration for Home Assistant.

This integration enables automatic battery charging during the cheapest electricity
hours based on Tibber price data. It supports configurable night and day charging
schedules with independent SOC targets.

YAML Configuration Example:
    tibber_cheapest_charging:
      battery_soc_sensor: sensor.battery_soc
      battery_charging_switch: switch.battery_charging
      price_sensor: sensor.tibber_prices
      night_start_time: "23:00:00"
      night_end_time: "06:00:00"
      night_target_soc: 60
      day_schedule_enabled: false

Prerequisites:
    - Tibber integration must be configured
    - cheapest-energy-hours Jinja macro (TheFes/cheapest-energy-hours)
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_BATTERY_CAPACITY_SENSOR,
    CONF_BATTERY_CHARGING_POWER,
    CONF_BATTERY_CHARGING_SWITCH,
    CONF_BATTERY_SOC_SENSOR,
    CONF_CHARGING_DURATION_HOURS,
    CONF_DAY_END_TIME,
    CONF_DAY_SCHEDULE_ENABLED,
    CONF_DAY_START_TIME,
    CONF_DAY_TARGET_SOC,
    CONF_DEFAULT_CHARGE_DURATION,
    CONF_DEFAULT_CHARGE_START_TIME,
    CONF_EVENING_PEAK_END,
    CONF_EVENING_PEAK_START,
    CONF_EVENING_PEAK_TARGET_SOC,
    CONF_FAILURE_BEHAVIOR,
    CONF_FORECAST_MODE_AUTOMATIC,
    CONF_MINIMUM_SOC_FLOOR,
    CONF_MORNING_CONSUMPTION_KWH,
    CONF_NIGHT_END_TIME,
    CONF_NIGHT_START_TIME,
    CONF_NIGHT_TARGET_SOC,
    CONF_NOTIFICATION_SERVICE,
    CONF_NOTIFY_CHARGING_COMPLETED,
    CONF_NOTIFY_CHARGING_ERROR,
    CONF_NOTIFY_CHARGING_SCHEDULED,
    CONF_NOTIFY_CHARGING_SKIPPED,
    CONF_NOTIFY_CHARGING_STARTED,
    CONF_NOTIFY_EMERGENCY_CHARGING,
    CONF_PRICE_SENSOR,
    CONF_SOC_OFFSET_KWH,
    CONF_SOLAR_FORECAST_ENABLED,
    CONF_SOLAR_FORECAST_SENSOR,
    CONF_TARGET_SOC,
    CONF_TRIGGER_TIME,
    DEFAULT_CHARGING_DURATION_HOURS,
    DEFAULT_DAY_END_TIME,
    DEFAULT_DAY_SCHEDULE_ENABLED,
    DEFAULT_DAY_START_TIME,
    DEFAULT_DAY_TARGET_SOC,
    DEFAULT_DEFAULT_CHARGE_DURATION,
    DEFAULT_DEFAULT_CHARGE_START_TIME,
    DEFAULT_EVENING_PEAK_END,
    DEFAULT_EVENING_PEAK_START,
    DEFAULT_EVENING_PEAK_TARGET_SOC,
    DEFAULT_FAILURE_BEHAVIOR,
    DEFAULT_FORECAST_MODE_AUTOMATIC,
    DEFAULT_MINIMUM_SOC_FLOOR,
    DEFAULT_MORNING_CONSUMPTION_KWH,
    DEFAULT_NIGHT_END_TIME,
    DEFAULT_NIGHT_START_TIME,
    DEFAULT_NIGHT_TARGET_SOC,
    DEFAULT_NOTIFICATION_SERVICE,
    DEFAULT_NOTIFY_CHARGING_COMPLETED,
    DEFAULT_NOTIFY_CHARGING_ERROR,
    DEFAULT_NOTIFY_CHARGING_SCHEDULED,
    DEFAULT_NOTIFY_CHARGING_SKIPPED,
    DEFAULT_NOTIFY_CHARGING_STARTED,
    DEFAULT_NOTIFY_EMERGENCY_CHARGING,
    DEFAULT_SOC_OFFSET_KWH,
    DEFAULT_SOLAR_FORECAST_ENABLED,
    DEFAULT_TARGET_SOC,
    DEFAULT_TRIGGER_TIME,
    DOMAIN,
    FAILURE_BEHAVIORS,
)
from .coordinator import TibberCheapestChargingCoordinator
from .dashboard import async_setup_dashboard, async_register_dashboard_service

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

# YAML Configuration Schema
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                # Required entities
                vol.Required(CONF_BATTERY_SOC_SENSOR): cv.entity_id,
                vol.Required(CONF_BATTERY_CHARGING_SWITCH): cv.entity_id,
                vol.Required(CONF_PRICE_SENSOR): cv.entity_id,
                # Optional entities
                vol.Optional(CONF_SOLAR_FORECAST_SENSOR): cv.entity_id,
                vol.Optional(CONF_BATTERY_CAPACITY_SENSOR): cv.entity_id,
                vol.Optional(CONF_BATTERY_CHARGING_POWER): cv.entity_id,
                # Schedule times
                vol.Optional(
                    CONF_NIGHT_START_TIME, default=DEFAULT_NIGHT_START_TIME
                ): cv.time,
                vol.Optional(
                    CONF_NIGHT_END_TIME, default=DEFAULT_NIGHT_END_TIME
                ): cv.time,
                vol.Optional(
                    CONF_DAY_SCHEDULE_ENABLED, default=DEFAULT_DAY_SCHEDULE_ENABLED
                ): cv.boolean,
                vol.Optional(
                    CONF_DAY_START_TIME, default=DEFAULT_DAY_START_TIME
                ): cv.time,
                vol.Optional(CONF_DAY_END_TIME, default=DEFAULT_DAY_END_TIME): cv.time,
                vol.Optional(
                    CONF_EVENING_PEAK_START, default=DEFAULT_EVENING_PEAK_START
                ): cv.time,
                vol.Optional(
                    CONF_EVENING_PEAK_END, default=DEFAULT_EVENING_PEAK_END
                ): cv.time,
                # SOC targets
                vol.Optional(
                    CONF_NIGHT_TARGET_SOC, default=DEFAULT_NIGHT_TARGET_SOC
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Optional(
                    CONF_DAY_TARGET_SOC, default=DEFAULT_DAY_TARGET_SOC
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Optional(
                    CONF_EVENING_PEAK_TARGET_SOC, default=DEFAULT_EVENING_PEAK_TARGET_SOC
                ): vol.All(vol.Coerce(int), vol.Range(min=20, max=100)),
                vol.Optional(CONF_TARGET_SOC, default=DEFAULT_TARGET_SOC): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=100)
                ),
                # Charging behavior
                vol.Optional(
                    CONF_CHARGING_DURATION_HOURS, default=DEFAULT_CHARGING_DURATION_HOURS
                ): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=8)),
                vol.Optional(
                    CONF_TRIGGER_TIME, default=DEFAULT_TRIGGER_TIME
                ): cv.time,
                vol.Optional(
                    CONF_FAILURE_BEHAVIOR, default=DEFAULT_FAILURE_BEHAVIOR
                ): vol.In(FAILURE_BEHAVIORS),
                vol.Optional(
                    CONF_DEFAULT_CHARGE_START_TIME,
                    default=DEFAULT_DEFAULT_CHARGE_START_TIME,
                ): cv.time,
                vol.Optional(
                    CONF_DEFAULT_CHARGE_DURATION, default=DEFAULT_DEFAULT_CHARGE_DURATION
                ): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=8)),
                # Notification settings
                vol.Optional(
                    CONF_NOTIFICATION_SERVICE, default=DEFAULT_NOTIFICATION_SERVICE
                ): cv.string,
                vol.Optional(
                    CONF_NOTIFY_CHARGING_SCHEDULED,
                    default=DEFAULT_NOTIFY_CHARGING_SCHEDULED,
                ): cv.boolean,
                vol.Optional(
                    CONF_NOTIFY_CHARGING_STARTED, default=DEFAULT_NOTIFY_CHARGING_STARTED
                ): cv.boolean,
                vol.Optional(
                    CONF_NOTIFY_CHARGING_COMPLETED,
                    default=DEFAULT_NOTIFY_CHARGING_COMPLETED,
                ): cv.boolean,
                vol.Optional(
                    CONF_NOTIFY_CHARGING_SKIPPED, default=DEFAULT_NOTIFY_CHARGING_SKIPPED
                ): cv.boolean,
                vol.Optional(
                    CONF_NOTIFY_CHARGING_ERROR, default=DEFAULT_NOTIFY_CHARGING_ERROR
                ): cv.boolean,
                vol.Optional(
                    CONF_NOTIFY_EMERGENCY_CHARGING,
                    default=DEFAULT_NOTIFY_EMERGENCY_CHARGING,
                ): cv.boolean,
                # Solar forecast settings
                vol.Optional(
                    CONF_SOLAR_FORECAST_ENABLED, default=DEFAULT_SOLAR_FORECAST_ENABLED
                ): cv.boolean,
                vol.Optional(
                    CONF_FORECAST_MODE_AUTOMATIC, default=DEFAULT_FORECAST_MODE_AUTOMATIC
                ): cv.boolean,
                vol.Optional(
                    CONF_MORNING_CONSUMPTION_KWH, default=DEFAULT_MORNING_CONSUMPTION_KWH
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=20)),
                vol.Optional(
                    CONF_SOC_OFFSET_KWH, default=DEFAULT_SOC_OFFSET_KWH
                ): vol.All(vol.Coerce(float), vol.Range(min=-10, max=10)),
                vol.Optional(
                    CONF_MINIMUM_SOC_FLOOR, default=DEFAULT_MINIMUM_SOC_FLOOR
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=50)),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def _convert_time_to_string(time_value: Any) -> str:
    """Convert time value to string format."""
    if hasattr(time_value, "strftime"):
        return time_value.strftime("%H:%M:%S")
    return str(time_value)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Tibber Cheapest Charging integration via YAML configuration."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    yaml_config = config[DOMAIN]

    # Check if a config entry already exists for YAML config
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.source == "yaml":
            _LOGGER.debug("YAML config entry already exists, skipping creation")
            return True

    # Validate Tibber integration is configured
    if not await _validate_tibber_integration(hass):
        _LOGGER.error(
            "Tibber integration is not configured. Please set up the Tibber integration first."
        )
        return False

    # Convert time objects to strings for ConfigEntry storage
    entry_data = {}
    for key, value in yaml_config.items():
        if key in [
            CONF_NIGHT_START_TIME,
            CONF_NIGHT_END_TIME,
            CONF_DAY_START_TIME,
            CONF_DAY_END_TIME,
            CONF_EVENING_PEAK_START,
            CONF_EVENING_PEAK_END,
            CONF_TRIGGER_TIME,
            CONF_DEFAULT_CHARGE_START_TIME,
        ]:
            entry_data[key] = _convert_time_to_string(value)
        else:
            entry_data[key] = value

    # Mark as YAML source
    entry_data["source"] = "yaml"

    # Create a config entry from YAML configuration
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data=entry_data,
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tibber Cheapest Charging from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Validate Tibber integration is configured
    if not await _validate_tibber_integration(hass):
        raise ConfigEntryNotReady(
            "Tibber integration is not configured. Please set up the Tibber integration first."
        )

    # Validate cheapest-energy-hours macro is available
    if not await _validate_cheapest_energy_macro(hass):
        _LOGGER.warning(
            "cheapest-energy-hours Jinja macro not found. Some features may not work correctly. "
            "Install from: https://github.com/TheFes/cheapest-energy-hours"
        )

    # Create coordinator
    coordinator = TibberCheapestChargingCoordinator(hass, entry)

    # Initial data fetch
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up dashboard
    await async_setup_dashboard(hass, entry)

    # Register dashboard recreation service
    await async_register_dashboard_service(hass)

    # Set up options update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Clean up coordinator
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        await coordinator.async_shutdown()

        # Remove entry data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _validate_tibber_integration(hass: HomeAssistant) -> bool:
    """Check if the Tibber integration is configured."""
    # Check if tibber integration is loaded
    if "tibber" not in hass.config.components:
        # Check if any tibber entities exist
        entity_registry = hass.helpers.entity_registry.async_get(hass)
        tibber_entities = [
            entity
            for entity in entity_registry.entities.values()
            if entity.platform == "tibber"
        ]
        if not tibber_entities:
            return False
    return True


async def _validate_cheapest_energy_macro(hass: HomeAssistant) -> bool:
    """Check if the cheapest-energy-hours Jinja macro is available."""
    try:
        # Try to check if the macro file exists in custom_templates
        import os

        custom_templates_path = hass.config.path("custom_templates")
        macro_file = os.path.join(
            custom_templates_path, "cheapest_energy_hours.jinja"
        )

        if os.path.exists(macro_file):
            return True

        # Also check in templates directory
        templates_path = hass.config.path("templates")
        macro_file_alt = os.path.join(templates_path, "cheapest_energy_hours.jinja")

        return os.path.exists(macro_file_alt)
    except Exception:
        # If we can't check, assume it might be available
        return True
