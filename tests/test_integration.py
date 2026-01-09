"""
Integration Tests

Tests for Task Group 7: Test Review and Integration Validation
Validates complete blueprint schema and input dependencies.
"""


class TestBlueprintSchemaIntegration:
    def test_complete_blueprint_schema_is_valid_home_assistant_structure(self, blueprint, blueprint_inputs):
        """Complete blueprint schema is valid Home Assistant structure."""
        # Verify top-level structure
        assert "blueprint" in blueprint
        assert blueprint["blueprint"]["name"] == "Charge Cheapest"
        assert blueprint["blueprint"]["domain"] == "automation"
        assert "input" in blueprint["blueprint"]

        # Verify all 12 expected inputs are present
        expected_inputs = [
            "night_start_time",
            "night_end_time",
            "night_target_soc",
            "day_schedule_enabled",
            "day_start_time",
            "day_end_time",
            "day_target_soc",
            "evening_peak_start",
            "evening_peak_end",
            "price_sensor",
            "battery_charging_switch",
            "battery_charging_power",
        ]

        for input_name in expected_inputs:
            assert input_name in blueprint_inputs

    def test_all_inputs_with_defaults_have_required_defaults_per_spec(self, blueprint_inputs):
        """All inputs with defaults have required defaults per spec."""
        expected_defaults = {
            "night_start_time": "23:00:00",
            "night_end_time": "06:00:00",
            "night_target_soc": 60,
            "day_schedule_enabled": False,
            "day_start_time": "09:00:00",
            "day_end_time": "16:00:00",
            "day_target_soc": 50,
            "evening_peak_start": "17:00:00",
            "evening_peak_end": "21:00:00",
        }

        for input_name, expected_default in expected_defaults.items():
            assert blueprint_inputs[input_name]["default"] == expected_default

    def test_all_required_entity_inputs_do_not_have_defaults(self, blueprint_inputs):
        """All required entity inputs do not have defaults."""
        required_entity_inputs = [
            "price_sensor",
            "battery_charging_switch",
            "battery_charging_power",
        ]

        for input_name in required_entity_inputs:
            assert input_name in blueprint_inputs
            assert blueprint_inputs[input_name].get("default") is None

    def test_all_inputs_have_name_and_description(self, blueprint_inputs):
        """All inputs have name and description."""
        for input_name, input_config in blueprint_inputs.items():
            assert "name" in input_config, f"{input_name} missing name"
            assert isinstance(input_config["name"], str)
            assert "description" in input_config, f"{input_name} missing description"
            assert isinstance(input_config["description"], str)

    def test_soc_sliders_have_consistent_configuration(self, blueprint_inputs):
        """SOC sliders have consistent configuration."""
        soc_inputs = ["night_target_soc", "day_target_soc"]

        for input_name in soc_inputs:
            number_config = blueprint_inputs[input_name]["selector"]["number"]
            assert number_config["min"] == 0
            assert number_config["max"] == 100
            assert number_config["step"] == 5
            assert number_config["unit_of_measurement"] == "%"
            assert number_config["mode"] == "slider"
