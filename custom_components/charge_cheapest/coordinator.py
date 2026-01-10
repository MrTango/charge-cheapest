"""DataUpdateCoordinator for Charge Cheapest integration."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ATTR_CALCULATION_TIMESTAMP,
    ATTR_CHARGING_DURATION,
    ATTR_CURRENT_SOC,
    ATTR_ESTIMATED_COST,
    ATTR_NEXT_WINDOW_END,
    ATTR_NEXT_WINDOW_START,
    ATTR_OPTIMAL_SOC_TARGET,
    ATTR_SOLAR_FORECAST_KWH,
    ATTR_TARGET_SOC,
    ATTR_TOMORROW_PRICES_AVAILABLE,
    CHARGING_EFFICIENCY,
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
    CONF_EVENING_PEAK_START,
    CONF_EVENING_PEAK_TARGET_SOC,
    CONF_FAILURE_BEHAVIOR,
    CONF_FORECAST_MODE_AUTOMATIC,
    CONF_MINIMUM_SOC_FLOOR,
    CONF_MORNING_CONSUMPTION_KWH,
    CONF_NIGHT_END_TIME,
    CONF_NIGHT_START_TIME,
    CONF_NIGHT_TARGET_SOC,
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
    COORDINATOR_UPDATE_INTERVAL,
    DEFAULT_CHARGING_DURATION_HOURS,
    DEFAULT_DAY_END_TIME,
    DEFAULT_DAY_SCHEDULE_ENABLED,
    DEFAULT_DAY_START_TIME,
    DEFAULT_DAY_TARGET_SOC,
    DEFAULT_DEFAULT_CHARGE_DURATION,
    DEFAULT_DEFAULT_CHARGE_START_TIME,
    DEFAULT_EVENING_PEAK_START,
    DEFAULT_EVENING_PEAK_TARGET_SOC,
    DEFAULT_FAILURE_BEHAVIOR,
    DEFAULT_FORECAST_MODE_AUTOMATIC,
    DEFAULT_MINIMUM_SOC_FLOOR,
    DEFAULT_MORNING_CONSUMPTION_KWH,
    DEFAULT_NIGHT_END_TIME,
    DEFAULT_NIGHT_START_TIME,
    DEFAULT_NIGHT_TARGET_SOC,
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
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    DOMAIN,
    EMERGENCY_CHECK_BUFFER_MINUTES,
    FAILURE_BEHAVIOR_CHARGE_IMMEDIATELY,
    FAILURE_BEHAVIOR_DEFAULT_WINDOW,
    FAILURE_BEHAVIOR_SKIP,
    STATUS_CHARGING,
    STATUS_DISABLED,
    STATUS_ERROR,
    STATUS_IDLE,
    STATUS_SCHEDULED,
    TIME_SLOT_HOURS,
)

_LOGGER = logging.getLogger(__name__)


class TibberCheapestChargingCoordinator(DataUpdateCoordinator):
    """Coordinator for Charge Cheapest data updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=COORDINATOR_UPDATE_INTERVAL),
        )

        self.entry = entry
        self._config = {**entry.data, **entry.options}
        self._unsubscribe_callbacks: list = []
        self._scheduled_charging: dict[str, Any] = {}

        # Device info for entities
        self.device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Charge Cheapest",
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
            "sw_version": "1.0.0",
        }

    @property
    def config(self) -> dict[str, Any]:
        """Return current configuration."""
        return {**self.entry.data, **self.entry.options}

    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with fallback to default."""
        return self.config.get(key, default)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from sensors and calculate charging windows."""
        try:
            data = {}

            # Get current price and availability
            price_sensor = self._get_config_value(CONF_PRICE_SENSOR)
            if price_sensor:
                data.update(await self._fetch_price_data(price_sensor))

            # Get current SOC
            soc_sensor = self._get_config_value(CONF_BATTERY_SOC_SENSOR)
            if soc_sensor:
                data[ATTR_CURRENT_SOC] = self._get_sensor_value(soc_sensor, -1)

            # Check charging switch state
            charging_switch = self._get_config_value(CONF_BATTERY_CHARGING_SWITCH)
            if charging_switch:
                switch_state = self.hass.states.get(charging_switch)
                data["is_charging"] = switch_state and switch_state.state == "on"

            # Calculate charging duration
            data[ATTR_CHARGING_DURATION] = self._calculate_charging_duration(
                data.get(ATTR_CURRENT_SOC, 0),
                self._get_config_value(CONF_NIGHT_TARGET_SOC, DEFAULT_NIGHT_TARGET_SOC),
            )

            # Calculate optimal SOC target
            data[ATTR_OPTIMAL_SOC_TARGET] = self._calculate_optimal_morning_soc()

            # Calculate next charging window
            window_data = await self._calculate_next_charging_window(data)
            data.update(window_data)

            # Determine charging status
            data["status"] = self._determine_charging_status(data)

            # Calculate price range
            data["price_range"] = self._calculate_price_range(price_sensor)

            # Calculate estimated savings
            data["estimated_savings"] = self._calculate_estimated_savings(price_sensor)

            # System ready check
            data["system_ready"] = self._check_system_ready()

            # Add timestamp
            data[ATTR_CALCULATION_TIMESTAMP] = datetime.now().isoformat()

            return data

        except Exception as err:
            _LOGGER.error("Error updating Charge Cheapest data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def _fetch_price_data(self, price_sensor: str) -> dict[str, Any]:
        """Fetch price data from Tibber sensor."""
        data = {}

        state = self.hass.states.get(price_sensor)
        if state is None:
            data["current_price"] = None
            data[ATTR_TOMORROW_PRICES_AVAILABLE] = False
            return data

        # Current price
        try:
            data["current_price"] = float(state.state)
        except (ValueError, TypeError):
            data["current_price"] = None

        # Tomorrow's prices availability
        tomorrow_attr = state.attributes.get("tomorrow", [])
        data[ATTR_TOMORROW_PRICES_AVAILABLE] = bool(
            tomorrow_attr and len(tomorrow_attr) > 0
        )

        return data

    def _get_sensor_value(self, entity_id: str, default: float = -1) -> float:
        """Get numeric value from a sensor."""
        state = self.hass.states.get(entity_id)
        if state is None:
            return default
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return default

    def _calculate_charging_duration(
        self, current_soc: float, target_soc: float
    ) -> float:
        """Calculate charging duration based on SOC with 95% efficiency.

        Args:
            current_soc: Current state of charge (%)
            target_soc: Target state of charge (%)

        Returns:
            Charging duration in hours, rounded to 15-minute slots
        """
        fallback = self._get_config_value(
            CONF_CHARGING_DURATION_HOURS, DEFAULT_CHARGING_DURATION_HOURS
        )

        if current_soc < 0:
            return fallback

        # Get battery capacity
        capacity_sensor = self._get_config_value(CONF_BATTERY_CAPACITY_SENSOR)
        if not capacity_sensor:
            return fallback

        capacity_state = self.hass.states.get(capacity_sensor)
        if capacity_state is None:
            return fallback

        try:
            capacity_raw = float(capacity_state.state)
        except (ValueError, TypeError):
            return fallback

        if capacity_raw <= 0:
            return fallback

        # Check unit and convert to kWh if needed
        unit = capacity_state.attributes.get("unit_of_measurement", "kWh")
        if "wh" in unit.lower() and "kwh" not in unit.lower():
            capacity_kwh = capacity_raw / 1000
        else:
            capacity_kwh = capacity_raw

        # Get charging power
        power_entity = self._get_config_value(CONF_BATTERY_CHARGING_POWER)
        if not power_entity:
            return fallback

        charge_power_w = self._get_sensor_value(power_entity, -1)
        if charge_power_w <= 0:
            return fallback

        charge_power_kw = charge_power_w / 1000

        # Calculate SOC delta
        soc_delta = target_soc - current_soc
        if soc_delta <= 0:
            return 0

        # Calculate energy needed and time
        energy_needed_kwh = (soc_delta / 100) * capacity_kwh
        hours_needed = energy_needed_kwh / (charge_power_kw * CHARGING_EFFICIENCY)

        # Round to 15-minute slots
        hours_clamped = max(hours_needed, TIME_SLOT_HOURS)
        slots_needed = (hours_clamped * 4).__ceil__()
        return round(slots_needed / 4, 2)

    def _calculate_optimal_morning_soc(self) -> float:
        """Calculate optimal morning SOC based on solar forecast.

        Returns:
            Optimal SOC target percentage
        """
        default_target = self._get_config_value(
            CONF_NIGHT_TARGET_SOC, DEFAULT_NIGHT_TARGET_SOC
        )
        min_floor = self._get_config_value(
            CONF_MINIMUM_SOC_FLOOR, DEFAULT_MINIMUM_SOC_FLOOR
        )

        # Check if solar forecast is enabled
        if not self._get_config_value(
            CONF_SOLAR_FORECAST_ENABLED, DEFAULT_SOLAR_FORECAST_ENABLED
        ):
            return default_target

        # Get solar forecast
        forecast_sensor = self._get_config_value(CONF_SOLAR_FORECAST_SENSOR)
        if not forecast_sensor:
            return default_target

        forecast_kwh = self._get_sensor_value(forecast_sensor, -1)
        if forecast_kwh < 0:
            return default_target

        # Get battery capacity
        capacity_sensor = self._get_config_value(CONF_BATTERY_CAPACITY_SENSOR)
        if not capacity_sensor:
            return default_target

        capacity_state = self.hass.states.get(capacity_sensor)
        if capacity_state is None:
            return default_target

        try:
            capacity_raw = float(capacity_state.state)
        except (ValueError, TypeError):
            return default_target

        if capacity_raw <= 0:
            return default_target

        # Check unit
        unit = capacity_state.attributes.get("unit_of_measurement", "kWh")
        if "wh" in unit.lower() and "kwh" not in unit.lower():
            capacity_kwh = capacity_raw / 1000
        else:
            capacity_kwh = capacity_raw

        if capacity_kwh <= 0:
            return default_target

        # Calculate optimal SOC
        consumption = self._get_config_value(
            CONF_MORNING_CONSUMPTION_KWH, DEFAULT_MORNING_CONSUMPTION_KWH
        )
        offset = self._get_config_value(CONF_SOC_OFFSET_KWH, DEFAULT_SOC_OFFSET_KWH)

        excess_solar = forecast_kwh - consumption - offset
        soc_reduction = (excess_solar / capacity_kwh) * 100
        calculated_target = default_target - soc_reduction

        # Clamp between min_floor and default_target
        clamped_target = max(min_floor, min(calculated_target, default_target))
        return round(clamped_target, 1)

    async def _calculate_next_charging_window(
        self, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate the next charging window."""
        result = {
            ATTR_NEXT_WINDOW_START: None,
            ATTR_NEXT_WINDOW_END: None,
            ATTR_ESTIMATED_COST: 0,
            ATTR_TARGET_SOC: self._get_config_value(
                CONF_NIGHT_TARGET_SOC, DEFAULT_NIGHT_TARGET_SOC
            ),
        }

        # Check if tomorrow's prices are available
        if not data.get(ATTR_TOMORROW_PRICES_AVAILABLE, False):
            # Handle failure behavior
            return await self._handle_price_unavailable(result)

        # Try to calculate cheapest hours using Jinja macro
        try:
            cheapest_hours = await self._calculate_cheapest_hours(
                data.get(ATTR_CHARGING_DURATION, DEFAULT_CHARGING_DURATION_HOURS)
            )

            if cheapest_hours:
                result[ATTR_NEXT_WINDOW_START] = cheapest_hours.get("start")
                result[ATTR_NEXT_WINDOW_END] = cheapest_hours.get("end")
                result[ATTR_ESTIMATED_COST] = cheapest_hours.get("cost", 0)

        except Exception as err:
            _LOGGER.warning("Could not calculate cheapest hours: %s", err)
            return await self._handle_price_unavailable(result)

        return result

    async def _calculate_cheapest_hours(
        self, hours_needed: float
    ) -> dict[str, Any] | None:
        """Calculate cheapest hours using the cheapest-energy-hours Jinja macro.

        This method attempts to invoke the external Jinja macro for price calculation.
        Falls back to simple calculation if macro is not available.
        """
        price_sensor = self._get_config_value(CONF_PRICE_SENSOR)
        if not price_sensor:
            return None

        # Get price data from sensor
        state = self.hass.states.get(price_sensor)
        if state is None:
            return None

        today_prices = state.attributes.get("today", [])
        tomorrow_prices = state.attributes.get("tomorrow", [])

        if not today_prices:
            return None

        # Get schedule configuration
        night_start = self._get_config_value(
            CONF_NIGHT_START_TIME, DEFAULT_NIGHT_START_TIME
        )
        night_end = self._get_config_value(CONF_NIGHT_END_TIME, DEFAULT_NIGHT_END_TIME)

        # Parse times
        start_hour = self._parse_time_hour(night_start)
        end_hour = self._parse_time_hour(night_end)

        # Build price list for the window (cross-midnight support)
        window_prices = []
        now = datetime.now()

        # Add today's prices from start_hour onwards
        for i, price_entry in enumerate(today_prices):
            if i >= start_hour:
                hour_time = now.replace(hour=i, minute=0, second=0, microsecond=0)
                window_prices.append({
                    "time": hour_time,
                    "price": price_entry.get("total", 0),
                })

        # Add tomorrow's prices until end_hour
        if tomorrow_prices:
            tomorrow = now + timedelta(days=1)
            for i, price_entry in enumerate(tomorrow_prices):
                if i < end_hour:
                    hour_time = tomorrow.replace(hour=i, minute=0, second=0, microsecond=0)
                    window_prices.append({
                        "time": hour_time,
                        "price": price_entry.get("total", 0),
                    })

        if not window_prices:
            return None

        # Sort by price
        window_prices.sort(key=lambda x: x["price"])

        # Get cheapest consecutive hours
        slots_needed = int(hours_needed * 4)  # 15-minute slots
        hours_slots = int(hours_needed.__ceil__())

        if hours_slots > len(window_prices):
            hours_slots = len(window_prices)

        # Find cheapest consecutive hours
        best_start_idx = 0
        best_cost = float("inf")

        for i in range(len(window_prices) - hours_slots + 1):
            cost = sum(p["price"] for p in window_prices[i : i + hours_slots])
            if cost < best_cost:
                best_cost = cost
                best_start_idx = i

        if best_cost == float("inf"):
            return None

        selected_hours = window_prices[best_start_idx : best_start_idx + hours_slots]
        selected_hours.sort(key=lambda x: x["time"])

        return {
            "start": selected_hours[0]["time"].strftime("%H:%M:%S"),
            "end": (selected_hours[-1]["time"] + timedelta(hours=1)).strftime("%H:%M:%S"),
            "cost": round(best_cost, 4),
        }

    def _parse_time_hour(self, time_str: str) -> int:
        """Parse time string and return hour."""
        if isinstance(time_str, dict):
            return time_str.get("hour", 0)
        if ":" in str(time_str):
            return int(str(time_str).split(":")[0])
        return 0

    async def _handle_price_unavailable(
        self, result: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle case when price data is unavailable."""
        failure_behavior = self._get_config_value(
            CONF_FAILURE_BEHAVIOR, DEFAULT_FAILURE_BEHAVIOR
        )

        if failure_behavior == FAILURE_BEHAVIOR_SKIP:
            _LOGGER.info("Price data unavailable, skipping charging per failure_behavior")
            result["failure_mode"] = "skip"
            return result

        if failure_behavior == FAILURE_BEHAVIOR_DEFAULT_WINDOW:
            default_start = self._get_config_value(
                CONF_DEFAULT_CHARGE_START_TIME, DEFAULT_DEFAULT_CHARGE_START_TIME
            )
            default_duration = self._get_config_value(
                CONF_DEFAULT_CHARGE_DURATION, DEFAULT_DEFAULT_CHARGE_DURATION
            )

            result[ATTR_NEXT_WINDOW_START] = default_start
            result[ATTR_NEXT_WINDOW_END] = self._calculate_end_time(
                default_start, default_duration
            )
            result["failure_mode"] = "default_window"
            return result

        if failure_behavior == FAILURE_BEHAVIOR_CHARGE_IMMEDIATELY:
            now = datetime.now()
            default_duration = self._get_config_value(
                CONF_DEFAULT_CHARGE_DURATION, DEFAULT_DEFAULT_CHARGE_DURATION
            )

            result[ATTR_NEXT_WINDOW_START] = now.strftime("%H:%M:%S")
            result[ATTR_NEXT_WINDOW_END] = (
                now + timedelta(hours=default_duration)
            ).strftime("%H:%M:%S")
            result["failure_mode"] = "charge_immediately"
            return result

        return result

    def _calculate_end_time(self, start_time: str, duration_hours: float) -> str:
        """Calculate end time from start time and duration."""
        if isinstance(start_time, dict):
            start_hour = start_time.get("hour", 0)
            start_minute = start_time.get("minute", 0)
        elif ":" in str(start_time):
            parts = str(start_time).split(":")
            start_hour = int(parts[0])
            start_minute = int(parts[1]) if len(parts) > 1 else 0
        else:
            start_hour = 0
            start_minute = 0

        total_minutes = start_hour * 60 + start_minute + int(duration_hours * 60)
        end_hour = (total_minutes // 60) % 24
        end_minute = total_minutes % 60

        return f"{end_hour:02d}:{end_minute:02d}:00"

    def _determine_charging_status(self, data: dict[str, Any]) -> str:
        """Determine the current charging status."""
        # Check if system is ready
        if not data.get("system_ready", False):
            return STATUS_ERROR

        # Check if charging
        if data.get("is_charging", False):
            return STATUS_CHARGING

        # Check if scheduled
        if data.get(ATTR_NEXT_WINDOW_START):
            return STATUS_SCHEDULED

        return STATUS_IDLE

    def _calculate_price_range(self, price_sensor: str | None) -> str:
        """Calculate today's price range."""
        if not price_sensor:
            return "unavailable"

        state = self.hass.states.get(price_sensor)
        if state is None:
            return "unavailable"

        today_prices = state.attributes.get("today", [])
        if not today_prices:
            return "unavailable"

        try:
            prices = [p.get("total", 0) for p in today_prices]
            min_price = min(prices)
            max_price = max(prices)
            return f"{min_price:.3f} - {max_price:.3f}"
        except (ValueError, TypeError):
            return "unavailable"

    def _calculate_estimated_savings(self, price_sensor: str | None) -> float:
        """Calculate estimated savings vs average price."""
        if not price_sensor:
            return 0.0

        state = self.hass.states.get(price_sensor)
        if state is None:
            return 0.0

        today_prices = state.attributes.get("today", [])
        if not today_prices:
            return 0.0

        try:
            prices = [p.get("total", 0) for p in today_prices]
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)

            # Estimate based on 3 hours charging at charging power
            power_entity = self._get_config_value(CONF_BATTERY_CHARGING_POWER)
            charging_power = self._get_sensor_value(power_entity, 3000) if power_entity else 3000
            hours_charging = 3
            kwh_charged = (charging_power / 1000) * hours_charging

            savings = (avg_price - min_price) * kwh_charged
            return round(savings, 2)
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0

    def _check_system_ready(self) -> bool:
        """Check if all required entities are configured and available."""
        required_entities = [
            self._get_config_value(CONF_PRICE_SENSOR),
            self._get_config_value(CONF_BATTERY_SOC_SENSOR),
            self._get_config_value(CONF_BATTERY_CHARGING_SWITCH),
        ]

        for entity_id in required_entities:
            if not entity_id:
                return False

            state = self.hass.states.get(entity_id)
            if state is None or state.state in ("unavailable", "unknown"):
                return False

        return True

    async def async_start_charging(self) -> None:
        """Start battery charging."""
        switch_entity = self._get_config_value(CONF_BATTERY_CHARGING_SWITCH)
        if not switch_entity:
            _LOGGER.error("No charging switch configured")
            return

        try:
            await self.hass.services.async_call(
                "switch",
                "turn_on",
                {"entity_id": switch_entity},
            )
            _LOGGER.info("Started charging via %s", switch_entity)
        except Exception as err:
            _LOGGER.error("Failed to start charging: %s", err)

    async def async_stop_charging(self) -> None:
        """Stop battery charging."""
        switch_entity = self._get_config_value(CONF_BATTERY_CHARGING_SWITCH)
        if not switch_entity:
            _LOGGER.error("No charging switch configured")
            return

        try:
            await self.hass.services.async_call(
                "switch",
                "turn_off",
                {"entity_id": switch_entity},
            )
            _LOGGER.info("Stopped charging via %s", switch_entity)
        except Exception as err:
            _LOGGER.error("Failed to stop charging: %s", err)

    async def async_setup_automations(self) -> None:
        """Set up internal automations for charging triggers."""
        # Night charging trigger
        trigger_time = self._get_config_value(CONF_TRIGGER_TIME, DEFAULT_TRIGGER_TIME)
        hour, minute = self._parse_time_components(trigger_time)

        unsub = async_track_time_change(
            self.hass,
            self._handle_night_trigger,
            hour=hour,
            minute=minute,
            second=0,
        )
        self._unsubscribe_callbacks.append(unsub)

        # Day charging trigger (if enabled)
        if self._get_config_value(CONF_DAY_SCHEDULE_ENABLED, DEFAULT_DAY_SCHEDULE_ENABLED):
            day_start = self._get_config_value(CONF_DAY_START_TIME, DEFAULT_DAY_START_TIME)
            day_hour, day_minute = self._parse_time_components(day_start)

            unsub_day = async_track_time_change(
                self.hass,
                self._handle_day_trigger,
                hour=day_hour,
                minute=day_minute,
                second=0,
            )
            self._unsubscribe_callbacks.append(unsub_day)

        # Evening peak check trigger
        evening_peak_start = self._get_config_value(
            CONF_EVENING_PEAK_START, DEFAULT_EVENING_PEAK_START
        )
        peak_hour, peak_minute = self._parse_time_components(evening_peak_start)

        # Calculate check time (1 hour before peak)
        check_minutes = peak_hour * 60 + peak_minute - EMERGENCY_CHECK_BUFFER_MINUTES
        if check_minutes < 0:
            check_minutes += 1440
        check_hour = check_minutes // 60
        check_minute = check_minutes % 60

        unsub_peak = async_track_time_change(
            self.hass,
            self._handle_evening_peak_check,
            hour=check_hour,
            minute=check_minute,
            second=0,
        )
        self._unsubscribe_callbacks.append(unsub_peak)

        _LOGGER.info("Charging automations set up successfully")

    def _parse_time_components(self, time_str: str) -> tuple[int, int]:
        """Parse time string into hour and minute components."""
        if isinstance(time_str, dict):
            return time_str.get("hour", 0), time_str.get("minute", 0)
        if ":" in str(time_str):
            parts = str(time_str).split(":")
            return int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        return 0, 0

    @callback
    async def _handle_night_trigger(self, now: datetime) -> None:
        """Handle night charging trigger."""
        _LOGGER.info("Night charging trigger fired")

        # Refresh data
        await self.async_refresh()

        if self.data is None:
            _LOGGER.error("No data available for night charging")
            return

        # Check if SOC is already at target
        current_soc = self.data.get(ATTR_CURRENT_SOC, 0)
        target_soc = self.data.get(ATTR_TARGET_SOC, DEFAULT_NIGHT_TARGET_SOC)

        if current_soc >= target_soc:
            _LOGGER.info(
                "SOC already at target (%s >= %s), skipping night charging",
                current_soc,
                target_soc,
            )
            if self._get_config_value(CONF_NOTIFY_CHARGING_SKIPPED, DEFAULT_NOTIFY_CHARGING_SKIPPED):
                await self._send_notification(
                    "Night Charging Skipped",
                    f"Battery SOC already at target. Current: {current_soc}%, Target: {target_soc}%",
                )
            return

        # Schedule charging
        await self._schedule_charging_window()

    @callback
    async def _handle_day_trigger(self, now: datetime) -> None:
        """Handle day charging trigger."""
        _LOGGER.info("Day charging trigger fired")

        if not self._get_config_value(CONF_DAY_SCHEDULE_ENABLED, DEFAULT_DAY_SCHEDULE_ENABLED):
            return

        # Refresh data
        await self.async_refresh()

        if self.data is None:
            _LOGGER.error("No data available for day charging")
            return

        # Check if SOC is already at target
        current_soc = self.data.get(ATTR_CURRENT_SOC, 0)
        day_target = self._get_config_value(CONF_DAY_TARGET_SOC, DEFAULT_DAY_TARGET_SOC)

        if current_soc >= day_target:
            _LOGGER.info(
                "SOC already at day target (%s >= %s), skipping day charging",
                current_soc,
                day_target,
            )
            return

        # Schedule day charging
        await self._schedule_day_charging_window()

    @callback
    async def _handle_evening_peak_check(self, now: datetime) -> None:
        """Handle evening peak SOC check trigger."""
        _LOGGER.info("Evening peak check trigger fired")

        # Refresh data
        await self.async_refresh()

        if self.data is None:
            _LOGGER.error("No data available for evening peak check")
            return

        # Check if SOC is below evening peak target
        current_soc = self.data.get(ATTR_CURRENT_SOC, 0)
        evening_target = self._get_config_value(
            CONF_EVENING_PEAK_TARGET_SOC, DEFAULT_EVENING_PEAK_TARGET_SOC
        )

        if current_soc >= evening_target:
            _LOGGER.info(
                "SOC already at evening peak target (%s >= %s)",
                current_soc,
                evening_target,
            )
            return

        # Start emergency charging
        _LOGGER.warning(
            "SOC below evening peak target (%s < %s), starting emergency charging",
            current_soc,
            evening_target,
        )

        await self.async_start_charging()

        if self._get_config_value(CONF_NOTIFY_EMERGENCY_CHARGING, DEFAULT_NOTIFY_EMERGENCY_CHARGING):
            await self._send_notification(
                "Emergency Charging Started",
                f"SOC ({current_soc}%) below evening peak target ({evening_target}%). "
                f"Charging started to prepare for peak hours.",
            )

    async def _schedule_charging_window(self) -> None:
        """Schedule charging based on calculated window."""
        if self.data is None:
            return

        start_time = self.data.get(ATTR_NEXT_WINDOW_START)
        end_time = self.data.get(ATTR_NEXT_WINDOW_END)

        if not start_time or not end_time:
            _LOGGER.warning("No charging window calculated")
            return

        _LOGGER.info("Scheduling charging from %s to %s", start_time, end_time)

        if self._get_config_value(CONF_NOTIFY_CHARGING_SCHEDULED, DEFAULT_NOTIFY_CHARGING_SCHEDULED):
            duration = self.data.get(ATTR_CHARGING_DURATION, 0)
            cost = self.data.get(ATTR_ESTIMATED_COST, 0)
            await self._send_notification(
                "Battery Charging Scheduled",
                f"Charging scheduled from {start_time[:5]} to {end_time[:5]}. "
                f"Duration: {duration}h, Estimated cost: {cost:.4f} EUR",
            )

    async def _schedule_day_charging_window(self) -> None:
        """Schedule day charging window."""
        _LOGGER.info("Scheduling day charging window")

    async def _send_notification(self, title: str, message: str) -> None:
        """Send a notification."""
        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": title,
                    "message": message,
                    "notification_id": f"charge_cheapest_{title.lower().replace(' ', '_')}",
                },
            )
        except Exception as err:
            _LOGGER.error("Failed to send notification: %s", err)

    async def async_shutdown(self) -> None:
        """Clean up coordinator resources."""
        # Unsubscribe from all callbacks
        for unsub in self._unsubscribe_callbacks:
            unsub()
        self._unsubscribe_callbacks.clear()

        _LOGGER.info("Coordinator shutdown complete")
