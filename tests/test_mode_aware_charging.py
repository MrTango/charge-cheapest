"""
Mode-Aware Charging Logic Tests

Tests for Task Group 3: Mode-Aware Charging Target Selection
Validates that night and day charging respect the forecast mode setting.
"""


class TestModeAwareChargingTargetSelection:
    def test_night_charging_target_soc_variable_is_mode_aware(self, blueprint):
        """night_charging_target_soc variable is mode-aware."""
        variables = blueprint["variables"]
        assert "night_charging_target_soc" in variables
        assert isinstance(variables["night_charging_target_soc"], str)
        assert "forecast_mode_automatic" in variables["night_charging_target_soc"]
        assert "user_soc_input_number" in variables["night_charging_target_soc"]
        assert "optimal_morning_soc" in variables["night_charging_target_soc"]

    def test_day_charging_target_soc_variable_is_defined_and_mode_aware(self, blueprint):
        """day_charging_target_soc variable is defined and mode-aware."""
        variables = blueprint["variables"]
        assert "day_charging_target_soc" in variables
        assert isinstance(variables["day_charging_target_soc"], str)
        assert "forecast_mode_automatic" in variables["day_charging_target_soc"]
        assert "user_soc_input_number" in variables["day_charging_target_soc"]

    def test_night_charging_target_source_variable_includes_mode_indicator(self, blueprint):
        """night_charging_target_source variable includes mode indicator."""
        variables = blueprint["variables"]
        assert "night_charging_target_source" in variables
        assert isinstance(variables["night_charging_target_source"], str)
        assert "solar_optimized_automatic" in variables["night_charging_target_source"]
        assert "solar_optimized_recommendation" in variables["night_charging_target_source"]
        assert "static" in variables["night_charging_target_source"]

    def test_solar_forecast_polling_branch_contains_input_number_set_value(self, blueprint_raw):
        """Solar forecast polling branch contains input_number.set_value service call."""
        raw_content = blueprint_raw
        assert "input_number.set_value" in raw_content
        assert "user_soc_input_number" in raw_content
        assert "optimal_morning_soc" in raw_content

    def test_night_charging_skip_notification_includes_mode_information(self, blueprint_raw):
        """Night charging skip notification includes mode information."""
        raw_content = blueprint_raw
        assert "night_charging_target_source" in raw_content
        assert "'automatic' if forecast_mode_automatic else 'recommendation'" in raw_content
