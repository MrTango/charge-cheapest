"""
Recommendation Sensor Tests

Tests for Task Group 2: Template Sensor for Forecast Recommendation
Validates the recommended_soc_value and recommended_soc_attributes variables.
"""


class TestRecommendationSensorVariables:
    def test_recommended_soc_value_variable_is_defined_for_sensor_state(self, blueprint):
        """recommended_soc_value variable is defined for sensor state."""
        variables = blueprint["variables"]
        assert "recommended_soc_value" in variables
        assert isinstance(variables["recommended_soc_value"], str)
        assert "optimal_morning_soc" in variables["recommended_soc_value"]
        assert "round" in variables["recommended_soc_value"]

    def test_recommended_soc_attributes_variable_is_defined_with_required_attributes(self, blueprint):
        """recommended_soc_attributes variable is defined with required attributes."""
        variables = blueprint["variables"]
        assert "recommended_soc_attributes" in variables
        assert isinstance(variables["recommended_soc_attributes"], str)
        assert "expected_solar_kwh" in variables["recommended_soc_attributes"]
        assert "morning_consumption_kwh" in variables["recommended_soc_attributes"]
        assert "calculation_timestamp" in variables["recommended_soc_attributes"]

    def test_optimal_morning_soc_variable_includes_clamping_logic(self, blueprint):
        """optimal_morning_soc variable includes clamping logic."""
        variables = blueprint["variables"]
        assert "optimal_morning_soc" in variables
        assert isinstance(variables["optimal_morning_soc"], str)
        assert "minimum_soc_floor" in variables["optimal_morning_soc"]
        assert "night_target_soc" in variables["optimal_morning_soc"]
        assert "clamped_target" in variables["optimal_morning_soc"]
