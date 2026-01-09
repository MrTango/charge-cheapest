"""
Forecast Mode Tests

Tests for Task Group 1: Mode Toggle and User Input Configuration
Validates forecast_mode_automatic input and user_soc_input_number selector.
"""


class TestForecastModeToggleAndUserInputConfiguration:
    def test_forecast_mode_automatic_input_exists_with_boolean_selector(self, blueprint_inputs):
        """forecast_mode_automatic input exists with boolean selector and default false (recommendation mode)."""
        inputs = blueprint_inputs
        assert "forecast_mode_automatic" in inputs
        assert "selector" in inputs["forecast_mode_automatic"]
        assert "boolean" in inputs["forecast_mode_automatic"]["selector"]
        assert inputs["forecast_mode_automatic"]["default"] is False
        assert "Forecast" in inputs["forecast_mode_automatic"]["name"]
        assert "Automatic" in inputs["forecast_mode_automatic"]["name"]

    def test_user_soc_input_number_input_exists_with_entity_selector(self, blueprint_inputs):
        """user_soc_input_number input exists with entity selector for input_number domain."""
        inputs = blueprint_inputs
        assert "user_soc_input_number" in inputs
        assert "selector" in inputs["user_soc_input_number"]
        assert "entity" in inputs["user_soc_input_number"]["selector"]
        assert inputs["user_soc_input_number"]["selector"]["entity"]["domain"] == "input_number"
        assert "name" in inputs["user_soc_input_number"]
        assert "description" in inputs["user_soc_input_number"]

    def test_variable_references_for_new_inputs_are_defined_in_variables_section(self, blueprint):
        """Variable references for new inputs are defined in variables section."""
        variables = blueprint["variables"]
        assert "forecast_mode_automatic" in variables
        assert variables["forecast_mode_automatic"].name == "forecast_mode_automatic"
        assert "user_soc_input_number" in variables
        assert variables["user_soc_input_number"].name == "user_soc_input_number"
