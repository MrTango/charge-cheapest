"""
Forecast Mode Integration Tests

Tests for Task Group 4: Integration and Edge Cases
Validates end-to-end workflows and mode switching behavior.
"""


class TestForecastModeIntegration:
    def test_calculated_charging_duration_uses_night_charging_target_soc(self, blueprint):
        """calculated_charging_duration uses night_charging_target_soc for mode awareness."""
        variables = blueprint["variables"]
        assert "calculated_charging_duration" in variables
        assert "night_charging_target_soc" in variables["calculated_charging_duration"]

    def test_day_calculated_charging_duration_uses_day_charging_target_soc(self, blueprint):
        """day_calculated_charging_duration uses day_charging_target_soc for mode awareness."""
        variables = blueprint["variables"]
        assert "day_calculated_charging_duration" in variables
        assert "day_charging_target_soc" in variables["day_calculated_charging_duration"]

    def test_solar_forecast_polling_pre_populates_input_number_only_in_recommendation_mode(self, blueprint_raw):
        """Solar forecast polling pre-populates input_number only in recommendation mode."""
        raw_content = blueprint_raw
        assert "not forecast_mode_automatic" in raw_content
        assert "input_number.set_value" in raw_content

    def test_both_night_and_day_charging_reference_mode_aware_target_variables(self, blueprint_raw):
        """Both night and day charging reference mode-aware target variables."""
        raw_content = blueprint_raw
        assert "night_charging_target_soc | round(1)" in raw_content
        assert "day_charging_target_soc | round(1)" in raw_content

    def test_fallback_behavior_preserved_when_solar_forecast_disabled(self, blueprint):
        """Fallback behavior preserved when solar forecast disabled."""
        variables = blueprint["variables"]
        assert "night_target_soc | float(60)" in variables["night_charging_target_soc"]
        assert "day_target_soc | float(50)" in variables["day_charging_target_soc"]
