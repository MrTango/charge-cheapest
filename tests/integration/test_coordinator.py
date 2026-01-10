"""Tests for Tibber Cheapest Charging coordinator logic."""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest
import sys
import os
from datetime import datetime, timedelta

# Add custom_components to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


# Constants matching const.py
CHARGING_EFFICIENCY = 0.95
TIME_SLOT_HOURS = 0.25


def calculate_charging_duration(
    current_soc: float,
    target_soc: float,
    capacity_kwh: float,
    charge_power_kw: float,
    fallback: float = 3.0,
) -> float:
    """Calculate charging duration based on SOC with 95% efficiency.

    This mirrors the coordinator's _calculate_charging_duration method.
    """
    if current_soc < 0 or capacity_kwh <= 0 or charge_power_kw <= 0:
        return fallback

    soc_delta = target_soc - current_soc
    if soc_delta <= 0:
        return 0

    energy_needed_kwh = (soc_delta / 100) * capacity_kwh
    hours_needed = energy_needed_kwh / (charge_power_kw * CHARGING_EFFICIENCY)

    # Round to 15-minute slots
    hours_clamped = max(hours_needed, TIME_SLOT_HOURS)
    slots_needed = int((hours_clamped * 4).__ceil__())
    return round(slots_needed / 4, 2)


def calculate_optimal_morning_soc(
    default_target: float,
    min_floor: float,
    forecast_kwh: float,
    capacity_kwh: float,
    consumption_kwh: float,
    offset_kwh: float,
) -> float:
    """Calculate optimal morning SOC based on solar forecast.

    This mirrors the coordinator's _calculate_optimal_morning_soc method.
    """
    if forecast_kwh < 0 or capacity_kwh <= 0:
        return default_target

    excess_solar = forecast_kwh - consumption_kwh - offset_kwh
    soc_reduction = (excess_solar / capacity_kwh) * 100
    calculated_target = default_target - soc_reduction

    # Clamp between min_floor and default_target
    clamped_target = max(min_floor, min(calculated_target, default_target))
    return round(clamped_target, 1)


def handle_price_unavailable(failure_behavior: str, default_start: str, default_duration: float):
    """Handle case when price data is unavailable.

    Returns result dict with failure_mode and window times.
    """
    result = {"next_window_start": None, "next_window_end": None}

    if failure_behavior == "skip_charging":
        result["failure_mode"] = "skip"
        return result

    if failure_behavior == "use_default_window":
        result["next_window_start"] = default_start
        # Calculate end time
        parts = default_start.split(":")
        start_minutes = int(parts[0]) * 60 + int(parts[1])
        end_minutes = start_minutes + int(default_duration * 60)
        end_hour = (end_minutes // 60) % 24
        end_minute = end_minutes % 60
        result["next_window_end"] = f"{end_hour:02d}:{end_minute:02d}:00"
        result["failure_mode"] = "default_window"
        return result

    if failure_behavior == "charge_immediately":
        now = datetime.now()
        result["next_window_start"] = now.strftime("%H:%M:%S")
        result["next_window_end"] = (now + timedelta(hours=default_duration)).strftime("%H:%M:%S")
        result["failure_mode"] = "charge_immediately"
        return result

    return result


class TestChargingDurationCalculation:
    """Test SOC-based charging duration calculation."""

    def test_95_percent_efficiency_factor(self):
        """Test that charging duration uses 95% efficiency factor."""
        # 10 kWh battery, 3 kW charger
        # From 40% to 60% = 20% delta
        # Energy needed = 0.20 * 10 = 2 kWh
        # Hours needed = 2 / (3 * 0.95) = 2 / 2.85 = 0.70 hours
        # Rounded to 15-min slots = 0.75 hours

        duration = calculate_charging_duration(
            current_soc=40,
            target_soc=60,
            capacity_kwh=10,
            charge_power_kw=3,
        )

        assert duration == pytest.approx(0.75, abs=0.1)

    def test_rounds_to_15_minute_slots(self):
        """Test that duration rounds to 15-minute increments."""
        duration = calculate_charging_duration(
            current_soc=30,
            target_soc=60,
            capacity_kwh=10,
            charge_power_kw=3,
        )

        # Check it's a multiple of 0.25
        assert (duration * 4) % 1 == pytest.approx(0, abs=0.01)

    def test_returns_zero_when_soc_at_target(self):
        """Test that duration is zero when SOC already at target."""
        duration = calculate_charging_duration(
            current_soc=70,
            target_soc=60,
            capacity_kwh=10,
            charge_power_kw=3,
        )

        assert duration == 0

    def test_returns_fallback_for_invalid_inputs(self):
        """Test that fallback is returned for invalid inputs."""
        duration = calculate_charging_duration(
            current_soc=40,
            target_soc=60,
            capacity_kwh=0,  # Invalid
            charge_power_kw=3,
            fallback=3.0,
        )

        assert duration == 3.0


class TestOptimalSocCalculation:
    """Test optimal morning SOC calculation with solar forecast."""

    def test_reduces_soc_with_high_solar_forecast(self):
        """Test that SOC target is reduced with high solar forecast."""
        optimal_soc = calculate_optimal_morning_soc(
            default_target=60,
            min_floor=20,
            forecast_kwh=10,  # High solar
            capacity_kwh=10,
            consumption_kwh=3,
            offset_kwh=0,
        )

        # excess = 10 - 3 - 0 = 7 kWh
        # reduction = (7 / 10) * 100 = 70%
        # calculated = 60 - 70 = -10% -> clamped to 20%
        assert optimal_soc == 20

    def test_clamps_to_minimum_floor(self):
        """Test that SOC target is clamped to minimum floor."""
        optimal_soc = calculate_optimal_morning_soc(
            default_target=60,
            min_floor=30,
            forecast_kwh=15,  # Very high solar
            capacity_kwh=10,
            consumption_kwh=3,
            offset_kwh=0,
        )

        assert optimal_soc >= 30

    def test_returns_default_when_forecast_unavailable(self):
        """Test that default target is returned when forecast unavailable."""
        optimal_soc = calculate_optimal_morning_soc(
            default_target=60,
            min_floor=20,
            forecast_kwh=-1,  # Unavailable
            capacity_kwh=10,
            consumption_kwh=3,
            offset_kwh=0,
        )

        assert optimal_soc == 60


class TestFailureBehaviors:
    """Test failure behavior handling."""

    def test_skip_charging_behavior(self):
        """Test skip_charging failure behavior."""
        result = handle_price_unavailable(
            failure_behavior="skip_charging",
            default_start="01:00:00",
            default_duration=3.0,
        )

        assert result["failure_mode"] == "skip"
        assert result["next_window_start"] is None

    def test_default_window_behavior(self):
        """Test use_default_window failure behavior."""
        result = handle_price_unavailable(
            failure_behavior="use_default_window",
            default_start="01:00:00",
            default_duration=3.0,
        )

        assert result["failure_mode"] == "default_window"
        assert result["next_window_start"] == "01:00:00"
        assert result["next_window_end"] == "04:00:00"

    def test_charge_immediately_behavior(self):
        """Test charge_immediately failure behavior."""
        result = handle_price_unavailable(
            failure_behavior="charge_immediately",
            default_start="01:00:00",
            default_duration=3.0,
        )

        assert result["failure_mode"] == "charge_immediately"
        assert result["next_window_start"] is not None
        assert result["next_window_end"] is not None


class TestCrossMidnightCalculation:
    """Test cross-midnight window calculations."""

    def test_parse_time_hour(self):
        """Test time parsing for hour extraction."""
        def _parse_time_hour(time_str: str) -> int:
            if isinstance(time_str, dict):
                return time_str.get("hour", 0)
            if ":" in str(time_str):
                return int(str(time_str).split(":")[0])
            return 0

        assert _parse_time_hour("23:00:00") == 23
        assert _parse_time_hour("06:30:00") == 6
        assert _parse_time_hour({"hour": 23, "minute": 0}) == 23

    def test_end_time_calculation(self):
        """Test end time calculation from start and duration."""
        def _calculate_end_time(start_time: str, duration_hours: float) -> str:
            parts = str(start_time).split(":")
            start_hour = int(parts[0])
            start_minute = int(parts[1]) if len(parts) > 1 else 0

            total_minutes = start_hour * 60 + start_minute + int(duration_hours * 60)
            end_hour = (total_minutes // 60) % 24
            end_minute = total_minutes % 60

            return f"{end_hour:02d}:{end_minute:02d}:00"

        assert _calculate_end_time("01:00:00", 3.0) == "04:00:00"
        assert _calculate_end_time("23:00:00", 4.0) == "03:00:00"  # Cross midnight
        assert _calculate_end_time("22:30:00", 2.5) == "01:00:00"  # Cross midnight
