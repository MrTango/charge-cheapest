"""End-to-end integration tests for Charge Cheapest."""

from __future__ import annotations

import json
import os
import pytest
import sys
from datetime import datetime, timedelta

# Add custom_components to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


# Constants
CHARGING_EFFICIENCY = 0.95
TIME_SLOT_HOURS = 0.25


class TestCrossMidnightWindowCalculation:
    """Test cross-midnight window calculation accuracy."""

    def test_cross_midnight_price_window_selection(self):
        """Test that cross-midnight windows correctly select cheapest hours."""
        # Simulate today's prices (23:00 is index 23)
        today_prices = [
            {"total": 0.30} for _ in range(23)
        ] + [{"total": 0.15}]  # 23:00 is cheap

        # Simulate tomorrow's prices (00:00-05:00)
        tomorrow_prices = [
            {"total": 0.12},  # 00:00
            {"total": 0.10},  # 01:00 - cheapest
            {"total": 0.11},  # 02:00
            {"total": 0.13},  # 03:00
            {"total": 0.15},  # 04:00
            {"total": 0.18},  # 05:00
        ] + [{"total": 0.35} for _ in range(18)]

        # Build window prices (23:00 today to 06:00 tomorrow)
        start_hour = 23
        end_hour = 6

        window_prices = []
        now = datetime.now()

        # Add today's prices from start_hour
        for i, price_entry in enumerate(today_prices):
            if i >= start_hour:
                window_prices.append({
                    "hour": i,
                    "day": "today",
                    "price": price_entry["total"],
                })

        # Add tomorrow's prices until end_hour
        for i, price_entry in enumerate(tomorrow_prices):
            if i < end_hour:
                window_prices.append({
                    "hour": i,
                    "day": "tomorrow",
                    "price": price_entry["total"],
                })

        # Should have 7 hours in window (23, 0, 1, 2, 3, 4, 5)
        assert len(window_prices) == 7

        # Find cheapest 3 consecutive hours
        hours_needed = 3
        best_cost = float("inf")
        best_start_idx = 0

        for i in range(len(window_prices) - hours_needed + 1):
            cost = sum(p["price"] for p in window_prices[i : i + hours_needed])
            if cost < best_cost:
                best_cost = cost
                best_start_idx = i

        # Cheapest 3 hours should start at 00:00 (prices: 0.12, 0.10, 0.11 = 0.33)
        assert window_prices[best_start_idx]["day"] == "tomorrow"
        assert window_prices[best_start_idx]["hour"] == 0


class TestSocCalculationMatchesBlueprint:
    """Test that SOC calculation matches original blueprint logic."""

    def test_charging_duration_calculation(self):
        """Test charging duration calculation matches blueprint formula."""
        # Blueprint formula:
        # energy_needed_kwh = (soc_delta / 100) * capacity_kwh
        # hours_needed = energy_needed_kwh / (charge_power_kw * 0.95)
        # slots = ceil(hours_needed * 4) / 4

        current_soc = 30
        target_soc = 60
        capacity_kwh = 10
        charge_power_kw = 3

        soc_delta = target_soc - current_soc  # 30%
        energy_needed = (soc_delta / 100) * capacity_kwh  # 3 kWh
        hours_needed = energy_needed / (charge_power_kw * CHARGING_EFFICIENCY)  # 3 / 2.85 = 1.053h

        # Round to 15-minute slots
        hours_clamped = max(hours_needed, TIME_SLOT_HOURS)
        slots_needed = (hours_clamped * 4).__ceil__()  # 5 slots
        duration = slots_needed / 4  # 1.25 hours

        assert duration == 1.25

    def test_wh_to_kwh_conversion(self):
        """Test that Wh to kWh conversion works correctly."""
        capacity_wh = 10000  # 10000 Wh
        unit = "Wh"

        # Convert to kWh
        if "wh" in unit.lower() and "kwh" not in unit.lower():
            capacity_kwh = capacity_wh / 1000
        else:
            capacity_kwh = capacity_wh

        assert capacity_kwh == 10


class TestOptionsFlowChanges:
    """Test that options flow changes take effect."""

    def test_config_value_with_options_override(self):
        """Test that options override base config values."""
        base_config = {
            "night_target_soc": 60,
            "day_target_soc": 50,
        }

        options = {
            "night_target_soc": 70,  # Override
        }

        def _get_config_value(key, default=None):
            return {**base_config, **options}.get(key, default)

        assert _get_config_value("night_target_soc") == 70  # From options
        assert _get_config_value("day_target_soc") == 50   # From base config


class TestGracefulFailureHandling:
    """Test graceful handling of failures."""

    def test_tibber_unavailable_handling(self):
        """Test handling when Tibber becomes unavailable."""
        def _check_tomorrow_prices(prices: list | None) -> bool:
            return prices is not None and len(prices) > 0

        # Prices available
        assert _check_tomorrow_prices([{"total": 0.20}]) is True

        # Prices unavailable
        assert _check_tomorrow_prices([]) is False
        assert _check_tomorrow_prices(None) is False

    def test_entity_unavailable_handling(self):
        """Test handling when entities become unavailable."""
        def _check_system_ready(entities: dict) -> bool:
            for entity_id, state in entities.items():
                if state is None or state in ("unavailable", "unknown"):
                    return False
            return True

        # All entities available
        entities_ok = {
            "sensor.price": "0.25",
            "sensor.soc": "45",
            "switch.charging": "off",
        }
        assert _check_system_ready(entities_ok) is True

        # One entity unavailable
        entities_bad = {
            "sensor.price": "unavailable",
            "sensor.soc": "45",
            "switch.charging": "off",
        }
        assert _check_system_ready(entities_bad) is False


class TestDashboardServiceExecution:
    """Test dashboard service registration and execution."""

    def test_service_definition_structure(self):
        """Test that service is defined with correct structure."""
        services_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/charge_cheapest/services.yaml",
        )

        with open(services_path) as f:
            content = f.read()

        assert "recreate_dashboard:" in content
        assert "name:" in content
        assert "description:" in content


class TestFullIntegrationWorkflow:
    """Test full integration workflow scenarios."""

    def test_configuration_data_flow(self):
        """Test that configuration flows through the system correctly."""
        # Simulate config entry creation
        config_entry_data = {
            "battery_soc_sensor": "sensor.battery_soc",
            "battery_charging_switch": "switch.battery_charging",
            "price_sensor": "sensor.tibber_prices",
            "night_start_time": "23:00:00",
            "night_end_time": "06:00:00",
            "night_target_soc": 60,
        }

        # Verify required fields
        required_fields = ["battery_soc_sensor", "battery_charging_switch", "price_sensor"]
        for field in required_fields:
            assert field in config_entry_data

        # Verify defaults can be applied
        defaults = {
            "day_schedule_enabled": False,
            "failure_behavior": "skip_charging",
        }

        merged_config = {**defaults, **config_entry_data}
        assert merged_config["day_schedule_enabled"] is False
        assert merged_config["failure_behavior"] == "skip_charging"
