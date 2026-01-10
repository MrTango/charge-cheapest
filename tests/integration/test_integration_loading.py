"""Tests for Tibber Cheapest Charging integration loading."""

from __future__ import annotations

import json
import os
import pytest
import sys

# Add custom_components to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestIntegrationFiles:
    """Test integration file structure and content."""

    def test_init_py_exists(self):
        """Test that __init__.py exists."""
        init_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/__init__.py",
        )

        assert os.path.exists(init_path)

    def test_init_py_has_async_setup(self):
        """Test that __init__.py defines async_setup function."""
        init_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/__init__.py",
        )

        with open(init_path) as f:
            content = f.read()

        assert "async def async_setup" in content

    def test_init_py_has_async_setup_entry(self):
        """Test that __init__.py defines async_setup_entry function."""
        init_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/__init__.py",
        )

        with open(init_path) as f:
            content = f.read()

        assert "async def async_setup_entry" in content

    def test_init_py_has_async_unload_entry(self):
        """Test that __init__.py defines async_unload_entry function."""
        init_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/__init__.py",
        )

        with open(init_path) as f:
            content = f.read()

        assert "async def async_unload_entry" in content

    def test_init_py_defines_platforms(self):
        """Test that __init__.py defines PLATFORMS list."""
        init_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/__init__.py",
        )

        with open(init_path) as f:
            content = f.read()

        assert "PLATFORMS" in content
        assert "Platform.SENSOR" in content
        assert "Platform.BINARY_SENSOR" in content


class TestManifest:
    """Test manifest.json content."""

    def test_manifest_has_tibber_dependency(self):
        """Test that manifest lists tibber as dependency."""
        manifest_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/manifest.json",
        )

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "tibber" in manifest.get("dependencies", [])

    def test_manifest_has_correct_domain(self):
        """Test that manifest has correct domain."""
        manifest_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/manifest.json",
        )

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert manifest.get("domain") == "tibber_cheapest_charging"

    def test_manifest_has_correct_iot_class(self):
        """Test that manifest has correct iot_class."""
        manifest_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/manifest.json",
        )

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert manifest.get("iot_class") == "cloud_polling"


class TestTibberValidation:
    """Test Tibber integration validation logic."""

    def test_tibber_validation_logic(self):
        """Test Tibber integration validation returns correct results."""
        # Inline validation logic for testing
        def _check_tibber_configured(components: set, tibber_entities: list) -> bool:
            if "tibber" in components:
                return True
            return len(tibber_entities) > 0

        # Tibber in components
        assert _check_tibber_configured({"tibber", "sensor"}, []) is True

        # Tibber entities exist
        assert _check_tibber_configured(set(), ["sensor.tibber_price"]) is True

        # Neither present
        assert _check_tibber_configured(set(), []) is False


class TestDependencyValidation:
    """Test external dependency validation."""

    def test_cheapest_energy_macro_check(self):
        """Test cheapest-energy-hours macro validation logic."""
        # Inline check logic for testing
        def _check_macro_exists(custom_templates_path: str, templates_path: str) -> bool:
            import os

            macro_file1 = os.path.join(custom_templates_path, "cheapest_energy_hours.jinja")
            macro_file2 = os.path.join(templates_path, "cheapest_energy_hours.jinja")

            return os.path.exists(macro_file1) or os.path.exists(macro_file2)

        # Test with non-existent paths
        result = _check_macro_exists("/nonexistent/path1", "/nonexistent/path2")
        assert result is False
