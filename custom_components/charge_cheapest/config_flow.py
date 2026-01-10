"""Config flow for Charge Cheapest integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

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
    SERVICE_RECREATE_DASHBOARD,
)

_LOGGER = logging.getLogger(__name__)


def _validate_entity_exists(hass: HomeAssistant, entity_id: str) -> str | None:
    """Validate that an entity exists and is not unavailable.

    Returns an error key for translation, or None if valid.
    """
    if not entity_id:
        return "entity_required"

    state = hass.states.get(entity_id)
    if state is None:
        return "entity_not_found"

    if state.state in ("unavailable", "unknown"):
        return "entity_unavailable"

    return None


class TibberCheapestChargingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Charge Cheapest."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - required entity selection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate required entities
            for entity_key in [
                CONF_BATTERY_SOC_SENSOR,
                CONF_BATTERY_CHARGING_SWITCH,
                CONF_PRICE_SENSOR,
            ]:
                entity_id = user_input.get(entity_key)
                error = _validate_entity_exists(self.hass, entity_id)
                if error:
                    errors[entity_key] = error

            if not errors:
                self._data.update(user_input)
                return await self.async_step_optional_entities()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BATTERY_SOC_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Required(CONF_BATTERY_CHARGING_SWITCH): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="switch")
                    ),
                    vol.Required(CONF_PRICE_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_optional_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the optional entity selection step."""
        if user_input is not None:
            # Filter out empty values
            for key, value in user_input.items():
                if value:
                    self._data[key] = value
            return await self.async_step_schedule()

        return self.async_show_form(
            step_id="optional_entities",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SOLAR_FORECAST_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Optional(CONF_BATTERY_CAPACITY_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Optional(CONF_BATTERY_CHARGING_POWER): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="input_number")
                    ),
                }
            ),
        )

    async def async_step_schedule(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the schedule configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate schedule times don't conflict
            if user_input.get(CONF_DAY_SCHEDULE_ENABLED, False):
                day_end = user_input.get(CONF_DAY_END_TIME, DEFAULT_DAY_END_TIME)
                evening_start = user_input.get(
                    CONF_EVENING_PEAK_START, DEFAULT_EVENING_PEAK_START
                )

                # Parse times for comparison
                try:
                    day_end_minutes = _time_to_minutes(day_end)
                    evening_start_minutes = _time_to_minutes(evening_start)

                    if day_end_minutes >= evening_start_minutes:
                        errors["base"] = "schedule_conflict"
                except (ValueError, TypeError):
                    pass

            if not errors:
                self._data.update(user_input)
                return self.async_create_entry(
                    title="Charge Cheapest",
                    data=self._data,
                )

        return self.async_show_form(
            step_id="schedule",
            data_schema=vol.Schema(
                {
                    # Night schedule
                    vol.Optional(
                        CONF_NIGHT_START_TIME, default=DEFAULT_NIGHT_START_TIME
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_NIGHT_END_TIME, default=DEFAULT_NIGHT_END_TIME
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_NIGHT_TARGET_SOC, default=DEFAULT_NIGHT_TARGET_SOC
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=100, step=5, unit_of_measurement="%", mode="slider"
                        )
                    ),
                    # Day schedule
                    vol.Optional(
                        CONF_DAY_SCHEDULE_ENABLED, default=DEFAULT_DAY_SCHEDULE_ENABLED
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DAY_START_TIME, default=DEFAULT_DAY_START_TIME
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_DAY_END_TIME, default=DEFAULT_DAY_END_TIME
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_DAY_TARGET_SOC, default=DEFAULT_DAY_TARGET_SOC
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=100, step=5, unit_of_measurement="%", mode="slider"
                        )
                    ),
                    # Evening peak
                    vol.Optional(
                        CONF_EVENING_PEAK_START, default=DEFAULT_EVENING_PEAK_START
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_EVENING_PEAK_END, default=DEFAULT_EVENING_PEAK_END
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_EVENING_PEAK_TARGET_SOC,
                        default=DEFAULT_EVENING_PEAK_TARGET_SOC,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=20, max=100, step=5, unit_of_measurement="%", mode="slider"
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_import(
        self, import_config: dict[str, Any]
    ) -> FlowResult:
        """Handle import from YAML configuration."""
        # Check if already configured
        await self.async_set_unique_id("yaml_import")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="Charge Cheapest (YAML)",
            data=import_config,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return TibberCheapestChargingOptionsFlow(config_entry)


class TibberCheapestChargingOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Charge Cheapest."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if recreate dashboard was requested
            if user_input.pop("recreate_dashboard", False):
                await self._trigger_dashboard_recreation()

            # Validate schedule times
            if user_input.get(CONF_DAY_SCHEDULE_ENABLED, False):
                day_end = user_input.get(CONF_DAY_END_TIME, DEFAULT_DAY_END_TIME)
                evening_start = user_input.get(
                    CONF_EVENING_PEAK_START, DEFAULT_EVENING_PEAK_START
                )

                try:
                    day_end_minutes = _time_to_minutes(day_end)
                    evening_start_minutes = _time_to_minutes(evening_start)

                    if day_end_minutes >= evening_start_minutes:
                        errors["base"] = "schedule_conflict"
                except (ValueError, TypeError):
                    pass

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        # Get current values
        current_data = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    # SOC targets
                    vol.Optional(
                        CONF_NIGHT_TARGET_SOC,
                        default=current_data.get(
                            CONF_NIGHT_TARGET_SOC, DEFAULT_NIGHT_TARGET_SOC
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=100, step=5, unit_of_measurement="%", mode="slider"
                        )
                    ),
                    vol.Optional(
                        CONF_DAY_TARGET_SOC,
                        default=current_data.get(
                            CONF_DAY_TARGET_SOC, DEFAULT_DAY_TARGET_SOC
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=100, step=5, unit_of_measurement="%", mode="slider"
                        )
                    ),
                    vol.Optional(
                        CONF_EVENING_PEAK_TARGET_SOC,
                        default=current_data.get(
                            CONF_EVENING_PEAK_TARGET_SOC, DEFAULT_EVENING_PEAK_TARGET_SOC
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=20, max=100, step=5, unit_of_measurement="%", mode="slider"
                        )
                    ),
                    # Schedule times
                    vol.Optional(
                        CONF_NIGHT_START_TIME,
                        default=current_data.get(
                            CONF_NIGHT_START_TIME, DEFAULT_NIGHT_START_TIME
                        ),
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_NIGHT_END_TIME,
                        default=current_data.get(
                            CONF_NIGHT_END_TIME, DEFAULT_NIGHT_END_TIME
                        ),
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_DAY_SCHEDULE_ENABLED,
                        default=current_data.get(
                            CONF_DAY_SCHEDULE_ENABLED, DEFAULT_DAY_SCHEDULE_ENABLED
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DAY_START_TIME,
                        default=current_data.get(
                            CONF_DAY_START_TIME, DEFAULT_DAY_START_TIME
                        ),
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_DAY_END_TIME,
                        default=current_data.get(CONF_DAY_END_TIME, DEFAULT_DAY_END_TIME),
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_EVENING_PEAK_START,
                        default=current_data.get(
                            CONF_EVENING_PEAK_START, DEFAULT_EVENING_PEAK_START
                        ),
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_EVENING_PEAK_END,
                        default=current_data.get(
                            CONF_EVENING_PEAK_END, DEFAULT_EVENING_PEAK_END
                        ),
                    ): selector.TimeSelector(),
                    # Notification preferences
                    vol.Optional(
                        CONF_NOTIFY_CHARGING_SCHEDULED,
                        default=current_data.get(
                            CONF_NOTIFY_CHARGING_SCHEDULED,
                            DEFAULT_NOTIFY_CHARGING_SCHEDULED,
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_NOTIFY_CHARGING_STARTED,
                        default=current_data.get(
                            CONF_NOTIFY_CHARGING_STARTED, DEFAULT_NOTIFY_CHARGING_STARTED
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_NOTIFY_CHARGING_COMPLETED,
                        default=current_data.get(
                            CONF_NOTIFY_CHARGING_COMPLETED,
                            DEFAULT_NOTIFY_CHARGING_COMPLETED,
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_NOTIFY_CHARGING_SKIPPED,
                        default=current_data.get(
                            CONF_NOTIFY_CHARGING_SKIPPED, DEFAULT_NOTIFY_CHARGING_SKIPPED
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_NOTIFY_CHARGING_ERROR,
                        default=current_data.get(
                            CONF_NOTIFY_CHARGING_ERROR, DEFAULT_NOTIFY_CHARGING_ERROR
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_NOTIFY_EMERGENCY_CHARGING,
                        default=current_data.get(
                            CONF_NOTIFY_EMERGENCY_CHARGING,
                            DEFAULT_NOTIFY_EMERGENCY_CHARGING,
                        ),
                    ): selector.BooleanSelector(),
                    # Solar forecast settings
                    vol.Optional(
                        CONF_SOLAR_FORECAST_ENABLED,
                        default=current_data.get(
                            CONF_SOLAR_FORECAST_ENABLED, DEFAULT_SOLAR_FORECAST_ENABLED
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_FORECAST_MODE_AUTOMATIC,
                        default=current_data.get(
                            CONF_FORECAST_MODE_AUTOMATIC, DEFAULT_FORECAST_MODE_AUTOMATIC
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_MORNING_CONSUMPTION_KWH,
                        default=current_data.get(
                            CONF_MORNING_CONSUMPTION_KWH, DEFAULT_MORNING_CONSUMPTION_KWH
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=20, step=0.5, unit_of_measurement="kWh", mode="slider"
                        )
                    ),
                    vol.Optional(
                        CONF_SOC_OFFSET_KWH,
                        default=current_data.get(
                            CONF_SOC_OFFSET_KWH, DEFAULT_SOC_OFFSET_KWH
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=-10, max=10, step=0.5, unit_of_measurement="kWh", mode="slider"
                        )
                    ),
                    vol.Optional(
                        CONF_MINIMUM_SOC_FLOOR,
                        default=current_data.get(
                            CONF_MINIMUM_SOC_FLOOR, DEFAULT_MINIMUM_SOC_FLOOR
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=10, max=50, step=5, unit_of_measurement="%", mode="slider"
                        )
                    ),
                    # Failure behavior
                    vol.Optional(
                        CONF_FAILURE_BEHAVIOR,
                        default=current_data.get(
                            CONF_FAILURE_BEHAVIOR, DEFAULT_FAILURE_BEHAVIOR
                        ),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=FAILURE_BEHAVIORS,
                            mode="dropdown",
                        )
                    ),
                    vol.Optional(
                        CONF_CHARGING_DURATION_HOURS,
                        default=current_data.get(
                            CONF_CHARGING_DURATION_HOURS, DEFAULT_CHARGING_DURATION_HOURS
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0.5, max=8, step=0.5, unit_of_measurement="h", mode="slider"
                        )
                    ),
                    vol.Optional(
                        CONF_DEFAULT_CHARGE_DURATION,
                        default=current_data.get(
                            CONF_DEFAULT_CHARGE_DURATION, DEFAULT_DEFAULT_CHARGE_DURATION
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0.5, max=8, step=0.5, unit_of_measurement="h", mode="slider"
                        )
                    ),
                    # Recreate Dashboard button
                    vol.Optional("recreate_dashboard", default=False): selector.BooleanSelector(),
                }
            ),
            errors=errors,
        )

    async def _trigger_dashboard_recreation(self) -> None:
        """Trigger dashboard recreation service."""
        try:
            await self.hass.services.async_call(
                DOMAIN,
                SERVICE_RECREATE_DASHBOARD,
                {},
            )
            # Show success notification
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Dashboard Recreated",
                    "message": "The Charge Cheapest dashboard has been recreated successfully.",
                    "notification_id": "charge_cheapest_dashboard_recreated",
                },
            )
        except Exception as err:
            _LOGGER.error("Failed to recreate dashboard: %s", err)


def _time_to_minutes(time_str: str) -> int:
    """Convert time string to minutes since midnight."""
    if isinstance(time_str, dict):
        # Handle TimeSelector output format
        hours = time_str.get("hour", 0)
        minutes = time_str.get("minute", 0)
        return hours * 60 + minutes

    if ":" in str(time_str):
        parts = str(time_str).split(":")
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        return hours * 60 + minutes

    return 0
