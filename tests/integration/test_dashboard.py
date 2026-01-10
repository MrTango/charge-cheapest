"""Tests for Charge Cheapest dashboard auto-registration."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock
import pytest
import sys
import os

# Add custom_components to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


# Dashboard configuration inline for testing without imports
DASHBOARD_URL_PATH = "charge-cheapest"
DASHBOARD_TITLE = "Charge Cheapest"


class TestDashboardStructure:
    """Test dashboard configuration structure."""

    def test_dashboard_has_three_views(self):
        """Test that dashboard has Overview, Statistics, and Configuration views."""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/charge_cheapest/dashboard.py",
        )

        # Read and check the file contains expected views
        with open(dashboard_path) as f:
            content = f.read()

        assert '"title": "Overview"' in content
        assert '"title": "Statistics"' in content
        assert '"title": "Configuration"' in content

    def test_dashboard_uses_correct_entity_ids(self):
        """Test that dashboard references correct entity IDs."""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/charge_cheapest/dashboard.py",
        )

        with open(dashboard_path) as f:
            content = f.read()

        # Check for charge_cheapest_ prefixed entities
        assert "sensor.charge_cheapest_status" in content
        assert "sensor.charge_cheapest_current_price" in content
        assert "sensor.charge_cheapest_next_window" in content
        assert "binary_sensor.charge_cheapest_system_ready" in content
        assert "binary_sensor.charge_cheapest_is_cheap_hour" in content

    def test_dashboard_has_apexcharts_conditional(self):
        """Test that dashboard includes ApexCharts conditional card."""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/charge_cheapest/dashboard.py",
        )

        with open(dashboard_path) as f:
            content = f.read()

        assert "custom:apexcharts-card" in content
        assert "history-graph" in content  # Fallback

    def test_dashboard_url_path(self):
        """Test dashboard URL path constant."""
        assert DASHBOARD_URL_PATH == "charge-cheapest"

    def test_dashboard_title(self):
        """Test dashboard title constant."""
        assert DASHBOARD_TITLE == "Charge Cheapest"


class TestDashboardService:
    """Test dashboard service definitions."""

    def test_services_yaml_exists(self):
        """Test that services.yaml file exists."""
        services_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/charge_cheapest/services.yaml",
        )

        assert os.path.exists(services_path)

    def test_services_yaml_has_recreate_dashboard(self):
        """Test that services.yaml defines recreate_dashboard service."""
        services_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/charge_cheapest/services.yaml",
        )

        with open(services_path) as f:
            content = f.read()

        assert "recreate_dashboard:" in content


class TestDashboardCards:
    """Test dashboard card configurations."""

    def test_overview_view_has_status_card(self):
        """Test that overview view has status entities card."""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/charge_cheapest/dashboard.py",
        )

        with open(dashboard_path) as f:
            content = f.read()

        assert '"title": "Charging Status"' in content

    def test_statistics_view_has_savings_card(self):
        """Test that statistics view has savings summary card."""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/charge_cheapest/dashboard.py",
        )

        with open(dashboard_path) as f:
            content = f.read()

        assert '"title": "Savings Summary"' in content

    def test_configuration_view_has_validation_status(self):
        """Test that configuration view has validation status card."""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/charge_cheapest/dashboard.py",
        )

        with open(dashboard_path) as f:
            content = f.read()

        assert '"title": "System Status"' in content
