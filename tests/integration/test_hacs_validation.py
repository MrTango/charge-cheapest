"""Tests for HACS validation requirements."""

from __future__ import annotations

import json
import os
import pytest
import sys
import re

# Add custom_components to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestHacsValidation:
    """Test HACS validation requirements."""

    def test_manifest_has_all_required_fields(self):
        """Test that manifest.json has all HACS-required fields."""
        manifest_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/manifest.json",
        )

        with open(manifest_path) as f:
            manifest = json.load(f)

        # Required HACS fields
        required_fields = [
            "domain",
            "name",
            "version",
            "documentation",
            "codeowners",
            "dependencies",
            "iot_class",
        ]

        for field in required_fields:
            assert field in manifest, f"Missing required field: {field}"

        # Check specific values
        assert manifest["domain"] == "tibber_cheapest_charging"
        assert manifest["iot_class"] == "cloud_polling"
        assert "tibber" in manifest["dependencies"]

    def test_hacs_json_points_to_correct_path(self):
        """Test that hacs.json has correct content path."""
        hacs_path = os.path.join(
            os.path.dirname(__file__),
            "../../hacs.json",
        )

        with open(hacs_path) as f:
            hacs_config = json.load(f)

        # content_in_root should be false for custom_components structure
        assert hacs_config.get("content_in_root") is False

        # homeassistant minimum version should match manifest
        manifest_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/manifest.json",
        )

        with open(manifest_path) as f:
            manifest = json.load(f)

        if "homeassistant" in hacs_config and "homeassistant" in manifest:
            assert hacs_config["homeassistant"] == manifest["homeassistant"]

    def test_integration_version_format_is_valid(self):
        """Test that integration version format is valid semver."""
        manifest_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/manifest.json",
        )

        with open(manifest_path) as f:
            manifest = json.load(f)

        version = manifest.get("version", "")

        # Basic semver format check: X.Y.Z
        parts = version.split(".")
        assert len(parts) == 3, f"Version should be semver format: {version}"

        for part in parts:
            assert part.isdigit(), f"Version parts should be numeric: {version}"

    def test_manifest_has_config_flow_enabled(self):
        """Test that manifest has config_flow enabled."""
        manifest_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/manifest.json",
        )

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert manifest.get("config_flow") is True

    def test_translations_file_exists_and_valid(self):
        """Test that translations file exists and is valid JSON."""
        translations_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/translations/en.json",
        )

        assert os.path.exists(translations_path)

        with open(translations_path) as f:
            translations = json.load(f)

        # Check required translation sections
        assert "config" in translations
        assert "options" in translations

        # Check config flow steps
        assert "step" in translations["config"]
        assert "user" in translations["config"]["step"]
        assert "optional_entities" in translations["config"]["step"]
        assert "schedule" in translations["config"]["step"]


class TestIntegrationStructure:
    """Test integration directory structure."""

    def test_all_required_files_exist(self):
        """Test that all required integration files exist."""
        base_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging",
        )

        required_files = [
            "__init__.py",
            "manifest.json",
            "config_flow.py",
            "coordinator.py",
            "const.py",
            "sensor.py",
            "binary_sensor.py",
            "dashboard.py",
            "services.yaml",
            "translations/en.json",
        ]

        for filename in required_files:
            filepath = os.path.join(base_path, filename)
            assert os.path.exists(filepath), f"Missing file: {filename}"

    def test_const_defines_domain(self):
        """Test that const.py defines DOMAIN correctly by parsing file content."""
        const_path = os.path.join(
            os.path.dirname(__file__),
            "../../custom_components/tibber_cheapest_charging/const.py",
        )

        with open(const_path) as f:
            content = f.read()

        # Check DOMAIN is defined with correct value
        assert 'DOMAIN' in content
        assert 'tibber_cheapest_charging' in content

        # Verify the actual DOMAIN assignment - look for DOMAIN: Final = "value"
        domain_match = re.search(r'DOMAIN:\s*Final\s*=\s*"([^"]+)"', content)
        assert domain_match is not None, "DOMAIN definition not found in const.py"
        assert domain_match.group(1) == "tibber_cheapest_charging"
