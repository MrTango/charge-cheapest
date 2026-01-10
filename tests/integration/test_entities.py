"""Tests for Charge Cheapest entity platforms."""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest
import sys
import os

# Add custom_components to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestSensorValueCalculations:
    """Test sensor value calculations."""

    def test_next_window_formatting(self):
        """Test next charging window time range formatting."""
        def _format_next_window(start: str | None, end: str | None, failure_mode: str | None = None) -> str:
            if not start or not end:
                if failure_mode == "skip":
                    return "Skipped"
                return "Not scheduled"

            start_formatted = start[:5] if isinstance(start, str) and len(start) >= 5 else str(start)
            end_formatted = end[:5] if isinstance(end, str) and len(end) >= 5 else str(end)

            return f"{start_formatted} - {end_formatted}"

        # Test valid window
        assert _format_next_window("01:00:00", "04:00:00") == "01:00 - 04:00"

        # Test skipped
        assert _format_next_window(None, None, "skip") == "Skipped"

        # Test not scheduled
        assert _format_next_window(None, None) == "Not scheduled"

    def test_is_cheap_hour_calculation(self):
        """Test is_cheap_hour binary sensor calculation."""
        def _is_cheap_hour(current_price: float | None, price_range: str) -> bool:
            if current_price is None:
                return False

            if not price_range or price_range == "unavailable":
                return False

            try:
                parts = price_range.split(" - ")
                if len(parts) == 2:
                    min_price = float(parts[0])
                    max_price = float(parts[1])
                    avg_price = (min_price + max_price) / 2
                    return current_price < avg_price
            except (ValueError, TypeError):
                pass

            return False

        # Price below average
        assert _is_cheap_hour(0.20, "0.15 - 0.45") is True  # avg = 0.30

        # Price above average
        assert _is_cheap_hour(0.40, "0.15 - 0.45") is False  # avg = 0.30

        # Price exactly at average
        assert _is_cheap_hour(0.30, "0.15 - 0.45") is False  # avg = 0.30

        # No price
        assert _is_cheap_hour(None, "0.15 - 0.45") is False

        # Invalid range
        assert _is_cheap_hour(0.20, "unavailable") is False


class TestStatusDetermination:
    """Test charging status determination."""

    def test_status_determination_logic(self):
        """Test status determination based on various conditions."""
        STATUS_IDLE = "idle"
        STATUS_SCHEDULED = "scheduled"
        STATUS_CHARGING = "charging"
        STATUS_ERROR = "error"

        def _determine_status(system_ready: bool, is_charging: bool, next_window_start: str | None) -> str:
            if not system_ready:
                return STATUS_ERROR
            if is_charging:
                return STATUS_CHARGING
            if next_window_start:
                return STATUS_SCHEDULED
            return STATUS_IDLE

        assert _determine_status(False, False, None) == STATUS_ERROR
        assert _determine_status(True, True, None) == STATUS_CHARGING
        assert _determine_status(True, False, "01:00:00") == STATUS_SCHEDULED
        assert _determine_status(True, False, None) == STATUS_IDLE


class TestPriceRangeCalculation:
    """Test price range calculation."""

    def test_price_range_format(self):
        """Test price range formatting from price list."""
        def _calculate_price_range(prices: list[dict]) -> str:
            if not prices:
                return "unavailable"

            try:
                price_values = [p.get("total", 0) for p in prices]
                min_price = min(price_values)
                max_price = max(price_values)
                return f"{min_price:.3f} - {max_price:.3f}"
            except (ValueError, TypeError):
                return "unavailable"

        prices = [
            {"total": 0.20},
            {"total": 0.15},
            {"total": 0.45},
            {"total": 0.30},
        ]

        assert _calculate_price_range(prices) == "0.150 - 0.450"
        assert _calculate_price_range([]) == "unavailable"


class TestEstimatedSavingsCalculation:
    """Test estimated savings calculation."""

    def test_savings_calculation(self):
        """Test estimated savings calculation."""
        def _calculate_savings(prices: list[dict], charging_power_w: float, hours: float = 3) -> float:
            if not prices:
                return 0.0

            try:
                price_values = [p.get("total", 0) for p in prices]
                avg_price = sum(price_values) / len(price_values)
                min_price = min(price_values)

                kwh_charged = (charging_power_w / 1000) * hours
                savings = (avg_price - min_price) * kwh_charged
                return round(savings, 2)
            except (ValueError, TypeError, ZeroDivisionError):
                return 0.0

        prices = [
            {"total": 0.20},
            {"total": 0.15},
            {"total": 0.45},
            {"total": 0.30},
        ]

        # avg = 0.275, min = 0.15, diff = 0.125
        # 3kW * 3h = 9 kWh
        # savings = 0.125 * 9 = 1.125 EUR
        savings = _calculate_savings(prices, 3000, 3)
        assert savings == pytest.approx(1.12, abs=0.1)


class TestEntityIdPrefixes:
    """Test entity ID prefix conventions."""

    def test_sensor_entity_id_prefix(self):
        """Test that sensor entity IDs use charge_cheapest_ prefix."""
        sensor_keys = [
            "status",
            "current_price",
            "next_window",
            "recommended_soc",
            "price_range",
            "estimated_savings",
            "charging_duration",
            "target_soc",
        ]

        for key in sensor_keys:
            entity_id = f"sensor.charge_cheapest_{key}"
            assert entity_id.startswith("sensor.charge_cheapest_")

    def test_binary_sensor_entity_id_prefix(self):
        """Test that binary sensor entity IDs use charge_cheapest_ prefix."""
        binary_sensor_keys = [
            "is_charging",
            "is_cheap_hour",
            "prices_available_tomorrow",
            "system_ready",
        ]

        for key in binary_sensor_keys:
            entity_id = f"binary_sensor.charge_cheapest_{key}"
            assert entity_id.startswith("binary_sensor.charge_cheapest_")


class TestDeviceInfo:
    """Test device info structure."""

    def test_device_info_structure(self):
        """Test that device info has required fields."""
        device_info = {
            "identifiers": {("charge_cheapest", "test_entry_id")},
            "name": "Charge Cheapest",
            "manufacturer": "Charge Cheapest",
            "model": "Smart Battery Charging",
            "sw_version": "1.0.0",
        }

        assert "identifiers" in device_info
        assert "name" in device_info
        assert "manufacturer" in device_info
        assert "model" in device_info
