"""
Internal Configuration Tests

Tests for Task Group 6: Macro Defaults and Documentation
Validates that hardcoded macro parameters are documented and not exposed as inputs.
"""


class TestInternalConfiguration:
    def test_blueprint_has_comments_documenting_hardcoded_macro_parameters(self, blueprint_raw):
        """Blueprint has comments documenting hardcoded macro parameters."""
        raw_content = blueprint_raw
        assert "attr_today: 'today'" in raw_content
        assert "attr_tomorrow: 'tomorrow'" in raw_content
        assert "value_key: 'total'" in raw_content
        assert "datetime_in_data: false" in raw_content
        assert "mode: 'start', 'end', 'list'" in raw_content

    def test_no_inputs_exist_for_advanced_macro_parameters(self, blueprint_inputs):
        """No inputs exist for advanced macro parameters."""
        inputs = blueprint_inputs
        # These should NOT be exposed as user inputs
        assert "attr_today" not in inputs
        assert "attr_tomorrow" not in inputs
        assert "value_key" not in inputs
        assert "datetime_in_data" not in inputs
        assert "mode" not in inputs
        assert "look_ahead" not in inputs
        assert "weight" not in inputs
        assert "price_tolerance" not in inputs

    def test_prerequisite_documentation_is_present_for_cheapest_energy_hours_macro(self, blueprint_raw):
        """Prerequisite documentation is present for cheapest-energy-hours macro."""
        raw_content = blueprint_raw
        assert "cheapest-energy-hours" in raw_content
        assert "HACS" in raw_content
        assert "custom_templates" in raw_content
        assert "Prerequisites" in raw_content
