"""
Blueprint Foundation Tests

Tests for Task Group 1: Blueprint Metadata and Structure
Validates YAML syntax, required metadata fields, and input section structure.
"""

import re


class TestBlueprintFoundation:
    def test_blueprint_yaml_parses_without_errors(self, blueprint):
        """Blueprint YAML parses without errors."""
        assert blueprint is not None

    def test_required_metadata_fields_are_present(self, blueprint):
        """Required metadata fields are present."""
        assert "blueprint" in blueprint
        assert "name" in blueprint["blueprint"]
        assert isinstance(blueprint["blueprint"]["name"], str)
        assert "description" in blueprint["blueprint"]
        assert isinstance(blueprint["blueprint"]["description"], str)
        assert blueprint["blueprint"]["domain"] == "automation"

    def test_input_section_exists_with_expected_structure(self, blueprint):
        """Input section exists with expected structure."""
        assert "input" in blueprint["blueprint"]
        assert isinstance(blueprint["blueprint"]["input"], dict)

    def test_source_url_is_provided_for_sharing(self, blueprint):
        """Source URL is provided for sharing."""
        assert "source_url" in blueprint["blueprint"]
        assert isinstance(blueprint["blueprint"]["source_url"], str)
        assert re.match(r"^https?://", blueprint["blueprint"]["source_url"])
